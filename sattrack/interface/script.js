$(document).ready(function() {
	console.log("Document Loaded");
	$svg = d3.select("#svg").append("svg")
    .attr("width", width)
    .attr("height", height);
	draw();
	$lon = 0;
	$lat = 0;
	$az = 0;
	$alt = 0;
	$time = "";
	$lonlabel = d3.select("#lon");
	$latlabel = d3.select("#lat");
	$azilabel = d3.select("#azi");
	$altlabel = d3.select("#alt");
	$timelabel = d3.select("#time");
	getStatus();
	$svg.selectAll("circle")
		.data([[$lon, $lat]]).enter()
		.append("circle")
		.attr("cx", function (d) { return projection(d)[0]; })
		.attr("cy", function (d) { return projection(d)[1]; })
		.attr("r", "8px")
		.attr("fill", "red")
		.attr("class", "satellite");
});

var width = $(window).height(),
    height = $(window).height();
	console.log(width)

var projection = d3.geo.orthographic()
    .scale(300)
    .translate([width / 2, height / 2])
    .clipAngle(90)
    .precision(.1);

var path = d3.geo.path()
    .projection(projection);

var graticule = d3.geo.graticule();

var draw = function() {
	
	
	$svg.append("defs").append("path")
		.datum({type: "Sphere"})
		.attr("id", "sphere")
		.attr("d", path);

	$svg.append("use")
		.attr("class", "stroke")
		.attr("xlink:href", "#sphere");

	$svg.append("use")
		.attr("class", "fill")
		.attr("xlink:href", "#sphere");

	$svg.append("path")
		.datum(graticule)
		.attr("class", "graticule")
		.attr("d", path);

	d3.json("world-50m.json", function(error, world) {
	  if (error) throw error;
	  console.log("World loaded");

	 $svg.insert("path", ".graticule")
		  .datum(topojson.feature(world, world.objects.land))
		  .attr("class", "land")
		  .attr("d", path);

	  $svg.insert("path", ".graticule")
		  .datum(topojson.mesh(world, world.objects.countries, function(a, b) { return a !== b; }))
		  .attr("class", "boundary")
		  .attr("d", path);
	});

	d3.select(self.frameElement).style("height", height + "px");
};

function getStatus(){
	$.getJSON(window.location.href + '?status', function(data) {
			$lon = parseFloat(data.lon);
			$lat = parseFloat(data.lat);
			$az = parseFloat(data.az);
			$alt = parseFloat(data.alt);
			$time = data.time;
			$lonlabel.text($lon.toFixed(3));
			$latlabel.text($lat.toFixed(3));
			$azilabel.text($az.toFixed(3));
			$altlabel.text($alt.toFixed(3));
			$timelabel.text($time + " UTC");
			// console.log(data);
			rotateProjection($lat, $lon);
			plotPoints(parseFloat($lat), parseFloat($lon));
			setTimeout(getStatus, 1000*data.interval);
	})
}

function rotateProjection(lat, lon) {
		projection.rotate([-lon, -lat]);
		$svg.selectAll("path").attr("d", path);
}

function plotPoints(lat, lon) {
	$svg.selectAll(".satellite")
		.attr("cx", function () { return projection([lon, lat])[0]; })
		.attr("cy", function () { return projection([lon, lat])[1]; })	;
}
