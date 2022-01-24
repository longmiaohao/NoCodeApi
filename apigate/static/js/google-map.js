google.charts.load('current', {'packages':['geochart']});
google.charts.setOnLoadCallback(drawRegionsMap);

function drawRegionsMap() {

	var data = google.visualization.arrayToDataTable([
		['Country', 'Popularity'],
		['Germany', 200],
		['IN', 900],
		['United States', 300],
		['Brazil', 400],
		['Canada', 500],
		['France', 600],
		['RU', 700]
	]);

	var options = {
		width: 'auto',
		backgroundColor: 'transparent',
		colors: ["#D2A968", "#BF7A6A", "#A9BD7A", "#6FB4CE", "#ab7967", "#F782AA" ],
		datalessRegionColor: '#444D5D',
	};

	var chart = new google.visualization.GeoChart(document.getElementById('geo_chart'));

	chart.draw(data, options);
}
$(window).on('resize',function(){location.reload();});