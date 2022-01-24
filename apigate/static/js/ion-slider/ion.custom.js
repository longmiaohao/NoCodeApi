// ION Range
$(function () {
	$("#range").ionRangeSlider({
		hide_min_max: true,
		keyboard: true,
		min: 10,
		max: 500,
		from: 50,
		to: 440,
		type: 'double',
		step: 1,
		prefix: "$",
		grid: true
	});
});