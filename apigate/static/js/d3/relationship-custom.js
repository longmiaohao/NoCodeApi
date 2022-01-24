var json1 = [
		{
			"value": "$2,500",
			"parent": "UI Design"
		}, {
			"value": "$4,600",
			"parent": "UI Design"
		}, {
			"value": "$2,600",
			"parent": "UI Design"
		}, {
			"value": "$1,900",
			"parent": "Frontend Development"
		}, {
			"value": "$5,400",
			"parent": "Frontend Development"
		}, {
			"value": "$3,750",
			"parent": "Frontend Development"
		}, {
			"value": "$3,500",
			"parent": "Frontend Development"
		}, {
			"value": "$1,800",
			"parent": "Frontend Development"
		}, {
			"value": "$5, 600",
			"parent": "UX Design"
		}, {
			"value": "$3,250",
			"parent": "UX Design"
		}, {
			"value": "$2,500",
			"parent": "UX Design"
		},{
			"value": "$3,250",
			"parent": "UX Design"
		}];


	var graph = d3.select('#relationshipGraph').relationshipGraph({
		'showTooltips': true,
		'maxChildCount': 10,
		'showKeys': false,
		'thresholds': [1000, 2000, 4000]
	});

	graph.data(json1);

	var interval = null;

	function data1() {
		if (interval != null) {
			clearInterval(interval);
		}
		graph.data(json1);
		document.querySelector('h1').innerHTML = 'Highest Grossing Films by Studio';
	}