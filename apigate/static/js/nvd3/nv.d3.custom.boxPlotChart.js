// NVD3 Accounts Graph
nv.addGraph(function() {
	var chart = nv.models.boxPlotChart()
	.x(function(d) { return d.label })
	// .y(function(d) { return d.values.Q3 })
	.color(['#BF7A6A', '#A9BD7A', '#6FB4CE'])
	chart.margin({"left":40,"right":0,"top":10,"bottom":40})
	.staggerLabels(true)
	.maxBoxWidth(75) // prevent boxes from being incredibly wide 
	.yDomain([0, 500]);
	d3.select('#bankAccounts svg')
	.datum(exampleData())
	.call(chart);
	nv.utils.windowResize(chart.update);
	return chart;
});

function exampleData(){
	return [{
		label: "HSBC",
		values: { 
			Q1: 120,
			Q2: 150,
			Q3: 200,
			whisker_low: 115,
			whisker_high: 210,
			outliers: [50, 100, 225]
		},
	},{
		label: "Axis",
		values: {
			Q1: 200,
			Q2: 250,
			Q3: 400,
			whisker_low: 225,
			whisker_high: 425,
			outliers: [175]          
		},
	},{
		label: "CITY",
		values: { 
			Q1: 50,
			Q2: 100,
			Q3: 125,
			whisker_low: 25,
			whisker_high: 175,
			outliers: [0]
		},
	}
];}