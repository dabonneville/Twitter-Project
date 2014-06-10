var dataDirectory = "/filepath/to/data",
    dateFormat = d3.time.format("%x"),
    datetimeFormat = d3.time.format("%x %-I %p"),
    commaFormat = d3.format(",");

var congress, us;  // Geodata globals.


/**
 * Load data and render a Multiple Series Line Chart to an element.
 *
 * @param {string} filename The name of the file containing the chart data.
 * @param {string} id The DOM ID to which to append the table.
 */
function lineWithFocusChart(filename, id, format) {
  d3.json(dataDirectory + filename, function(data) {
    nv.addGraph(function() {
      var chart = nv.models.lineWithFocusChart()
          .margin({top: 30, right: 40, bottom: 30, left: 60})
          .margin2({top: 0, right: 40, bottom: 30, left: 60})
          .x(function(d) { return d[0] })
          .y(function(d) { return d[1] });

      chart.xAxis
          .showMaxMin(false)
          .staggerLabels(true)
          .tickFormat(function(d) { return format(new Date(d)) });
      chart.x2Axis
          .showMaxMin(false)
          .staggerLabels(true)
          .tickFormat(function(d) { return format(new Date(d)) });

      chart.yAxis
          .showMaxMin(false)
          .tickFormat(commaFormat);
      chart.y2Axis
          .showMaxMin(false)
          .tickFormat(commaFormat);

      d3.select(id)
          .datum(data)
        .transition().duration(500)
          .call(chart);

      nv.utils.windowResize(chart.update);

      return chart;
    });
  });
};


function stackedAreaChart(filename, id, format) {
  d3.json(dataDirectory + filename, function(data) {
    nv.addGraph(function() {
      var chart = nv.models.stackedAreaChart()
                    .x(function(d) { return d[0] })
                    .y(function(d) { return d[1] })
                    .clipEdge(true);

      chart.xAxis
          .showMaxMin(false)
          .tickFormat(function(d) { return format(new Date(d)) });

      chart.yAxis
          .tickFormat(d3.format(',.2f'));

      d3.select(id)
        .datum(data)
          .transition().duration(500).call(chart);

      nv.utils.windowResize(chart.update);

      return chart;
    });
  });
};

function multiBarHorizontalChart(filename, id) {
  d3.json(dataDirectory + filename, function(data) {
    nv.addGraph(function() {
      var chart = nv.models.multiBarHorizontalChart()
          .margin({top: 30, right: 20, bottom: 50, left: 160})
          .x(function(d) { return d[0] })
          .y(function(d) { return d[1] })
          .stacked(true);

      chart.yAxis
          .tickFormat(commaFormat);

      d3.select(id)
          .datum(data)
        .transition().duration(500)
          .call(chart);

      nv.utils.windowResize(chart.update);

      return chart;
    });
  });
};


function choroplethChart(filename, id) {
  d3.csv(dataDirectory + filename, function(data) {
    nv.addGraph(function() {
      var chart = qac.models.choroplethChart();

      d3.select(id)
          .datum([congress, us, data])  // Requires global geodata variables.
        .transition().duration(500)
          .call(chart);

      nv.utils.windowResize(chart.update);

      return chart;
    });
  });
};


/**
 * Load an HTML file from the server and set its contents to an element.
 *
 * @param {string} filename The name of the file containing the HTML table.
 * @param {string} id The DOM ID to which to append the table.
 */
insertHTML = function(filename, id) {
  $.get(dataDirectory + filename, function(data) {
    $(id).html(data);
  });
};


/* Tab Handlers *****************************************************/

var overallCurrentAgg = "day";

