// Basic DataTable
$(function(){
	$('#basicExample').DataTable({
		'iDisplayLength': 5,
	});
});

// Autofill DataTable
$(function(){
	$('#autoFill').DataTable({
		autoFill: true,
		'iDisplayLength': 5,
	});
});

// Fixed Header DataTable
$(function(){
	var table = $('#fixedHeader').DataTable( {
		fixedHeader: true,
		'iDisplayLength': 5,
	});
});

// Responsive Table
$(function(){
	$('#responsiveTable').DataTable({
		responsive: true,
		'iDisplayLength': 5,
	});
});

$(function(){
  $('#scrollTable').DataTable({
    "scrollY": "200px",
    "scrollCollapse": true,
    "paging": false,
    'iDisplayLength': 5,
  });
});