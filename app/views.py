import json

from flask.ext.login import login_required, current_user, login_user, logout_user
from playhouse.migrate import SqliteMigrator, migrate

import dbutils

from app import app, db
from flask import render_template, request, jsonify, Response, url_for, redirect
from peewee import fn, DoesNotExist, TextField, BooleanField, ForeignKeyField

from dbmodels import TaskBoard, Comment, TaskComment, BoardTask, Task, EmployeePin, User, Organization

import wwwmodels as viewmodels

import utils


@app.before_first_request
def prepare():
    # dbutils.verify_tables(drop_tables=True, generate_data=True)
    # m = SqliteMigrator(db.database)
    # migrate(m.add_column('task', 'hidden', BooleanField(default=False)))
    # migrate(m.add_column('user', 'organization_id', ForeignKeyField(Organization, null=True, to_field=Organization.id)))
    # for u in User.select():
    #   org = (Organization.select().order_by(fn.Random())).get()
    #  u.organization = org
    # u.save()
    print ('a')


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('pages/login.html')
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        try:
            user = User.get(User.email == email)
        except DoesNotExist:
            return jsonify(error='Invalid Credentials')
        if user.password == password:
            login_user(user)
            return jsonify(id=user.id, name=user.name, url=url_for('company', cid=user.organization.id))
        else:
            return jsonify(error='Invalid Credentials')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('pages/signup.html')
    if request.method == 'POST':
        cm = request.json['company']
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        query = User.select().where(User.email == email)
        if query.exists():
            return jsonify(error='Email already in use')
        query = Organization.select().where(Organization.name == cm)
        if query.exists():
            return jsonify(error='A warehouse already exists with the specified name')

        manager = User()
        manager.email = email
        manager.name = name
        manager.password = password
        manager.save()

        c = Organization()
        c.name = cm
        c.save()

        manager = User.get(User.email == email)
        c = Organization.get(Organization.name == cm)

        manager.organization = c
        manager.save()

        return jsonify(msg='You have successfully signed up', url=url_for('company', cid=c.id))

    return jsonify(error='Invalid Credentials')


@app.route('/showboard/<int:board_id>', methods=['GET'])
@login_required
def show_board(board_id=None):
    if board_id is None:
        return show_error('400', 'No board id specified')
    try:
        board = TaskBoard.get(TaskBoard.id == board_id)
        return render_template('pages/board.html', id=board_id, orgid=board.org_id,
                               orgname=board.org_name, accountname=current_user.name, managerid=current_user.id,
                               boardname=board.name)
    except DoesNotExist as e:
        return show_error('404', e.message)


@app.route('/report/<int:board_id>', methods=['GET'])
def report(board_id):
    if board_id is None:
        return show_error('400', 'No board id specified')
    try:
        board = TaskBoard.get(TaskBoard.id == board_id)
        t = Task.select().join(BoardTask).join(TaskBoard).where(TaskBoard.id == board_id, Task.marked_as_task).count()
        td = Task.select().join(BoardTask).join(TaskBoard).where(TaskBoard.id == board_id, Task.marked_as_todo).count()
        d = Task.select().join(BoardTask).join(TaskBoard).where(TaskBoard.id == board_id,
                                                                Task.marked_as_completed).count()
        return render_template('pages/report.html', total=t + td + d, t=t, td=td, d=d)
    except DoesNotExist as e:
        return show_error('404', e.message)


@app.route('/gettasks', methods=['POST'])
def get_tasks():
    board_id = int(request.json['board_id'])
    board = TaskBoard.get(TaskBoard.id == board_id)
    query = tuple(Task.select().join(BoardTask).join(TaskBoard).where(TaskBoard.id == board_id))
    tasks = list()
    for item in query:
        if not item.hidden:
            tasks.append(viewmodels.Task.create_from_dbmodel(item, dbutils.get_comments(item.id)).to_dict())
    return jsonify(tasks=tasks)


@app.route('/hidetask', methods=['POST'])
def hide_task():
    task = request.json['task_id']
    try:
        task = Task.get(Task.id == task)
        return jsonify(msg='All good')
    except DoesNotExist as e:
        return jsonify(error='An error occurred ' + e.message)


@app.route('/addcomment', methods=['POST'])
def add_comment():
    task = request.json['task_id']
    text = request.json['text']
    author_type = request.json['author_type']
    author_id = request.json['author_id']
    try:
        task = Task.get(Task.id == task)
        c = Comment()
        c.text = text
        if author_type == 'manager':
            a = User.get(User.id == author_id)
            c.created_by_manager = a
        else:
            a = EmployeePin.get(EmployeePin.pin == author_id)
            c.created_by_employee = a
        c.save()
        tc = TaskComment()
        tc.comment = c
        tc.task = task
        tc.save()
        return jsonify(msg='Created a new comment')
    except DoesNotExist as e:
        return jsonify(error='An error occurred ' + e.message)


@app.route('/getemployee', methods=['POST'])
def get_employee():
    if request.json['pin'] is None:
        return jsonify(error='Invalid Pin')
    pin = request.json['pin']
    try:
        emp = EmployeePin.get(EmployeePin.pin == pin)
        emp = {"id": emp.id, "color": emp.hex_color, "logo": emp.logo_url, "pin": emp.pin,
               "fname": emp.first_name, "lname": emp.last_name}
        return jsonify(employee=emp)
    except DoesNotExist:
        return jsonify(error='Invalid Pin')


