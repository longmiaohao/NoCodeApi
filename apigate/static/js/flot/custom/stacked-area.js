var $border_color = "#ccc";
var $grid_color = "#ccc";
var $default_black = "#666";

$(function () {
		
	var d1, d2, d3, data, chartOptions;

	var d1 = [[1262304000000, 6], [1264982400000, 3057], [1267401600000, 3434], [1270080000000, 12982], [1272672000000, 21602], [1275350400000, 27826], [1277942400000, 24302], [1280620800000, 24237], [1283299200000, 21004], [1285891200000, 12144], [1288569600000, 10577], [1291161600000, 7295]];
	var d2 = [[1262304000000, 5], [1264982400000, 200], [1267401600000, 1605], [1270080000000, 1129], [1272672000000, 11643], [1275350400000, 19055], [1277942400000, 30062], [1280620800000, 39197], [1283299200000, 37000], [1285891200000, 27000], [1288569600000, 21000], [1291161600000, 12000]];
	var d3 = [[1262304000000, 10000], [1264982400000, 9010], [1267401600000, 21205], [1270080000000, 31129], [1272672000000, 32643], [1275350400000, 56055], [1277942400000, 32062], [1280620800000, 25197], [1283299200000, 17000], [1285891200000, 26000], [1288569600000, 15300], [1291161600000, 1000]];

	data = [{ 
		label: "Likes", 
		data: d1
	}, {
		label: "Tweets",
		data: d2
	}, {
		label: "Shares",
		data: d3
	}];
 
	chartOptions = {
		xaxis: {
			min: (new Date(2009, 11)).getTime(),
			max: (new Date(2010, 11)).getTime(),
			mode: "time",
			tickSize: [1, "month"],
			monthNames: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
			tickLength: 0
		},
		yaxis: {

		},
		series: {
			stack: true,
			lines: {
				show: true, 
				fill: 0.1,
				lineWidth: 2
			},
			points: {
				show: true,
				radius: 4,
				fill: true,
				fillColor: "#2a3039",
				lineWidth: 2
			}
		},
		grid:{
      hoverable: true,
      clickable: false,
      borderWidth: 1,
      tickColor: '#353c48',
      borderColor: '#353c48',
    },
		legend: {
			show: true,
			position: 'nw'
		},
		shadowSize: 0,
		tooltip: true,
		tooltipOpts: {
		content: '%s: %y'
		},
		colors: ['#CC93C4', '#79CEBC', '#FEBBA4', '#BED3E4', '#FFE0D4'],
	};

	var holder = $('#stacked-area-chart');

	if (holder.length) {
		$.plot(holder, data, chartOptions );
	}
});