/**
 * Created by pete on 8/05/2016.
 */

var animations = ["fadeIn",
    "fadeInDown",
    "fadeInDownBig",
    "fadeInLeft",
    "fadeInLeftBig",
    "fadeInRight",
    "fadeInRightBig",
    "fadeInUp",
    "fadeInUpBig",
    "flipInX",
    "flipInY",
    "rotateInDownLeft",
    "rotateInDownRight",
    "rotateInUpLeft",
    "rotateInUpRight",
    "rollIn",
    "zoomIn",
    "zoomInDown",
    "zoomInLeft",
    "zoomInRight",
    "zoomInUp",
    "slideInDown",
    "slideInLeft",
    "slideInRight",
    "slideInUp",
    "bounce",
    "flash",
    "pulse",
    "rubberBand",
    "shake",
    "headShake",
    "swing",
    "tada",
    "wobble",
    "jello"];

function alertModal(title, body)
{
    $("#confirmTask").modal('hide');
    $('#alert-modal-title').html(title);
    $('#alert-modal-body').html(body);
    $('#alert-modal').modal('show');
}

$(document).ready(function() {
    var boardId = $("#board_id").val();
    var orgId = $("#orgid").val();
    populateTasks(boardId);
    populateEmployees(orgId);
});

$("#emp-pin-confirm").click(function(){

    var pin = $("#emp-pin-emp-display-pin").text();
    var action = $("#task-action").val();
    var task = $("#task-id").val();
    var value = {"pin": pin, "action": action, "task": task};
    $.ajax({
        type : "POST",
        url : $("#mark-task-url").val(),
        data: JSON.stringify(value),
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
            $("#task" + task).detach().appendTo('#' + action);
            alertModal('Success', result.msg);
        },
        error: function(result){
            alertModal('Success', result.error);
        }
    });
});

$("#verify-pin").click(function()
{
    $("#emp-pin-emp-display").hide();
    $("#emp-pin-emp-display-name").hide();
    $("#emp-pin-emp-display-pin").hide();
    var value = {"pin": $("#emp-pin").val()};
    $.ajax({
        type : "POST",
        url : $("#get-employee-url").val(),
        data: JSON.stringify(value),
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
            if(result.employee != undefined)
            {
                console.log(result.employee);
                $("#emp-pin-form").fadeOut();
                $("#emp-pin-emp-display").css('background-color', result.employee.color);
                $("#emp-pin-emp-display-name").text(result.employee.fname + " " + result.employee.lname);
                $("#emp-pin-emp-display-pin").text(result.employee.pin);
                $("#emp-pin-emp-display").fadeIn();
                $("#emp-pin-emp-display-name").fadeIn();
                $("#emp-pin-emp-display-pin").fadeIn();
            }
            else
            {
                $("#emp-pin-form-error").text(result.error);
            }
        }
    });
});

function populateTasks(boardId)
{
    var value = {"board_id": boardId};
    $.ajax({
        type : "POST",
        url : $("#get-tasks-url").val(),
        data: JSON.stringify(value),
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
            var i;
            for (i = 0; i < result.tasks.length; ++i)
            {
                var task = result.tasks[i];
                var element = '<div id=\"task'+ task.id +'\" class=\"task animated '+ animations[Math.floor(Math.random() * animations.length)] +'\" data-id=\"'+ task.id +'\"> ';
                if(task.unassigned == true)
                {
                    element += '<div id=\"employee\" class=\"taskEmp\" style=\"background-color: ' +
                        ''+ task.color +'\" > <h3>U</h3> </div>';
                }
                else
                {
                    element += '<div id=\"employee\ '+ task+'" class=\"taskEmp\" style=\"background-color: ' +
                        ''+ task.color +'\" > <h3>'+ task.emp_abv +'</h3> </div>';
                }

                element += '<div class=\"taskContent\"><h6>'+ task.title +'</h6>' +
                    '<div><p><span id=\"comment00\">'+ task.comments.length +' ' +
                    '</span><span class=\"glyphicon glyphicon-comment\"></span>' +
                    '</p><span class=\"btn transparent glyphicon glyphicon-chevron-down showComment\"></span> ' +
                    '</div></div><div class=\"taskImportant\"></div><div id=\"commentsBlock0\">';
                if(task.comments.length > 0)
                {
                    for (var j = 0; j < task.comments.length; j++)
                    {
                        var comment = task.comments[i];
                        if(comment != undefined)
                        {
                            element += '<p>* '+ comment.text +'<p> ';
                        }
                    }
                }
                element += '</div></div>';
                if(task.unassigned == true)
                {
                    $("#newTasks").append(element);
                    var count = parseInt($("#newTasksNumber").text());
                    $("#newTasksNumber").text(count + 1);
                }
                else if(task.todo == true)
                {
                    $("#todo").append(element);
                    var count = parseInt($("#todoTasksNumber").text());
                    $("#todoTasksNumber").text(count + 1);
                }
                else
                {
                    $("#done").append(element);
                    var count = parseInt($("#doneTasksNumber").text());
                    $("#doneTasksNumber").text(count + 1);
                }

                $("#newTasks, #todo, #done").sortable({ connectWith: ".dnd-container",
                    placeholder: "ui-sortable-placeholder",
                    start: function(event, ui) {
                    },
                    stop: function(event, ui) {
                    },
                    receive: function(event, ui)
                    {
                        ui.sender.sortable("cancel");
                        var source = ui.sender.attr('id');
                        var destination = $(this).attr('id');
                        var taskId = ui.item.attr("data-id");
                        if(source == "newTasks" && (destination == "todo" || destination == "done" ))
                        {
                            $("#task-action").val(destination);
                            $("#task-id").val(taskId);
                            $("#confirmTask").modal('show');
                        }
                        if(destination == "newTasks")
                        {
                            alertModal("Error", "You can't move a task to the unassigned pile")
                        }
                    }
                }).disableSelection();


            }
        }
    });
}

function populateComments(taskId)
{
    var value = {"task_id": taskId};
    $.ajax({
        type : "POST",
        url : $("#get-comments-url").val(),
        data: JSON.stringify(value),
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
            var i;
            for (i = 0; i < result.comments.length; ++i) {
                var element = '<p id="comment' + i + '">' + result.comments[i]['text'] +
                    '<span class="glyphicon glyphicon-remove remove"></span></p>';
                $("#comments-" + taskId).append(element);
                $("#empsNumber").html(parseInt(this.val()) + 1);
            }
        }
    });
}


function populateEmployees(org) {
    var value = {"org_id": org};
    $.ajax({
        type: "POST",
        url: $("#get-employees-url").val(),
        data: JSON.stringify(value),
        contentType: 'application/json;charset=UTF-8',
        success: function (result) {
            for (var i = 0; i < result.employees.length; ++i) {
                var emp = result.employees[i];
                var element = '<div id="employee_2" style=\"background-color:' + emp.color + ' \" class="employee animated '+ animations[Math.floor(Math.random() * animations.length)] +'" ondrag="dragg()"> <p>'+ emp.fname + " " + emp.lname +'</p></div>';
                $("#employees").append(element);
                $("#empsNumber").html(parseInt($("#empsNumber").text()) + 1);
            }
        }
    });
}