$(".btn-overall-volume").click(function() {
  overallRequestAgg = $(this).text().toLowerCase();
  if (overallRequestAgg !== overallCurrentAgg) {
    overallCurrentAgg = overallRequestAgg;
    switch (overallRequestAgg) {
      case "day":
        document.getElementById("overall-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("overall-volume-day.json", "#overall-volume svg", dateFormat);
        break;
      case "hour":
        document.getElementById("overall-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("overall-volume-hour.json", "#overall-volume svg", datetimeFormat);
        break;
    }
  }
});

var partyCurrentAgg = "day";

$(".btn-party-volume").click(function() {
  partyRequestAgg = $(this).text().toLowerCase();
  if (partyRequestAgg !== partyCurrentAgg) {
    switch (partyRequestAgg) {
      case "day":
        document.getElementById("party-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("party-volume-day.json", "#party-volume svg", dateFormat);
        break;
      case "hour":
        document.getElementById("party-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("party-volume-hour.json", "#party-volume svg", datetimeFormat);
        break;
    }
    partyCurrentAgg = partyRequestAgg;
  }
});

var overallCurrentAggSenate = "hour";

$(".btn-overall-volume-senate").click(function() {
  overallRequestAgg = $(this).text().toLowerCase();
  if (overallRequestAgg !== overallCurrentAgg) {
    overallCurrentAgg = overallRequestAgg;
    switch (overallRequestAgg) {
      case "hour":
        document.getElementById("overall-volume-senate").innerHTML = "<svg></svg>";
        lineWithFocusChart("overall-volume-senate-hour.json", "#overall-volume-senate svg", datetimeFormat);
        break;
      case "day":
        document.getElementById("overall-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("overall-volume-senate-day.json", "#overall-volume-senate svg", dateFormat);
        break;
    }
  }
});

var partyCurrentAggSenate = "hour";

$(".btn-party-volume-senate").click(function() {
  partyRequestAggSenate = $(this).text().toLowerCase();
  if (partyRequestAggSenate !== partyCurrentAggSenate) {
    switch (partyRequestAggSenate) {
      case "hour":
        document.getElementById("party-volume-senate").innerHTML = "<svg></svg>";
        lineWithFocusChart("party-volume-senate-hour.json", "#party-volume-senate svg", datetimeFormat);
        break;
      case "day":
        document.getElementById("party-volume-senate").innerHTML = "<svg></svg>";
        lineWithFocusChart("party-volume-senate-day.json", "#party-volume-senate svg", dateFormat);
        break;
    }
    partyCurrentAggSenate = partyRequestAggSenate;
  }
});

var immigrationCurrentAgg = "hour";

$(".btn-immigration-volume").click(function() {
  immigrationRequestAgg = $(this).text().toLowerCase();
  if (immigrationRequestAgg !== immigrationCurrentAgg) {
    switch (immigrationRequestAgg) {
      case "hour":
        document.getElementById("immigration-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("immigration-volume-hour.json", "#immigration-volume svg", datetimeFormat);
        break;
      case "day":
        document.getElementById("immigration-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("immigration-volume-day.json", "#immigration-volume svg", dateFormat);
        break;
    }
    immigrationCurrentAgg = immigrationRequestAgg;
  }
});

var healthcareCurrentAgg = "hour";

$(".btn-healthcare-volume").click(function() {
  healthcareRequestAgg = $(this).text().toLowerCase();
  if (healthcareRequestAgg !== healthcareCurrentAgg) {
    switch (healthcareRequestAgg) {
      case "hour":
        document.getElementById("healthcare-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("healthcare-volume-hour.json", "#healthcare-volume svg", datetimeFormat);
        break;
      case "day":
        document.getElementById("healthcare-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("healthcare-volume-day.json", "#healthcare-volume svg", dateFormat);
        break;
    }
    healthcareCurrentAgg = healthcareRequestAgg;
  }
});

var syriaCurrentAgg = "hour";

$(".btn-syria-volume").click(function() {
  syriaRequestAgg = $(this).text().toLowerCase();
  if (syriaRequestAgg !== syriaCurrentAgg) {
    switch (syriaRequestAgg) {
      case "hour":
        document.getElementById("syria-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("syria-volume-hour.json", "#syria-volume svg", datetimeFormat);
        break;
      case "day":
        document.getElementById("syria-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("syria-volume-day.json", "#syria-volume svg", dateFormat);
        break;
    }
    syriaCurrentAgg = syriaRequestAgg;
  }
});

var sentimentCurrentAgg = "hour";

$(".btn-sentiment-volume").click(function() {
  sentimentRequestAgg = $(this).text().toLowerCase();
  if (sentimentRequestAgg !== sentimentCurrentAgg) {
    switch (sentimentRequestAgg) {
      case "hour":
        document.getElementById("sentiment-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("sentiment-volume-hour.json", "#sentiment-volume svg", datetimeFormat);
        break;
      case "day":
        document.getElementById("sentiment-volume").innerHTML = "<svg></svg>";
        lineWithFocusChart("sentiment-volume-day.json", "#sentiment-volume svg", dateFormat);
        break;
    }
    sentimentCurrentAgg = sentimentRequestAgg;
  }
});

function geodataHandler(callback) {
  d3.json("us-congress-113.json", function(e, data) {
    congress = data;
    d3.json("us.json", function(e, data) {
      us = data;
      callback();  // Execute callback after loading geodata.
    });
  });
};

function tabHandlerOverall() {
  lineWithFocusChart("overall-volume-day.json", "#overall-volume svg", datetimeFormat);
  lineWithFocusChart("sentiment-volume-day.json", "#sentiment-volume svg", datetimeFormat);
  choroplethChart("overall-choropleth.csv", "#overall-choropleth");
  stackedAreaChart("stack-area-day.json", "#stack-area svg", datetimeFormat);
  multiBarHorizontalChart("overall-source.json", "#overall-source svg");
  multiBarHorizontalChart("overall-hashtag24.json", "#overall-hashtag svg");
  multiBarHorizontalChart("overall-domain.json", "#overall-domain svg");
};

function tabHandlerParty() {
  lineWithFocusChart("party-volume-hour.json", "#party-volume svg", datetimeFormat);
  lineWithFocusChart("overall-volume-senate-hour.json", "#overall-volume-senate svg", datetimeFormat);
  lineWithFocusChart("party-volume-senate-hour.json", "#party-volume-senate svg", datetimeFormat);
  lineWithFocusChart("sentiment-volume-hour.json", "#sentiment-volume svg", datetimeFormat);
  insertHTML("democrat-hashtag.html", "#democrat-hashtag");
  insertHTML("republican-hashtag.html", "#republican-hashtag");
  insertHTML("democrat-domain.html", "#democrat-domain");
  insertHTML("republican-domain.html", "#republican-domain");
};

function tabHandlerIssueImmigration() {
  lineWithFocusChart("immigration-volume-hour.json", "#immigration-volume svg", datetimeFormat);
  choroplethChart("immigration-choropleth.csv", "#immigration-choropleth");
};

function tabHandlerIssueHealthcare() {
  lineWithFocusChart("healthcare-volume-hour.json", "#healthcare-volume svg", datetimeFormat);
  choroplethChart("healthcare-choropleth.csv", "#healthcare-choropleth");
};

function tabHandlerIssueSyria() {
  lineWithFocusChart("syria-volume-hour.json", "#syria-volume svg", datetimeFormat);
  choroplethChart("syria-choropleth.csv", "#syria-choropleth");
};


/* ******************************************************************/


var loadedTabs = {};

geodataHandler(tabHandlerOverall);

$('a[data-toggle="tab"]').on("shown", function (e) {
  activatedTab = $(e.target).attr("href");
  // previousTab  = $(e.relatedTarget).attr("href");

  if (!(activatedTab in loadedTabs)) {
    switch (activatedTab) {
      case "#party":
        tabHandlerParty();
        break;
      case "#issue-immigration":
        tabHandlerIssueImmigration();
        break;
      case "#issue-healthcare":
        tabHandlerIssueHealthcare();
        break;
      case "#issue-syria":
        tabHandlerIssueSyria();
        break;
    }
    loadedTabs[activatedTab] = true;
  }
});

