var mapOptions = {
	center: [51.96,7.60],
	zoom: 13,
	zoomControl: false,
	dragging: true,
	attributionControl: true
};

var map = new L.map('map', mapOptions);

var osmlayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: 'Map data: &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
	maxZoom: 18
}).addTo(map);

var rois = {};
var dates = [];

var LayerGroupRois = new L.LayerGroup();
LayerGroupRois.addTo(map);
var routeLayer = new L.LayerGroup();
routeLayer.addTo(map);
var markerLayer = new L.LayerGroup();
markerLayer.addTo(map);

function addToMap(geojson, LayerGroup, color) {
	LayerGroup.clearLayers();
	let geometry = L.geoJson(geojson, {
		"color": color
	});
	LayerGroup.addLayer(geometry);
}

$(document).ready(function () {
	let level = $("#levelslider").val();
	$("#levelsliderValue").text(level);
	$.ajax({
		type: "GET",
		url: "/getrois",
		success: function (response) {
			rois = response.data;
			console.log(rois);
			
			dates = Object.keys(rois);
			console.log(dates);
			
			$("#timeslider").attr({
				max: dates.length-1
			});
			$("#timesliderValue").text(dates[0]);
			addToMap(rois[dates[0]][level], LayerGroupRois, "#c82b00");
		}
	});
});

$(document).on('input', '#levelslider', function () {
	$("#levelsliderValue").text(this.value);
	let level = $(this).val();
	let time = $("#timeslider").val();
	
	addToMap(rois[dates[time]][level], LayerGroupRois, "#c82b00");
});
$(document).on('input', '#timeslider', function () {
	$("#timesliderValue").text(dates[this.value]);
	let time = $(this).val();
	let level = $("#levelslider").val();
	
	addToMap(rois[dates[time]][level], LayerGroupRois, "#c82b00");
});



function createButton(label, container, id) {
	var btn = L.DomUtil.create('button', '', container);
	btn.setAttribute('type', 'button');
	btn.setAttribute('class', 'button')
	btn.setAttribute('id', id)
	btn.innerHTML = label;
	return btn;
}

map.on('click', function (e) {
	var container = L.DomUtil.create('div'),
		startBtn = createButton('Start', container),
		destBtn = createButton('Destination', container);

	L.popup()
		.setContent(container)
		.setLatLng(e.latlng)
		.openOn(map);

	L.DomEvent.on(startBtn, 'click', function () {
		setAddress(e, "#start");
		map.closePopup();
	});

	L.DomEvent.on(destBtn, 'click', function () {
		setAddress(e, "#finish");
		map.closePopup();
	});
});

function setAddress(pos, selector) {
	let input = pos.latlng;
	$.ajax({
		type: "GET",
		url: "https://api.openrouteservice.org/geocode/reverse?api_key=5b3ce3597851110001cf6248c4fd9635cd434b46bd42e27e08eae56b&point.lon=" + input.lng + "&point.lat=" + input.lat,
		success: function (response) {
			response.features.forEach(element => {
				console.log(element.properties.label);
			});

			let address = response.features[0].properties.street;
			if (address == null) {
				$(selector).val(`${input.lat}, ${input.lng}`);

			} else {
				$(selector).val(response.features[0].properties.label);
			}
		},
		error: function (err) {
			console.log(err);
			return `${input.lat}, ${input.lng}`;
		}
	});
}

$(document).ready(function () {
	$("#submit").click(function (e) {
		let start = $("#start").val();
		let finish = $("#finish").val();
		let profile = $("input[name='transport']:checked").val();


		if (start != null && finish != null) {
			var toCoordinates = function (coordString) {
				let sep = coordString.split(",");
				let lat = parseFloat(sep[0]);
				let lng = parseFloat(sep[1]);

				return [lng, lat];
			}

			if (isNaN(start.split(",")[0])) {
				$.ajax({
					type: "GET",
					url: "https://api.openrouteservice.org/geocode/search?api_key=5b3ce3597851110001cf6248c4fd9635cd434b46bd42e27e08eae56b&text=" + start,
					async: false,
					success: function (response) {
						start = response.features[0].geometry.coordinates;
					}
				});
			} else {
				start = toCoordinates(start);
			}
			if (isNaN(finish.split(",")[0])) {
				$.ajax({
					type: "GET",
					url: "https://api.openrouteservice.org/geocode/search?api_key=5b3ce3597851110001cf6248c4fd9635cd434b46bd42e27e08eae56b&text=" + finish,
					async: false,
					success: function (response) {
						finish = response.features[0].geometry.coordinates;
					}
				});
			} else {
				finish = toCoordinates(finish);
			}
			let level = $("#levelslider").val();
			let data = {
				"coordinates": [
					start, finish
				],
				"options": {
					"avoid_polygons": rois[level]
				}
			}
			console.log(data);

			$.ajax({
				type: "POST",
				url: "https://api.openrouteservice.org/v2/directions/" + profile + "/geojson",
				data: JSON.stringify(data),
				contentType: "application/json; charset=utf-8",
				headers: {
					"Authorization": "5b3ce3597851110001cf6248c4fd9635cd434b46bd42e27e08eae56b"
				},
				success: function (response) {
					console.log(response);
					addRouteFeatures(response);
				},
				error: function (err) {
					console.log(err);
					// addRouteFeatures(response.responseText);
					$("#info").show();
					$("#info").text(err.responseText);
					$("#info").delay("10000").fadeOut();
				}
			});
		} else {
			alert("please enter valid start and destination");
		}
	});
});

function addRouteFeatures(geojson) {
	addToMap(geojson.features[0], routeLayer, "#00c800");

	markerLayer.clearLayers();
	var addNavInfo = function (geojson) {
		let segments = geojson.properties.segments
		var list = "";
		var swapCoord = function (coord) {
			return [coord[1], coord[0]];
		};
		segments[0].steps.forEach(element => {
			let listObj = "<li class='listObj'>" + element.instruction + ": → "+ element.distance +"m</li>";
			list += listObj;
			
			let marker = L.marker(swapCoord(geojson.geometry.coordinates[element.way_points[0]]), {"riseOnHover": true});
			let popupText = "<table><tr><td>Instruction:</td><td>" + element.instruction + "</td></tr><tr><td>Distance to next point:<td>" + element.distance + "m</td></tr></table>";
			marker.bindPopup(popupText);
			markerLayer.addLayer(marker);
		});
		$("#navList").html(list);
		$("#navigationInfo").show();
	};
	addNavInfo(geojson.features[0]);

	let bbox = [
		[geojson.bbox[1], geojson.bbox[0]],
		[geojson.bbox[3], geojson.bbox[2]]
	];
	map.flyToBounds(bbox);

}