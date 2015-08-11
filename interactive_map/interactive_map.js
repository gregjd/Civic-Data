// var w = 1500;
// var h = 900;
// var w = 960;
// var h = 500;
var w = 960;
var h = 900;

var projection = d3.geo.mercator()
                        .center([-71.4121134, 41.8148182]) // centered on Providence
                        // .center([-71.5064508, 41.5827282,]) // centered on RI
                        .scale(40000);

var path = d3.geo.path()
                    .projection(projection);
                 

var color = d3.scale.quantile()
// var color = d3.scale.quantize()
                    // .domain([0,120000])
                    // .domain([0,18000])
                    // .range(["rgb(237,248,233)","rgb(186,228,179)","rgb(116,196,118)","rgb(49,163,84)","rgb(0,109,44)"]);
                    .range(["#eff3ff","#bdd7e7","#6baed6","#3182bd","#08519c"]);
                    // ColorBrewer colors

var svg = d3.select("body")
            .append("svg")
            .attr("width", w)
            .attr("height", h);

// Load in muni data

var munis = {};

d3.csv("2013_5yr_pop_estimates.csv", function (pop_data) {

    for (var g = 0; g < pop_data.length; g++) {

        var loc = pop_data[g]["Municipality3"];

        if (!(loc in munis)) {
            munis[loc] = {}
        }

        munis[loc].pop_18_plus = parseFloat(pop_data[g]["Total 18+"]);
        munis[loc].pop_18_24 = parseFloat(pop_data[g]["Total 18-24"]);
    }

    console.log("done1");
});

d3.csv("Registered_voter_totals_Nov2014a.csv", function (voter_data) {

    for (var h = 0; h < voter_data.length; h++) {

        var loc = voter_data[h]["Muni"];
        
        munis[loc].voter_18_plus = parseFloat(voter_data[h]["Grand Total"]);
        munis[loc].voter_18_24 = parseFloat(voter_data[h]["18-24"]);
    }

    var muni_list = d3.entries(munis);
    // var getAges = function (d) { return d.value.voter_18_24; };
    console.log("done2");
    var getYouth = function (d) { 
        // console.log(d.properties.voter_18_24);
        // console.log(d.properties.pop_18_24);
        return (d.value.voter_18_24 / d.value.pop_18_24); };
    color.domain(d3.map(muni_list, getYouth).keys());
});


d3.json("ri_muni.geojson", function (geo_data) {

    for (var i = 0; i < geo_data.features.length; i++) {

        var muni_name = geo_data.features[i].properties.MUNI_CAPS;

        for (p in munis[muni_name]) {
            geo_data.features[i].properties[p] = munis[muni_name][p];
        }
    }
            
    svg.selectAll("path")
        .data(geo_data.features, function (d) { return d.properties.MUNI_CAPS; })
        .enter()
        .append("path")
        .attr("d", path)
        // .style('fill', '#ccc')
        .style("fill", function (d) {
            // var value = (d.properties.voter_18_24);
            var value = (d.properties.voter_18_24 / d.properties.pop_18_24);
            return color(value);
        })
        // .style('fill', function (d) {
        //     var value = d.properties.voter_18_24;
        //     return (value > 2000) ? 'black' : '#ccc';
        // })
        .style("stroke", "white")
        .style("stroke-width", 2);
});
