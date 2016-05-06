/**
 * Customising jquery functions
 */
var boardCount = 0;
var employeeCount = 0;
$(function() {

	makeEmpsDraggable();

	// add a new board
	$("#addBoard").click(function(){
		var newBoard = 
				'<div class="col-sm-3" id="board'+ boardCount + 
				'"><div class="board board-new"><div><h4 class="heading">New Board</h4>' +
              	'<button class="btn transparent delete remove">X</button></div><br/>' + 
            	'<form><fieldset class="form-group"><input type="text" class="form-control input"' +
            	' id="boardTitle" placeholder="Board Title"> </fieldset><fieldset class="form-group">' +
                '<textarea class="form-control input" id="boardDesc" placeholder="Description" rows="2"></textarea>' +
              	'</fieldset><p>Employees:  </p><div id="empsInvolved' + boardCount + '" class="emps"></div><div class="text-center">' +
                '<button class="btn brd save">Save</button></form></div></div>';
		$("#boards").append(newBoard);
		boardCount ++;
		$("#boardsNumber").text(boardCount);

		// make employees droppable at the board
	    makeEmpsDraggable();
	});

	// add new employee
	$("#addEmployee").click(function(){

		// generate random PIN number
		var randomPIN = Math.floor( Math.random() * ( 99999 - 10000 + 1)  + 10000);
		var newEmployee =
					'<div id="employee' + employeeCount + '" class="employee employee-new">' +
            		'<div class="heading"><p>New Employee</p><button class="btn transparent delete remove">X</button>' +
            		'</div><form><fieldset class="form-group"><input type="text" class="form-control input" id="firstName' + 
            		employeeCount + '"' +' placeholder="First Name" autocomplete="off"><input type="text" class="form-control input" id="lastName' + 
            		employeeCount + '" placeholder="Last Name" autocomplete="off">' +
               		'<input type="text" class="form-control input" id="phone' + employeeCount + 
               		'" placeholder="Phone Number" autocomplete="off"></fieldset>' +
              		'<div class="text-center"><p>PIN</p><span>: E' + randomPIN + '</span></div><div class="text-center">' +
                	'<button class="btn brd save">Save</button></div></form></div>';
		$("#employees").append(newEmployee);
		employeeCount ++;
		$("#empsNumber").text(employeeCount);

		// make employee draggable to board
	    makeEmpsDraggable();
	}); 

})

// remove board or employee
.on('click', '.remove', function() {

	// checks if event source is from board or employee
	if ($(this).parent().parent().attr('class') == 'board board-new'){
		$(this).parentsUntil("#boards").remove(); 
		boardCount--;
		$("#boardsNumber").text(boardCount);
	}
	else {
		$(this).parentsUntil("#employees").remove(); 
		employeeCount--;
		$("#empsNumber").text(employeeCount);
	}
})

// save board or employee
.on('click', '.save', function(){

	// checks if event source is from board or employee
	if ($(this).parent().parent().parent().attr('class') == 'board board-new'){ 
		var board =
	        '<div class="board" ondblclick="goToBoard()"><div><h2 class="text-center">' + $(this).parents('form').find('[id^="boardTitle"]').val() + '</h2>' +
	        '<button class="btn transparent menu glyphicon glyphicon-align-justify"></button>' +
	        '</div><br/><div class="text-center"><h2>' + $(this).parents('form').find('[id^="empsInvolved"]').children().length + 
	        ' <span class="glyphicon glyphicon-user"></span></h2><h2>0 <span class="glyphicon glyphicon-tasks"></span></h2>' +
	        '</div><hr/><div><p class="description">' + $(this).parents('form').find('[id^="boardDesc"]').val() + '</p>' +
	        '</div></div>';

	    // save board before delete
	    var rootBoard =  $(this).parents('div.col-sm-3');
	    $(rootBoard).empty();
	    $(rootBoard).append(board);
	}
	else {
		var employee =
			'<p><span>' + $(this).parents('form').find('[id^="firstName"]').val() + '</span> <span>' + 
			$(this).parents('form').find('[id^="lastName"]').val() + '</p>';
		var rootEmployee =  $(this).parents('div.employee');
	    $(rootEmployee).empty();
	    $(rootEmployee).append(employee).removeClass('employee-new');
	}
})

