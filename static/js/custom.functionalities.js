window.onload = function() {

    // Load the category doughnut chart
    var request = $.ajax({
      url: "getDoughnutScript.html",
      contentType: "application/json; charset=utf-8",
      type: "POST",
      data: {label : "global_doughnut"},
      dataType: "html"
    });

    request.done(function(msg) {
      var config = JSON.parse(msg);
      var ctx = document.getElementById("chart-area").getContext("2d");
      window.myDoughnut = new Chart(ctx, config);
    });

    request.fail(function(jqXHR, textStatus) {
      alert( "Request failed: " + textStatus );
    });
};

// Load the subcategory doughnut chart on click on the category doughnut chart
document.getElementById("chart-area").onclick = function(evt)
{
    var activePoints = window.myDoughnut.getElementsAtEvent(evt);
    if(activePoints.length > 0)
    {
        //get the internal index of slice in pie chart
        var clickedElementIndex = activePoints[0]["_index"];

        //get specific label by index
        var label = window.myDoughnut.data.labels[clickedElementIndex];

        //get value by index
        var value = window.myDoughnut.data.datasets[0].data[clickedElementIndex];

        var request = $.ajax({
          url: "getDoughnutScript.html",
          type: "POST",
          data: {label : label},
          dataType: "html"
        });

        request.done(function(msg) {
          var config = JSON.parse(msg);
          var ctx = document.getElementById("chart-area-sub").getContext("2d");
          if(window.myDoughnutSub != null)
          {
            window.myDoughnutSub.destroy();
          }
          window.myDoughnutSub = new Chart(ctx, config);
        });

        request.fail(function(jqXHR, textStatus) {
          alert( "Request failed: " + textStatus );
        });
    }
}


function monthYearObject(month, year)
{
  this.month = month;
  this.year = year;
}

function eventLoadingManager()
{
  this.loaded_months = [];
  this.load_month = function(month, year)
  {
    // Check that the month has not been loaded yet
    var isThere = false;
    for(i = 0;i<this.loaded_months.length;i++)
    {
      var pair = this.loaded_months[i];
      if(pair.month == month && pair.year == year)
      {
        isThere = true;
        break;
      }
    }
    if(!isThere)
    {
      // Effectively load the month
      this.loaded_months.push(new monthYearObject(month, year));

      var request = $.ajax({
        url: "getMonthEvents",
        contentType: "application/json; charset=utf-8",
        type: "POST",
        data: {year: year, month: month},
        dataType: "html"
      });

      request.done(function(msg) {
        var events = JSON.parse(msg);
        for(i = 0; i < events.length ; i++)
        {
          $('#calendar').fullCalendar('renderEvent', events[i], stick=true);
        }
      });

      request.fail(function(jqXHR, textStatus) {
        alert( "Request failed: " + textStatus );
      });

    }
  }
}


$(document).ready(function() {

    // Initialize the calendar

    window.my_event_loading_manager = new eventLoadingManager();

    $('#calendar').fullCalendar({
        // Calendar definition
        header: {
				left: 'prev,next today',
				center: 'title',
				right: 'month,agendaWeek,agendaDay,listWeek'
			},
		aspectRatio: 0.8

    })

    // Load events for current date
    var moment = $('#calendar').fullCalendar('getDate');
    window.my_event_loading_manager.load_month(moment.format("M"), moment.format("Y"));

});

// Load events when clicking on the next button
$(document).on('click','.fc-next-button', function()
{
    var moment = $('#calendar').fullCalendar('getDate');
    window.my_event_loading_manager.load_month(moment.format("M"), moment.format("Y"));
})

// Load events when clicking on the prev button
$(document).on('click','.fc-prev-button', function()
{
    var moment = $('#calendar').fullCalendar('getDate');
    window.my_event_loading_manager.load_month(moment.format("M"), moment.format("Y"));
})