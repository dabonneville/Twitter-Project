var qac = window.qac || {};

window.qac = qac;

qac.models = {};


/**
 * Load data and render a Choropleth to an element.
 *
 * @param {string} filename The name of the file containing the chart data.
 * @param {string} id The DOM ID to which to append the table.
 */
qac.models.choroplethChart = function() {
  var width = 940,
      height = 500,
      numberIntervals = 6,
      metadataByID = d3.map(),
      rateById = d3.map(),
      path = d3.geo.path(),
      log = d3.scale.log(),
      quantize = d3.scale.quantize();

  function chart(selection) {
    selection.each(function(data) {

      // Destructure and coerce data.
      var congress  = data[0],
          us        = data[1],
          frequency = data[2];

      frequency.forEach(function(d) {
        d.id = +d.id;
        d.rate = +d.rate;
      });

      log
          .domain(d3.extent(frequency, function(d) { return d.rate; }));

      frequency.forEach(function(d) {
        metadataByID.set(d.id, d);  // Note the redundant data; d.id is stored twice
        rateById.set(d.id, log(d.rate));
      });

      quantize
          .domain([0, 1])
          .range(d3.range(numberIntervals).map(function(d) { return "q" + d + "-" + numberIntervals; }));

      // Prepare chart container.
      var svg = d3.select(this).selectAll("svg").data([data]);

      var gEnter = svg.enter().append("svg").append("g");
      gEnter.append("g").attr("class", "legend");
      gEnter.append("g").attr("class", "districts");
      gEnter.append("path").attr("class", "states");
      gEnter.append("text").attr("class", "representative");
      gEnter.append("text").attr("class", "affiliation");
      gEnter.append("text").attr("class", "url");
      gEnter.append("text").attr("class", "rate");

      svg .attr("width", width)
          .attr("height", height);

      var g = svg.select("g");

      // Render districts and states.
      var districts = g.select(".districts")
          .selectAll("path")
            .data(topojson.feature(congress, congress.objects.districts).features)
          .enter().append("path")
            .attr("class", function(d) { return quantize(rateById.get(d.id)); })
            .attr("d", path)
            .style("opacity", .8);

      g.select(".states")
          .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
          .attr("d", path);

      // Add legend.
      var legendData = quantize.range()
          .map(quantize.invertExtent)
          .map(function(d) { return d.map(log.invert); })
          .map(function(d) { return d.map(function(i) { return d3.round(i, 0) }); })
          .map(function(d, i) {
            if (i === (numberIntervals - 1)) {
              return "[" + d[0] + " - " + d[1] + "]"
            } else {
              return "[" + d[0] + " - " + d[1] + ")"
            }
          });

      var legendWidth = 20,
          legendHeight = 20;

      var legend = gEnter.select(".legend");

      legend
          .selectAll("rect")
            .data(legendData)
          .enter().append("rect")
            .attr("x", width - 100)
            .attr("y", function(d, i) { return height - i * legendHeight - 10 * legendHeight;})
            .attr("width", legendWidth)
            .attr("height", legendHeight)
            .attr("class", function(d, i) { return quantize.range()[i]; })
            .style("opacity", 0.8);

      legend
          .selectAll("text")
             .data(legendData)
          .enter().append("text")
            .attr("x", width - 75)
            .attr("y", function(d, i) { return height - i * legendHeight - 9.25 * legendHeight;})
            .text(function(d, i) { return legendData[i]; });

      // Add metadata.
      var representative = gEnter.select(".representative")
            .attr("x", width - 170)
            .attr("y", height - 140);

      var affiliation = gEnter.select(".affiliation")
            .attr("x", width - 170)
            .attr("y", height - 125);

      var url = gEnter.select(".url")
            .attr("x", width - 170)
            .attr("y", height - 110);

      var rate = gEnter.select(".rate")
            .attr("x", width - 170)
            .attr("y", height - 95);

      // Add mouseover effects.
      districts.on("mouseout", function() {
        d3.select(this)
          .transition().duration(300)
          .style("opacity", .8);
      });

      districts.on("mouseover", function(d) {
        d3.select(this)
          .transition().duration(300)
          .style("opacity", 1);

        metadata = metadataByID.get(d.id);
        if (metadata) {
          representative.text(metadata.representative);
          affiliation.text("(" + metadata.affiliation + ", " + metadata.district + ")");
          url.text("twitter.com/" + metadata.screen_name);
          rate.text(function(d) { if (metadata.rate === 1) { return metadata.rate + " Tweet"; } else { return metadata.rate + " Tweets"; }} );
        };
      });

    });
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  return chart;
};

