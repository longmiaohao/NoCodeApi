
var weekStart = new Date();
weekStart.setDate(weekStart.getDate() - weekStart.getDay());
var ranges = d3.range(+weekStart/1000, +weekStart/1000 + 3600*24*8, 3600*20);

var max = 50;
var min = 10;

var marcData = {};

// Creating random data
ranges.map(function(element, index, array) {
  marcData[element] = Math.floor(Math.random() * (max - min) + min);
});

var cal = new CalHeatMap();
cal.init({
  itemSelector: "#cal-heatmap",
  domain: "week",
  data: marcData,
  colLimit: 7,
  cellSize: 16,
  range: 1,
  // legend: [5, 30, 40, 50],
  displayLegend: false,
  // legendHorizontalPosition: "center",
  tooltip: true,
});