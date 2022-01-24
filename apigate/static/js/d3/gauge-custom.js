var chartRevenue = charts.gauge({
		container: '#chartRevenue',
		value: 0,
		size: 130,
		label: 'Revenue',
		minorTicks: 5,
		majorTicks: 5,
		zones: {
		red: { from: 80, to: 100 },
		yellow: { from: 60, to: 90 },
		green: { from: 0, to: 20 }
	}
});
var val = 0;
window.setInterval(function(){ chartRevenue.redraw(Math.floor(Math.random()*10)+25) }, 100);


var chartExpenses = charts.gauge({
		container: '#chartExpenses',
		value: 0,
		size: 130,
		label: 'Expenses',
		minorTicks: 5,
		majorTicks: 5,
		zones: {
		red: { from: 60, to: 100 },
		yellow: { from: 75, to: 90 },
		green: { from: 0, to: 50 }
	}
});
var val = 0;
window.setInterval(function(){ chartExpenses.redraw(Math.floor(Math.random()*10)+55) }, 100);


var chartProfit = charts.gauge({
		container: '#chartProfit',
		value: 0,
		size: 130,
		label: 'Profit',
		minorTicks: 5,
		majorTicks: 5,
		zones: {
		red: { from: 40, to: 60 },
		yellow: { from: 75, to: 100 },
		green: { from: 0, to: 20 }
	}
});
var val = 0;
window.setInterval(function(){ chartProfit.redraw(Math.floor(Math.random()*10)+55) }, 100);

