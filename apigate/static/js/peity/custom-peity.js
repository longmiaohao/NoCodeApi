// Pie Chart
$(function(){
	$(".pie").peity("pie");
});

// Donut Chart
$(function(){
	$('.donut').peity('donut');
});

// Updating Chart
$(function(){
	var updatingChart = $(".updating-chart").peity("line", {
		width: 150,
		height: 50,
		stroke: "#D2A968",
		fill: false,
	})
	setInterval(function() {
		var random = Math.round(Math.random() * 5)
		var values = updatingChart.text().split(",")
		values.shift()
		values.push(random)
		updatingChart
		.text(values.join(","))
		.change()
	}, 500);
})

// Gradient Bar Chart
$(function(){
	$(".gradientBar").peity("bar", {
		width: 110,
		height: 50,
		fill: function(_, i, all) {
			var g = parseInt((i / all.length) * 255)
			return "rgb(190, " + g + ", 100)"
		}
	})
});

