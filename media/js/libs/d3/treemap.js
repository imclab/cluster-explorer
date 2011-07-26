var w = 1140,
    h = 600,
    color = d3.scale.category20c();

var treemap = d3.layout.treemap()
   .size([w, h])
   .sticky(false)
   .children(function(d) { return d.clusters; })
   .value(function(d) { return d.count; })
   .round(true);

var div = d3.select("#chart").append("div")
   .style("position", "relative")
   .style("width", w + "px")
   .style("height", h + "px")
   .style("margin", "0 auto");

function drawIt(someData, hash) {
    if (hash.substr(-1) != "/") hash = hash+"/";
    
    var theThings = div.data([someData]).selectAll("div").data(treemap.nodes);
    //Update
    theThings
        .html(function(d, i) { return d.children ? null : "<a href='"+hash+(i-1)+"'>"+d.count+" documents</a>"; })
        .transition().duration(1500)
            .call(cell)
    //Enter
    theThings.enter()
        .append("div").attr("class","cell")
        .style("background", function(d) { return d.count ? color(d.count) : null; })
        .html(function(d, i) { return d.children ? null : "<a href='"+hash+(i-1)+"'>"+d.count+" documents</a>"; })
        .transition().duration(1500)
            .call(cell)
    
    //Exit
    theThings.exit()
        .transition().duration(1500)
            .style("width","0px")
            .remove();
}

function cell() {
  this
      .style("left", function(d) { return d.x + "px"; })
      .style("top", function(d) { return d.y + "px"; })
      .style("width", function(d) { return d.dx - 1 + "px"; })
      .style("height", function(d) { return d.dy - 1 + "px"; });
}
