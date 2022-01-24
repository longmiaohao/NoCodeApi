$(function(){ 
	$("[id$='circle']").percircle();
	
	$("#clock").percircle({
		perclock: true
	});
	
	$("#custom").percircle({
		text:"custom",
		percent: 27
	});
});