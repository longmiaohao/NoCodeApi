// sparkline Graphs
$(function() {
	$("#sessions").sparkline([8,12,32,17,49,169,119,121,98,155,129,137,140,145,147,155,29,73,32,82,119,121,143,165,190 ], {
		type: 'line',
		lineColor: '#BF7A6A',
		fillColor: '#2A3039',
		lineWidth: 2,
		width: 90,
		height: 30,
		spotColor: '#A9BD7A',
		minSpotColor: '#6FB4CE',
		spotRadius: 4,
	});
});

$(function() {
	$("#users").sparkline([8,12,32,17,49,29,73,32,82,129,137,140,145,147,155,119,121,143,165,168,169,119,121,98,198 ], {
		type: 'line',
		lineColor: '#D2A968',
		fillColor: '#2A3039',
		lineWidth: 2,
		width: 90,
		height: 30,
		spotColor: '#A9BD7A',
		minSpotColor: '#6FB4CE',
		spotRadius: 4,
	});
});

$(function() {
	$("#duration").sparkline([8,12,29,37,54,33,85,66,82,119,121,143,165,168,169,119,121,98,155,129,137,140,145,147,185 ], {
		type: 'line',
		lineColor: '#A9BD7A',
		fillColor: '#2A3039',
		lineWidth: 2,
		width: 90,
		height: 30,
		spotColor: '#A9BD7A',
		minSpotColor: '#6FB4CE',
		spotRadius: 4,
	});
});

$(function() {
	$("#bouncerate").sparkline([9,43,32,28,32,32,27,49,125,137,140,145,147,155,82,119,121,143,105,118,129,119,161 ], {
		type: 'line',
		lineColor: '#6FB4CE',
		fillColor: '#2A3039',
		lineWidth: 2,
		width: 90,
		height: 30,
		spotColor: '#A9BD7A',
		minSpotColor: '#6FB4CE',
		spotRadius: 4,
	});
});

$(function() {
	$('#invoice').sparkline([2,2,3,4,5,6,7,11,10,6,12], {
		type: 'bar',
		barColor: '#475161',
		barWidth: 7,
		barSpacing: 2,
		height: 30,
	});
	$('#invoice').sparkline([1,1,2,2,3,3,4,7,5,5,3,4,3,7,8], {
		composite: true,
		fillColor: false,
		type: 'line',
		lineColor: '#FCB050',
		lineWidth: 2,
		height: 30,
		spotColor: '#A9BD7A',
		minSpotColor: '#6FB4CE',
		spotRadius: 0,
	});
});

$(function() {
	$("#moneySpend").sparkline([58,68,78,88,58], {
		type: 'bullet',
		height: '16',
		targetColor: '#6FB4CE',
		performanceColor: '#ffd0c5',
		rangeColors: ['#BF7A6A', '#CC8271','#FF9878'],
	});
});

$(function() {
	$("#lineGraph").sparkline([3,2,4,3,5,4,3,5,4,4,7,9,12,15,12,11,12,11], {
		type: 'line',
		width: '200',
		height: '70',
		lineColor: '#6fb4ce',
		fillColor: false,
		spotColor: '#BF7A6A',
		minSpotColor: '#BF7A6A',
		maxSpotColor: '#F782AA',
		lineWidth: 2,
		spotRadius: 5
	});
});

$(function() {
	$("#barGraph").sparkline([4,5,6,7,8,9,10,11,10,9,8,7,6,5,4], {
		type: 'bar',
		height: '70',
		barWidth: 7,
		barSpacing: 5,
		barColor: '#6fb4ce'
	});
});

$(function() {
	$("#barNegativeGraph").sparkline([2,-1,3,-5,4,7,-3,4,2,-3,4,-1,4], {
		type: 'bar',
		height: '70',
		barWidth: 7,
		barSpacing: 2,
		barColor: '#6fb4ce',
		negBarColor: '#d2a968'
	});
});