// edit board
.on('click', '.menu', function(){

	var rootBoard =  $(this).parents('div.col-sm-3');
	var boardId = $(rootBoard).attr('id').substr(-1);

	var editBoard =
		'<div class="board board-new"><div><h4 class="heading">Edit Board</h4>' +
      	'<button class="btn transparent delete cancel">X</button></div><br/>' + 
    	'<form><fieldset class="form-group"><input type="text" class="form-control input"' +
    	' id="boardTitle' + boardId + '" placeholder="Board Title" value="' + 
    	$(rootBoard).find('h2.text-center').text() + 
    	'"></fieldset><fieldset class="form-group">' +
        '<textarea class="form-control input" id="boardDesc' + boardId + '" placeholder="Description" rows="2">' + 
        $(rootBoard).find('p.description').text() + '</textarea>' +
      	'</fieldset><p>Employees:  </p><div id="empsInvolved' + boardId + 
      	'" class="emps"></div><div class="text-center"><button class="btn brd remove">Delete</button> ' +
        '<button class="btn brd save">Save</button></form></div></div>';

    $(rootBoard).children().hide();
    $(rootBoard).append(editBoard);
})

// edit employee
.on('dblclick', '.employee', function(){
    // alert("The paragraph was double-clicked");s

    var rootEmployee =  $(this).closest('div.employee');
    // check that employee div is not the new dive or edit div
    if (!$(rootEmployee).hasClass('employee-new')) {
	    var employeeId = $(rootEmployee).attr('id').substr(-1);

	    var editEmployee = 
			'<div class="heading"><p>Edit Employee</p><button class="btn transparent delete cancel">X</button>' +
			'</div><form><fieldset class="form-group"><input type="text" class="form-control input" id="firstName' + 
			employeeId + '" placeholder="First Name" value="' + $(rootEmployee).find('span:first-child').text() + 
			'" autocomplete="off"><input type="text" class="form-control input" id="lastName' + 
			employeeId + '" placeholder="Last Name" value="' + $(rootEmployee).find('span:last-child').text() + 
			'" autocomplete="off"><input type="text" class="form-control input" id="phone' + 
			employeeId + '" placeholder="Phone Number" autocomplete="off"></fieldset>' +
	  		'<div class="text-center"><p>PIN</p><span>: AP1023</span></div><div class="text-center">' +
	        '<button class="btn brd remove">Delete</button><button class="btn brd save">Save</button></div></form></div>';	

	    $(rootEmployee).children().hide();
	    $(rootEmployee).append(editEmployee).addClass('employee-new');	
	}
})


// cancel editting boards or employees
.on('click', '.cancel', function(){

	if ($(this).parent().parent().attr('class') == 'board board-new'){
	    var rootBoard =  $(this).parents('div.col-sm-3');
	     $(rootBoard).find('div:first-child').show();
	     $(rootBoard).find('div.board-new').remove();
	 }
	 else {
	 	var rootEmployee =  $(this).closest('div.employee');
	     $(rootEmployee).removeClass('employee-new').find('p').show();
	     $(rootEmployee).find('div').remove();
	     $(rootEmployee).find('form').remove();
	 }
})
// focus on text field
.on('click', '.input', function(){
	$(this).focus();
});

/**
 * Function to redirect to board page when board double clicked
 */
function goToBoard(){
		window.location.href = "board.html";
}

/**
 * Function to make employees draggable to boards
 */
function makeEmpsDraggable() {
	$( '#employees, [id^="empsInvolved"]' ).sortable({ connectWith: ".emps"}).disableSelection(); 
}