@app.route('/marktask', methods=['POST'])
def mark_task():
    action = request.json['action']
    emp = request.json['pin']
    task = request.json['task']

    try:
        task = Task.get(Task.id == task)
    except DoesNotExist:
        return jsonify(error='Invalid Task Id')
    try:
        emp = EmployeePin.get(EmployeePin.pin == emp)
    except DoesNotExist:
        return jsonify(error='Invalid PIN')
    task.marked_by = emp
    if action == 'todo':
        task.marked_as_task = False
        task.marked_as_completed = False
        task.marked_as_todo = True
    if action == 'done':
        task.marked_as_task = False
        task.marked_as_completed = True
        task.marked_as_todo = False
    task.save()
    msg = ' '.join(('Task was marked as', action, 'by employee with PIN', emp.pin))
    return jsonify(msg=msg)


@app.route('/getemployees', methods=['POST'])
def get_employees():
    ordid = int(request.json['org_id'])
    employees = list()
    try:
        org = Organization.get(Organization.id == ordid)
        for emp in EmployeePin.select().where(EmployeePin.organization == org):
            employees.append({"id": emp.id, "color": emp.hex_color, "logo": emp.logo_url, "pin": emp.pin,
                              "fname": emp.first_name, "lname": emp.last_name})
        # return Response(response=jsonify(employees=employees), status=200, mimetype="application/json")
        return jsonify(employees=employees)
    except DoesNotExist as e:
        return jsonify(error="Invalid Parameters" + e.message)


@app.route('/companies')
def companies():
    return render_template('companies.html', items=tuple(Organization.select()))


@app.route('/company/<int:cid>')
@login_required
def company(cid=None):
    print(current_user.email)
    if cid is None:
        return show_error('404', 'Page not found')
    else:
        try:
            org = Organization.get(Organization.id == cid)
            return render_template('pages/boards.html', id=org.id, name=current_user.name, mid=current_user.id)
        except DoesNotExist:
            return show_error('404', 'Page not found')


@app.route('/createboard', methods=['POST'])
def create_board():
    orgid = int(request.json['org_id'])
    title = request.json['title']
    desc = request.json['desc']
    manager = int(request.json['manager'])

    try:
        manager = User.get(User.id == manager)
        org = Organization.get(Organization.id == orgid)
    except DoesNotExist:
        return jsonify(error='Invalid Manager Id')

    board = TaskBoard()
    board.creator = manager
    board.name = title
    board.description = desc
    board.organization = org
    try:
        board.save()
        b = {'id': board.id, 'name': board.name, 'desc': board.description, 'count': 0}
        return jsonify(board=b)
    except Exception as e:
        return jsonify(error=e.message)


@app.route('/getboards', methods=['POST'])
def get_boards():
    orgid = int(request.json['org_id'])
    try:
        org = Organization.get(Organization.id == orgid)
        boards = tuple(TaskBoard.select().where(TaskBoard.organization == org))
    except DoesNotExist:
        return jsonify(error="Invalid Board Id")
    data = list()
    for b in boards:
        count = 0
        for a in BoardTask.select():
            if a.board_id == b.id:
                count += 1
        data.append({'id': b.id, 'name': b.name, 'desc': b.description, 'count': count})
    return jsonify(boards=data)


@app.route('/submitcreatetask', methods=['POST'])
def submit_create_task():
    a = request.json
    try:
        board_id = int(request.json['board_id'])
        task_title = request.json['task_title']
        task_desc = request.json['task_desc']
        if request.json['employee_id'] != 'none':
            employee_id = request.json['employee_id']
        manager_id = int(request.json['manager_id'])
        urgent = utils.to_bool(request.json['urgent'])
    except ValueError as ve:
        return jsonify(error="Invalid Parameters", details=ve.message)
    if board_id is None or task_title is None or task_desc is None or manager_id is None:
        return jsonify(error="Invalid Parameters")
    try:
        assign_to_employee = False
        board = TaskBoard.get(TaskBoard.id == board_id)
        if request.json['employee_id'] != 'none':
            assign_to_employee = True
            employee = EmployeePin.get(EmployeePin.pin == employee_id)
        manager = User.get(User.id == manager_id)
        task = Task()
        task.title = task_title
        task.description = task_desc
        task.marked_as_high_priority = urgent
        if assign_to_employee:
            task.marked_by = employee
        task.save()
        bt = BoardTask()
        bt.task = task
        bt.board = board
        bt.save()
        return jsonify(msg="All Good", url=url_for('show_board', board_id=board_id))
    except DoesNotExist:
        return jsonify(error="Invalid Parameters")


@app.route('/getcomments', methods=['POST'])
def get_comments():
    datac = list()
    taskid = int(request.json['task_id'])
    print taskid
    try:
        try:
            taskid = int(taskid)
        except ValueError:
            raise DoesNotExist('Task Id Needs to be numeric')
        if taskid is None:
            raise DoesNotExist('Task Id Needs to be specified')
        # for tc in TaskComment.select():
        #    if tc.taskid == taskid:
        #        datac.append(tc.comment)

        for c in Comment.select().join(TaskComment).where(TaskComment.task == taskid):
            author = c.get_author()
            datac.append({'author': c.get_author(), 'text': c.text})
        # comments = (Comment.select().join(TaskComment).where(TaskComment.task == taskid))

        return jsonify(comments=datac)
    except DoesNotExist as e:
        return jsonify(error='Invalid Task Id ' + e.message)


def show_error(code=None, msg=None):
    return render_template('error.html', code=code, msg=msg)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('signin'))
