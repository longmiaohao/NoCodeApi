// USA map 1
$(function(){
	var cityAreaData = [
		230.20,
		750.90,
		440.28,
		180.15,
		69.35,
		280.90,
		510.50,
		99.60,
		135.50
	]
	$('#us-map2').vectorMap({
		map: 'us_aea_en',
		scaleColors: ['#707C8E'],
		normalizeFunction: 'polynomial',
		focusOn:{
			x: 2,
			y: 0,
			scale: 1
		},
		zoomOnScroll: false,
		zoomMin: 1,
		hoverColor: true,
		regionStyle:{
			initial: {
				fill: '#67C394',
			},
			hover: {
				"fill-opacity": 0.8
			},
		},
		markerStyle: {
			initial: {
				fill: '#E64C66',
				stroke: '#D2A968',
				r: 5
			}
		},
		backgroundColor: '#2a3039',
		 markers :[
			{latLng: [32.90, -97.03], name: 'Dallas/FW,TX'},
			{latLng: [34.11, -79.24], name: 'Marion S.C'},
			{latLng: [40.09, -74.51], name: 'Levittown, Pa'},
			{latLng: [32.33, -92.55], name: 'Arcadia, La'},
			{latLng: [35.53, -11.25], name: 'Cameron, Ariz'},
			{latLng: [39.46, -86.09], name: 'Indianapolis'},
			{latLng: [38.32, -82.41], name: 'Ironton, Ohio'},
			{latLng: [38.50, -104.49], name: 'Colorado Springs'},
			{latLng: [45.14, -120.11], name: 'Condon'},
			{latLng: [19.12, -155.29], name: 'Pahala'},
			{latLng: [64.44, -120.17], name: 'Los Alamos, Calif'},
			{latLng: [70.10, -105.06], name: 'Longmont'},
			{latLng: [57.05, -134.50], name: 'Baranof'},
			{latLng: [37.30, -119.30], name: 'California, CA'},
			{latLng: [36.10,-115.09], name: 'Las Vegas, Nev'},
			{latLng: [56.48, -132.58], name: 'Petersburg, Alaska'},
			{latLng: [29.35, -95.46 ], name: 'Richmond Tex'},
			{latLng: [31.02, -85.52], name: 'Geneva, Ala'},
			{latLng: [42.11, -73.30], name: 'Hillsdale, N.Y'},
			{latLng: [48.30, -122.14], name: 'Sedro Wooley'},
			{latLng: [32.46, -108.17], name: 'Silver City'},
			{latLng: [43.25, -74.22], name: 'Hamilton Mt.'},
			{latLng: [32.42, -108.08], name: 'Hurley, N. Mex'},
			{latLng: [35.22, -117.38], name: 'Johannesburg'},
			{latLng: [40.50, -79.38], name: 'Worthington Pa'},
			{latLng: [37.45, -119.40], name: 'Yosemite Nat. Park'},
			{latLng: [41.09, -81.22], name: 'Kent, Ohio'},
			{latLng: [40.0, -74.30], name: 'New Jersey'},
		],
		series: {
			markers: [{
				attribute: 'r',
				scale: [3, 7],
				values: cityAreaData
			}]
		},
	});
});

// Africa
$(function(){
	$('#mapAfrica').vectorMap({
		map: 'africa_mill',
		backgroundColor: '#2a3039',
		scaleColors: ['#707C8E'],
		zoomOnScroll:false,
		zoomMin: 1,
		hoverColor: true,
		series: {
			regions: [{
				values: gdpData,
				scale: ['#FFF997', '#FEDFDD', '#FBACAF', '#E4817B', '#AE4357'],
				normalizeFunction: 'polynomial'
			}]
		},
	});
});

// Markers on the world map
$(function(){
	$('#world-map-markers').vectorMap({
		map: 'world_mill_en',
		scaleColors: ['#6FB4CE', '#A9BD7A'],
		normalizeFunction: 'polynomial',
		hoverOpacity: 0.7,
		hoverColor: false,
		zoomOnScroll: false,
		markerStyle: {
			initial: {
				fill: '#E04747',
				stroke: '#FFFFFF',
				r: 4
			}
		},
		zoomMin: 1,
		hoverColor: true,
		series: {
			regions: [{
				values: gdpData,
				scale: ['#89A4C1', '#959AB8'],
				normalizeFunction: 'polynomial'
			}]
		},
		backgroundColor: '#2a3039',
		markers: [
			{latLng: [41.90, 12.45], name: 'Vatican City'},
			{latLng: [43.73, 7.41], name: 'Monaco'},
			{latLng: [-0.52, 166.93], name: 'Nauru'},
			{latLng: [-8.51, 179.21], name: 'Tuvalu'},
			{latLng: [43.93, 12.46], name: 'San Marino'},
			{latLng: [47.14, 9.52], name: 'Liechtenstein'},
			{latLng: [7.11, 171.06], name: 'Marshall Islands'},
			{latLng: [37.30, -119.30], name: 'California, CA'},
			{latLng: [56.48, -132.58], name: 'Petersburg, Alaska'},
			{latLng: [28.61, 77.20], name: 'New Delhi'},
			{latLng: [57.9, 2.9], name: 'Aberdeen'},
			{latLng: [36.52, 174.45], name: 'Auckland'},
			{latLng: [39.55, 116.25], name: 'Beijing'},
			{latLng: [12.56, 38.27], name: 'Salvador'},
			{latLng: [33.55, 18.22], name: 'Cape Town'},
			{latLng: [61.52, 105.31], name: 'Moscow'},
			{latLng: [31.57, 115.52], name: 'Perth'},
			{latLng: [17.3, -62.73], name: 'Saint Kitts and Nevis'},
			{latLng: [3.2, 73.22], name: 'Maldives'},
			{latLng: [35.88, 14.5], name: 'Malta'},
			{latLng: [-4.61, 55.45], name: 'Seychelles'},
			{latLng: [42.5, 1.51], name: 'Andorra'},
			{latLng: [-21.13, -175.2], name: 'Tonga'},
			{latLng: [26.02, 50.55], name: 'Bahrain'},
		]
	});
});

