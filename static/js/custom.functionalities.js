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

$(document).ready(function() {

    // Initialize the calendar

    $('#calendar').fullCalendar({
        // put your options and callbacks here
        header: {
				left: 'prev,next today',
				center: 'title',
				right: 'month,agendaWeek,agendaDay,listWeek'
			},
		height: "auto"

    })
    var moment = $('#calendar').fullCalendar('getDate');


    var request = $.ajax({
      url: "getMonthEvents",
      contentType: "application/json; charset=utf-8",
      type: "POST",
      data: {year: moment.format("Y"), month: moment.format("M")},
      dataType: "html"
    });

    request.done(function(msg) {
      var events = JSON.parse(msg);
      for(i = 0; i < events.length ; i++)
      {
        $('#calendar').fullCalendar('renderEvent', events[i]);
      }
    });

    request.fail(function(jqXHR, textStatus) {
      alert( "Request failed: " + textStatus );
    });

});
