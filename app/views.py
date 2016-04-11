import csv

import datetime
import os

from app import app, db
from flask import render_template, request, jsonify, Response
from peewee import fn, DoesNotExist

from config import BASEDIR
from dbmodels import Role, User, UserRoles, EmployeePin, Task, TaskCompletion, MarkedAsTodo, TaskBoard, BoardTask, \
    EmployeeShift, Shift


@app.before_first_request
def prepare():
    populate_dummy_data()


@app.route('/', methods=['GET'])
def index():
    print 'lol'
    tasks = Task.select().order_by(fn.Random())
    return render_template('tasknew.html', normaltasks=tasks, doingtasks=(), donetasks=())

@app.route('/marktask', methods=['POST'])
def updatetask():
    pin=request.form['pin']

    try:
        brd = int(request.form['board'])
    except ValueError:
        data = jsonify(error='Invalid Board Id')
        return Response(response=data, status=200, mimetype="application/json")

    try:
        tsk = int(request.form['task'])
    except ValueError:
        data = jsonify(error='Invalid Task Id')
        return Response(response=data, status=200, mimetype="application/json")

    try:
        task = Task.select(Task.id == brd)
    except DoesNotExist:
        data = jsonify(error='Invalid Task Id')
        return Response(response=data, status=200, mimetype="application/json")

    try:
        board = TaskBoard.select(TaskBoard.id == brd)
    except DoesNotExist:
        data = jsonify(error='Invalid Board Id')
        return Response(response=data, status=200, mimetype="application/json")

    try:
        employee = EmployeePin.select(EmployeePin.pin == pin)
    except DoesNotExist:
        data = jsonify(error='Invalid Employee Pin')
        return Response(response=data, status=200, mimetype="application/json")

    try:
        shift = Shift.select(Shift.day.day == datetime.date.today())
    except DoesNotExist:
        data = jsonify(error='No shift today')
        return Response(response=data, status=200, mimetype="application/json")

    taskaction = request.form['action']
    if taskaction == 'markastodo':
        try:
            mm = MarkedAsTodo.select(MarkedAsTodo.task == task)
            data = jsonify(error='Task is already masked as ToDo')
            return Response(response=data, status=200, mimetype="application/json")
        except DoesNotExist:
            mmm = MarkedAsTodo()
            mmm.task = task
            mmm.employee = employee
            mmm.save()
            data = jsonify(markedastodo=mmm.get_id)
            return Response(response=data, status=200, mimetype="application/json")

    elif taskaction == 'markasdone':
        print('a')
            # TODO: Handle marked as done



@app.route('/board/<string:boardname>', methods=['GET'])
def show_board(boardname):
    board = TaskBoard.get(TaskBoard.name == boardname)
    if board is None:
        return render_template('error.html'), 404
    tasks = BoardTask.select(BoardTask.board == board)
    return render_template('board.html', thetasks=tasks, theboard=board)

def populate_dummy_data():
    Role.drop_table(True)
    User.drop_table(True)
    UserRoles.drop_table(True)
    EmployeeShift.drop_table(True)
    Task.drop_table(True)
    TaskCompletion.drop_table(True)
    MarkedAsTodo.drop_table(True)
    TaskBoard.drop_table(True)
    BoardTask.drop_table(True)
    Shift.drop_table(True)
    EmployeePin.drop_table(True)
    db.database.create_tables([Role, User, UserRoles, EmployeePin, Task, TaskCompletion, MarkedAsTodo, TaskBoard,
                               BoardTask, EmployeeShift, Shift], True)
    with open(os.path.join(BASEDIR, 'dummypins.csv')) as g:
        for pin in g.readlines():
            entry = EmployeePin()
            entry.pin = str(pin.rstrip())
            entry.save()

    reader = csv.reader(open(os.path.join(BASEDIR, 'dummymanagerdata.csv'), mode='r'))
    manager_role = Role()
    manager_role.name = "Warehouse Manager"
    manager_role.description = "Manager of this warehouse"
    manager_role.save()
    for line in reader:
        manager = User()
        manager.email = line[0].rstrip()
        manager.password = line[1].rstrip()
        manager.confirmed_at = datetime.datetime.now()
        manager.name = line[2].rstrip()
        manager.save()
        their_role = UserRoles()
        their_role.user = manager
        their_role.role = manager_role
        their_role.save()
        taskboard = TaskBoard()
        taskboard.creator = manager
        taskboard.name = ''.join((manager.name, '\'s board'))
        taskboard.created_at = datetime.datetime.now()
        taskboard.save()
        reader2 = csv.reader(open(os.path.join(BASEDIR, 'dummytasks.csv'), mode='r'))
        for line2 in reader2:
            task = Task()
            task.title = line[0].rstrip()
            task.description = line[1].rstrip()
            task.save()
            bt = BoardTask()
            bt.board = taskboard
            bt.task = task
            bt.save()



