$( document ).ready(function() {
	$("#mac").circliful({
			animation: 1,
			animationStep: 5,
			foregroundBorderWidth: 15,
			backgroundBorderWidth: 15,
			percent: 78,
			fontColor: '#b3bdcc',
			foregroundColor: '#BF7A6A',
			backgroundColor: '#353c48',
			multiPercentage: 1,
			percentages: [10, 20, 30]
	});
	$("#windows").circliful({
			animation: 1,
			animationStep: 5,
			foregroundBorderWidth: 15,
			backgroundBorderWidth: 15,
			percent: 48,
			fontColor: '#b3bdcc',
			foregroundColor: '#D2A968',
			backgroundColor: '#353c48',
			multiPercentage: 1,
			percentages: [10, 20, 30]
	});
	$("#linux").circliful({
			animation: 1,
			animationStep: 5,
			foregroundBorderWidth: 15,
			backgroundBorderWidth: 15,
			percent: 88,
			fontColor: '#b3bdcc',
			foregroundColor: '#6FB4CE',
			backgroundColor: '#353c48',
			multiPercentage: 1,
			percentages: [10, 20, 30]
	});
});