// World Map GDP
$(function(){
	$('#world-map-gdp').vectorMap({
		map: 'world_mill_en',
		zoomOnScroll: false,
		series: {
			regions: [{
				values: gdpData,
				scale: ['#FFF997', '#FEDFDD', '#FBACAF', '#E4817B', '#AE4357'],
				normalizeFunction: 'polynomial'
			}]
		},
		backgroundColor: '#2a3039',
		onRegionTipShow: function(e, el, code){
			el.html(el.html()+' (GDP - '+gdpData[code]+')');
		}
	});
});

// Denmark
$(function(){
	$('#mapDenmark').vectorMap({
		map: 'dk_mill',
		zoomOnScroll: false,
		regionStyle:{
			initial: {
				fill: '#F6D683',
			},
			hover: {
				"fill-opacity": 0.8
			},
			selected: {
				fill: '#A9BD7A'
			},
		},
		backgroundColor: '#2a3039',
	});
});

// Europe
$(function(){
	$('#mapEurope').vectorMap({
		map: 'europe_mill',
		zoomOnScroll: false,
		series: {
			regions: [{
				values: gdpData,
				scale: ['#5F4E61', '#D2A968', '#A9BD7A', '#6FB4CE'],
				normalizeFunction: 'polynomial'
			}]
		},
		backgroundColor: '#2a3039',
	});
});

// Resions Selection
$(function(){
	var map,
	markers = [
		{latLng: [52.50, 13.39], name: 'Berlin'},
		{latLng: [53.56, 10.00], name: 'Hamburg'},
		{latLng: [48.13, 11.56], name: 'Munich'},
		{latLng: [50.95, 6.96], name: 'Cologne'},
		{latLng: [50.11, 8.68], name: 'Frankfurt am Main'},
		{latLng: [48.77, 9.17], name: 'Stuttgart'},
		{latLng: [51.23, 6.78], name: 'Düsseldorf'},
		{latLng: [51.51, 7.46], name: 'Dortmund'},
		{latLng: [51.45, 7.01], name: 'Essen'},
		{latLng: [53.07, 8.80], name: 'Bremen'}
	],
	cityAreaData = [
		887.70,
		755.16,
		310.69,
		405.17,
		248.31,
		207.35,
		217.22,
		280.71,
		210.32,
		325.42
	]

	map = new jvm.Map({
		container: $('#regionSelection'),
		map: 'de_merc',
		zoomOnScroll: false,
		zoomMin: 1,		
		regionsSelectable: true,
		markersSelectable: true,
		markers: markers,
		markerStyle: {
			initial: {
				fill: '#4DAC26'
			},
			selected: {
				fill: '#CA0020'
			}
		},
		regionStyle: {
			initial: {
				fill: '#6FB4CE'
			},
			selected: {
				fill: '#FCB050'
			}
		},
		series: {
			markers: [{
				attribute: 'r',
				scale: [5, 15],
				values: cityAreaData
			}]
		},
		backgroundColor: '#2a3039',
		onRegionSelected: function(){
			if (window.localStorage) {
				window.localStorage.setItem(
					'jvectormap-selected-regions',
					JSON.stringify(map.getSelectedRegions())
				);
			}
		},
		onMarkerSelected: function(){
			if (window.localStorage) {
				window.localStorage.setItem(
					'jvectormap-selected-markers',
					JSON.stringify(map.getSelectedMarkers())
				);
			}
		}
	});
	map.setSelectedRegions( JSON.parse( window.localStorage.getItem('jvectormap-selected-regions') || '[]' ) );
	map.setSelectedMarkers( JSON.parse( window.localStorage.getItem('jvectormap-selected-markers') || '[]' ) );
});


// Resions with Labels
$(function(){
	new jvm.Map({
		map: 'us_aea',
		container: $('#resionsWithLabels'),
		zoomOnScroll: false,
		zoomMin: 1,
		hoverColor: true,
		regionLabelStyle: {
			initial: {
				fill: '#B90E32'
			},
			hover: {
				fill: 'black'
			}
		},
		backgroundColor: '#2a3039',
		labels: {
			regions: {
				render: function(code){
					var doNotShow = ['US-RI', 'US-DC', 'US-DE', 'US-MD'];

					if (doNotShow.indexOf(code) === -1) {
						return code.split('-')[1];
					}
				},
				offsets: function(code){
					return {
						'CA': [-10, 10],
						'ID': [0, 40],
						'OK': [25, 0],
						'LA': [-20, 0],
						'FL': [45, 0],
						'KY': [10, 5],
						'VA': [15, 5],
						'MI': [30, 30],
						'AK': [50, -25],
						'HI': [25, 50]
					}[code.split('-')[1]];
				}
			}
		}
	});
});