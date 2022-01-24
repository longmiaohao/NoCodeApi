$(function(){
	if(!(/^\?noconvert/gi).test(location.search)){
		$(".tempGauge0").tempGauge({width:90, borderWidth: 2, showLabel:true});
		$(".tempGauge1").tempGauge({width:70, borderWidth: 2, showLabel:true, fillColor:"#BF7A6A"});
		$(".tempGauge2").tempGauge({width:60, borderWidth: 2, borderColor:"#707C8E", fillColor:"#D2A968", showLabel:true});
		$(".tempGauge3").tempGauge({width:40, borderWidth: 2, fillColor:"#6FB4CE", showLabel:true});
		$(".tempGauge4").tempGauge({width:30, borderWidth: 2, fillColor:"#999999"});		
	}
});