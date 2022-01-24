var $border_color = "#ccc";
var $grid_color = "#ccc";
var $default_black = "#666";

$(function () {
		
		var d1, d2, data, chartOptions;

		var d1 = [[1262304000000, 5], [1264982400000, 200], [1267401600000, 1605], [1270080000000, 6129], [1272672000000, 11643], [1275350400000, 19055], [1277942400000, 30062], [1280620800000, 39197], [1283299200000, 37000], [1285891200000, 27000], [1288569600000, 21000], [1291161600000, 17000]];
		var d2 = [[1262304000000, 2], [1264982400000, 120], [1267401600000, 1205], [1270080000000, 4129], [1272672000000, 6643], [1275350400000, 9055], [1277942400000, 15062], [1280620800000, 19197], [1283299200000, 20000], [1285891200000, 12000], [1288569600000, 7300], [1291161600000, 1000]];

		data = [{ 
			label: "Facebook", 
			data: d1
		}, {
			label: "Google Plus",
			data: d2
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
					lines: {
						show: true, 
						fill: false,
						lineWidth: 2,
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
	        clickable: true,
	        borderWidth: 1,
					tickColor: '#353c48',
					borderColor: '#353c48',
	      },
	      shadowSize: 0,
				legend: {
					show: true,
					position: 'nw'
				},
				
				tooltip: true,
				tooltipOpts: {
					content: '%s: %y'
				},
				colors: ['#827CB6', '#FD9EB4', '#9F99C5', '#FEC5C1', '#FFE0D4'],
		};

		var holder = $('#line-chart');

		if (holder.length) {
			$.plot(holder, data, chartOptions );
		}


});