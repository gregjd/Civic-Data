rimap = function () {

    // Set up projection
    var projection = d3.geo.mercator()
                            .center([-71.4121134, 41.8148182]) // centered on Providence
                            // .center([-71.5064508, 41.5827282,]) // centered on RI
                            .scale(40000);
    var path = d3.geo.path()
                        .projection(projection);

    // Converts a number to a percent, with a certain number of decimal places
    function toPct(value, decimal_places) {

        if (isNaN(value) || isNaN(decimal_places)) {
            throw Error("Parameters for toPct() must be numbers.");
        } else {
            return (value*100).toFixed(decimal_places) + "%";
        }   
    }

    // Takes an array and produces an array with intervals between the values in the original array
    // (Intended to produce legend text using color.domain())
    function getIntervals(array) {

        var new_array = [];
        new_array.push("Less than " + array[0]);
        for (var n = 1; n < array.length; n++) {
            new_array.push(array[n-1] + " - " + array[n]);
        }
        new_array.push("Over " + array.slice(-1));

        return new_array;
    }

    // Loads the geodata and draws the map
    function drawMap(config, dataset) {

        // Set geojson file (and name of field with polygon names)
        if (config.region === "Rhode Island") {
            var geo_file = "ri_muni.geojson";
            var geo_name = "MUNI";
        } else if (config.region === "Providence") {
            var geo_file = "prov_nhood.geojson";
            var geo_name = "LNAME";
        } else {
            throw Error("In rimap_config.json, 'region' must be \
                either 'Providence' or 'Rhode Island'.");
        }

        // Define color scale
        var color = d3.scale.threshold()
                            .domain(config.cutoffs)
                            .range(config.colors);

        // var legend_items = map(color.domain(), toPct);

        // Define what goes in the box that appears when you hover over a location
        var tip = d3.tip()
                    .attr("class", "d3-tip")
                    .offset([-10, 0])
                    .html(function (d) {
                        var calc = d.properties[config.value] / (d.properties[config.norm] || 1);
                        var num = config.percent ? toPct(calc, 1) : calc;
                        if (config.value_exceed && calc > config.value_exceed) {
                            var num_color = config.color_exceed;
                        } else {
                            var num_color = config.color_default;
                        }
                        var city = d.properties[geo_name];
                        return "<strong>" + city + "</strong><br>" + config.text +
                            ": <span style='color:" + num_color + "'>" + num + "</span>";
                    });

        // Create SVG
        var svg = d3.select("body")
                    .append("svg")
                    .attr("width", config.size)
                    .attr("height", config.size);

        svg.call(tip);

        // Open the file with location (municipality/neighborhood) shapes
        d3.json(geo_file, function (geo_data) {

            // Attach our data as properties of the location shapes
            for (var i = 0; i < geo_data.features.length; i++) {
                var loc_name = geo_data.features[i].properties[geo_name];
                var loc_data = dataset[loc_name] || dataset[loc_name.toUpperCase()];
                for (p in loc_data) {
                    geo_data.features[i].properties[p] = loc_data[p];
                }
            }
            
            // Draw the map    
            svg.selectAll("path")
                .data(geo_data.features, function (d) { return d.properties[geo_name]; })
                .enter()
                .append("path")
                .attr("d", path)
                .style("fill", function (d) {
                    var val = d.properties[config.value] / (d.properties[config.norm] || 1);
                    return color(val);
                })
                .style("stroke", "white")
                .style("stroke-width", 2)
                .style("opacity", 1)
                .on("mouseover", function (d) {
                    tip.show(d);
                    d3.select(this.parentNode.appendChild(this))
                        .style("stroke", "black");
                })
                .on("mouseout", function (d) {
                    tip.hide(d);
                    d3.select(this)
                        .style("stroke", "white");
                });
            
            // Create box for drop-down menu and legend
            var box = svg.append("div");
            // var box = svg.append("foreignObject").append("div");

            // Create drop-down menu
            // NOTE: These are currently sample items
            var menu = box.append("select")
            menu.append("option")
                .attr("value", "v1")
                .text("Value 1, Value 1");
            menu.append("option")
                .attr("value", "v2")
                .text("Value 2, Value 2");

            // Create legend
            var legend = box.append("div");
            // TODO: add legend items
        });
    }

    d3.json("rimap_config.json", function (config) {
        d3.json(config.file, function (dataset) {
            drawMap(config, dataset);
        });
    });
}();
