var pie = new d3pie("d3PieChart", {
	"header": {
		"title": {
			"text": "Skills",
			"fontSize": 21,
			"color": "#707C8E",
		},
		"location": "pie-center",
		"titleSubtitlePadding": 10
	},
	"size": {
		"canvasWidth": 260,
		"canvasHeight": 260,
		"pieInnerRadius": "85%",
		"pieOuterRadius": "65%"
	},
	"data": {
		"sortOrder": "label-desc",
		"content": [
			{
				"label": "HTML5",
				"value": 2,
				"color": "#BF7A6A"
			},
			{
				"label": "CSS3",
				"value": 10,
				"color": "#D2A968"
			},
			{
				"label": "Bootstrap",
				"value": 8,
				"color": "#FCB050"
			},
			{
				"label": "Sass/Less",
				"value": 5,
				"color": "#C3807C"
			},
			{
				"label": "RWD",
				"value": 4,
				"color": "#7C9490"
			},
			{
				"label": "Photoshop",
				"value": 4,
				"color": "#B1BDBC"
			},
			{
				"label": "jQuery",
				"value": 3,
				"color": "#648194"
			},
			{
				"label": "javascript",
				"value": 2,
				"color": "#D2A968"
			},
		]
	},
	"labels": {
		"outer": {
			"format": "label-percentage1",
			"pieDistance": 10
		},
		"inner": {
			"format": "none"
		},
		"mainLabel": {
			"fontSize": 11
		},
		"percentage": {
			"color": "#707C8E",
			"fontSize": 11,
			"decimalPlaces": 0
		},
		"value": {
			"color": "#cccc43",
			"fontSize": 11
		},
		"lines": {
			"enabled": true,
			"color": "#707C8E"
		},
		"truncation": {
			"enabled": true
		}
	},
	"tooltips": {
		"enabled": true,
		"type": "placeholder",
		"string": "{label}: {value}, {percentage}%"
	},
	"effects": {
		"pullOutSegmentOnClick": {
			"effect": "linear",
			"speed": 400,
			"size": 5
		}
	},
	"misc": {
		"colors": {
			"segmentStroke": "#2a3039"
		}
	}
});