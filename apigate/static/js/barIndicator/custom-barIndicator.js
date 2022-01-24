$('#defaultBar').barIndicator();



// Bar Color
var opt = {foreColor:'#BF7A6A'};$('#barColor').barIndicator(opt);

// Bar Height
var opt = { horBarHeight:27}; $('#barHeight').barIndicator(opt);

// Vertical Height
var opt = { style:'vertical'}; $('#barVertical').barIndicator(opt);
var opt = { style:'vertical', foreColor:'#BF7A6A'}; $('#barVertical2').barIndicator(opt);
var opt = { style:'vertical', foreColor:'#A9BD7A'}; $('#barVertical3').barIndicator(opt);

// Bar Holder Color
var opt = {foreColor:'#D2A968', backColor:'#6FB4CE'}; $('#barHolderColor').barIndicator(opt);

// label Positions
var opt = {horLabelPos:'topRight', foreColor:'#BF7A6A'};$('#barLabelTopRight').barIndicator(opt);
var opt = {horLabelPos:'right', foreColor:'#6FB4CE'};$('#barLabelRight').barIndicator(opt);
var opt = {horLabelPos:'left', foreColor:'#A9BD7A'};$('#barLabelLeft').barIndicator(opt);