$(function(){
	$("#discreteGraph").sparkline([4,6,7,7,4,3,2,1,4,4], {
		type: 'discrete',
		width: '120',
		height: '70',
		lineColor: '#6FB4CE'
	});
});

$(function(){
	$("#bulletGraph").sparkline([10,12,12,9,7], {
		type: 'bullet',
		height: '20',
		width: '90',
		targetColor: '#EE3233',
		performanceColor: '#003A6F',
		rangeColors: ['#CEEBFB','#A3D6F5','#66A7C5']
	});
});

$(function(){
	$("#pieGraph").sparkline([1,1,2], {
		type: 'pie',
		width: '70',
		height: '70',
		sliceColors: ['#6FB4CE','#A9BD7A','#BF7A6A']
	});
});

$(function(){
	$("#boxGraph").sparkline([4,27,34,52,54,59,61,68,78,82,85,87,91,93,100], {
		type: 'box',
		width: '120 ',
		height: '60',
		boxLineColor: '#707c8e',
		boxFillColor: '#707c8e',
		whiskerColor: '#707c8e',
		outlierLineColor: '#707c8e',
		medianColor: '#6fb4ce',
		targetColor: '#a9bd7a'
	});
});

$(function(){
	$('#compositeBar').sparkline([4,5,6,7,8,9,10,11,10,9,8,7,6,5,4], {
		type: 'bar',
		barColor: '#A9BD7A',
		width: '120 ',
		height: '60',
		barSpacing: 5,
	});
	$('#compositeBar').sparkline([3,2,4,3,5,4,3,5,4,4,7,9,12,15,12], {
		composite: true,
		fillColor: false,
		lineColor: '#6FB4CE',
		width: '120 ',
		height: '60',
		lineWidth: 2,
		spotRadius: 5
	});
});

$(function(){
	$('#compositeLine').sparkline([4,1,5,7,9,9,8,7,6,6,4,7,8,4,3,2,2,5,6,7], {
		type: 'line',
		lineColor: '#6FB4CE',
		width: '120 ',
		height: '50',
		lineWidth: 1,
		spotRadius: 5,
		fillColor: false
	});
	$('#compositeLine').sparkline([8,4,0,0,0,0,1,4,4,10,10,10,10,0,0,0,4,6,5,9,10], {
		type: 'line',
		fillColor: false,
		composite: true,
		fillColor: false,
		lineColor: '#A9BD7A',
		width: '120 ',
		height: '50',
		lineWidth: 1,
		spotRadius: 3
	});
});



$(function(){
	$('#rowOne').sparkline([320,250,400,380,280,320,220,385,450], {
		type: 'line',
		lineWidth: 2,
		fillColor: false,
		lineColor: '#BF7A6A',
		spotColor: '#50B432',
		minSpotColor: '#f7b53c',
		maxSpotColor: '#F782AA',
		highlightSpotColor: '#',
		height: 20,
		width: 80,
		spotRadius: 3,
	});
});

$(function(){
	$('#rowTwo').sparkline([230,210,315,190,250,200,330,280,350], {
		type: 'line',
		lineWidth: 2,
		fillColor: false,
		lineColor: '#A9BD7A',
		spotColor: '#50B432',
		minSpotColor: '#f7b53c',
		maxSpotColor: '#F782AA',
		highlightSpotColor: '#',
		height: 20,
		width: 80,
		spotRadius: 3,
	});
});

$(function(){
	$('#rowThree').sparkline([280,320,220,385,450,320,250,400,280], {
		type: 'line',
		lineWidth: 2,
		fillColor: false,
		lineColor: '#6FB4CE',
		spotColor: '#50B432',
		minSpotColor: '#f7b53c',
		maxSpotColor: '#F782AA',
		highlightSpotColor: '#',
		height: 20,
		width: 80,
		spotRadius: 3,
	});
});
