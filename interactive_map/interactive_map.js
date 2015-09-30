rimap = function () {

    // // Load config object
    // var config = d3.json("rimap_config.json", function (c) { console.log(c); return c; });
    

    // // Source of dataset
    // var filename = "pop_and_reg_voters.json";
    // // var filename = config.filename;

    // Define the SVG's size
    var w = 960;
    var h = 900;

    // Set up projection
    var projection = d3.geo.mercator()
                            .center([-71.4121134, 41.8148182]) // centered on Providence
                            // .center([-71.5064508, 41.5827282,]) // centered on RI
                            .scale(40000);
    var path = d3.geo.path()
                        .projection(projection);
                     
    // Define color scale
    var color = d3.scale.threshold()
                        .domain([0.6, 0.8, 1])
                        .range(["#3366CC", "#0099CC", "#33CCCC", "#FF6600"]);

    // Converts a number to a percent, with a certain number of decimal places
    function toPct(value, decimal_places) {

        if (isNaN(value) || isNaN(decimal_places)) {
            throw "Parameters for toPct() must be numbers.";
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

    // var legend_items = map(color.domain(), toPct);

    // Define what goes in the box that appears when you hover over a municipality
    var tip = d3.tip()
                .attr("class", "d3-tip")
                .offset([-10, 0])
                .html(function (d) {
                    var calc = d.properties["Reg 18-24"] / d.properties["Pop Total 18-24"];
                    var num = toPct(calc, 2);
                    var num_color = ((calc > 1) ? "red" : "green");
                    var city = d.properties.MUNI;
                    return "<strong>" + city + "</strong><br>Percent of youth registered: <span style='color:" 
                        + num_color + "'>" + num + "</span>";
                });

    // Create SVG
    var svg = d3.select("body")
                .append("svg")
                .attr("width", w)
                .attr("height", h);

    svg.call(tip);

    // Loads the geodata and draws the map
    function drawMap(dataset) {

        // Open the file with municipality shapes
        d3.json("ri_muni.geojson", function (geo_data) {

            // Attach our data as properties of the municipality shapes
            for (var i = 0; i < geo_data.features.length; i++) {

                var muni_name = geo_data.features[i].properties.MUNI_CAPS;

                for (p in dataset[muni_name]) {
                    geo_data.features[i].properties[p] = dataset[muni_name][p];
                }
            }
            
            // Draw the map    
            svg.selectAll("path")
                .data(geo_data.features, function (d) { return d.properties.MUNI_CAPS; })
                .enter()
                .append("path")
                .attr("d", path)
                .style("fill", function (d) {
                    var val = (d.properties["Reg 18-24"] / d.properties["Pop Total 18-24"]);
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

        var data_source = config.file;

        // Read in the data and draw the map
        d3.json(data_source, function (dataset) {

            drawMap(dataset);

            // // Open the file with municipality shapes
            // d3.json("ri_muni.geojson", function (geo_data) {

            //     // Attach our data as properties of the municipality shapes
            //     for (var i = 0; i < geo_data.features.length; i++) {

            //         var muni_name = geo_data.features[i].properties.MUNI_CAPS;

            //         for (p in dataset[muni_name]) {
            //             geo_data.features[i].properties[p] = dataset[muni_name][p];
            //         }
            //     }
                
            //     // Draw the map    
            //     svg.selectAll("path")
            //         .data(geo_data.features, function (d) { return d.properties.MUNI_CAPS; })
            //         .enter()
            //         .append("path")
            //         .attr("d", path)
            //         .style("fill", function (d) {
            //             var val = (d.properties["Reg 18-24"] / d.properties["Pop Total 18-24"]);
            //             return color(val);
            //         })
            //         .style("stroke", "white")
            //         .style("stroke-width", 2)
            //         .style("opacity", 1)
            //         .on("mouseover", function (d) {
            //             tip.show(d);
            //             d3.select(this.parentNode.appendChild(this))
            //                 .style("stroke", "black");
            //         })
            //         .on("mouseout", function (d) {
            //             tip.hide(d);
            //             d3.select(this)
            //                 .style("stroke", "white");
            //         });
                
            //     // Create box for drop-down menu and legend
            //     var box = svg.append("div");
            //     // var box = svg.append("foreignObject").append("div");

            //     // Create drop-down menu
            //     // NOTE: These are currently sample items
            //     var menu = box.append("select")
            //     menu.append("option")
            //         .attr("value", "v1")
            //         .text("Value 1, Value 1");
            //     menu.append("option")
            //         .attr("value", "v2")
            //         .text("Value 2, Value 2");

            //     // Create legend
            //     var legend = box.append("div");
            //     // TODO: add legend items
            // });
        });
    });
}();
