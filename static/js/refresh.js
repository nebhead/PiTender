
$(document).ready( function(){
$('#refreshdata').load('/data');
refresh();
});

function refresh()
{
	setTimeout( function() {
	  $('#refreshdata').load('/data');
	  refresh();
	}, 1000);
}
