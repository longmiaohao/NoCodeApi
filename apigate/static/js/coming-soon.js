(function($) {
  $.fn.countdown = function(options, callback) {
    //custom 'this' selector
    thisEl = $(this); 
  
    // array of custom settings
    var settings = { 
      'date': null,
      'format': null
    };

    // append the settings array to options
    if(options) {
      $.extend(settings, options);
    }
   
    //create the countdown processing function
    function countdown_proc() {
    var eventDate = Date.parse(settings.date) / 1000;
    var currentDate = Math.floor($.now() / 1000);
    
    if(eventDate <= currentDate) {
    callback.call(this);
    clearInterval(interval);
    }
      
    var seconds = eventDate - currentDate;
    
    var days = Math.floor(seconds / (60 * 60 * 24)); 
    //calculate the number of days
    
    seconds -= days * 60 * 60 * 24; 
    //update the seconds variable with number of days removed
    
    var hours = Math.floor(seconds / (60 * 60));
    seconds -= hours * 60 * 60; 
    //update the seconds variable with number of hours removed
    
    var minutes = Math.floor(seconds / 60);
    seconds -= minutes * 60; 
    //update the seconds variable with number of minutes removed
    
    //conditional statements
    if (days == 1) { thisEl.find(".timeDays").text("day"); } else { thisEl.find(".timeDays").text("days"); }
		    if (hours == 1) { thisEl.find(".timeHours").text("hour"); } else { thisEl.find(".timeHours").text("hours"); }
		    if (minutes == 1) { thisEl.find(".timeMinutes").text("minute"); } else { thisEl.find(".timeMinutes").text("minutes"); }
		    if (seconds == 1) { thisEl.find(".timeSeconds").text("second"); } else { thisEl.find(".timeSeconds").text("seconds"); }
    
    //logic for the two_digits ON setting
    if(settings.format == "on") {
        days = (String(days).length >= 2) ? days : "0" + days;
        hours = (String(hours).length >= 2) ? hours : "0" + hours;
        minutes = (String(minutes).length >= 2) ? minutes : "0" + minutes;
        seconds = (String(seconds).length >= 2) ? seconds : "0" + seconds;
    }
    
    //update the countdown's html values.
    thisEl.find(".days").text(days);
    thisEl.find(".hours").text(hours);
    thisEl.find(".minutes").text(minutes);
    thisEl.find(".seconds").text(seconds);
  }

	//run the function
	countdown_proc();

	//loop the function
	interval = setInterval(countdown_proc, 1000);
  };

}) (jQuery);



//Provide the plugin settings
$("#countdown").countdown({
      //The countdown end date
      date: "1 May 2017 12:00:00",
      
      // on (03:07:52) | off (3:7:52) - two_digits set to ON maintains layout consistency
      format: "on"
      }, 
  
      function() {
      // This will run when the countdown ends
       alert("We're Out Now");
       });
	   
	   
	 function setHeights() {
  var windowHeight = $(window).height();
  $('.slide').height(windowHeight);
}

setHeights();

$(window).resize(function() {
  setHeights();
});

function addSticky() {
  $('.slide').each(function() {
    var scrollerAnchor = $(this).offset().top;
    if (window.scrollY >= scrollerAnchor) {
      $(this).addClass('fix-it');
    } else {
      $(this).removeClass('fix-it');
    }
  });
}

$(window).scroll(function() {
  addSticky();
});  