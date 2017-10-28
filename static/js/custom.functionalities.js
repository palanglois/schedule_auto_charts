window.onload = function() {

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

document.getElementById("chart-area").onclick = function(evt)
{
    var activePoints = window.myDoughnut.getElementsAtEvent(evt);
    if(activePoints.length > 0)
    {
        //get the internal index of slice in pie chart
        var clickedElementindex = activePoints[0]["_index"];

        //get specific label by index
        var label = window.myDoughnut.data.labels[clickedElementindex];

        //get value by index
        var value = window.myDoughnut.data.datasets[0].data[clickedElementindex];

        var request = $.ajax({
          url: "getDoughnutScript.html",
          type: "POST",
          data: {label : label},
          dataType: "html"
        });

        request.done(function(msg) {
          var config = JSON.parse(msg);
          var ctx = document.getElementById("chart-area-sub").getContext("2d");
          console.log($('#chart-area-sub'));
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

