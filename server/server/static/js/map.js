var mapOptions = {
    center: [64.00, 26.00],
    zoom: 7,
    zoomControl: false,
    dragging: true,
    attributionControl: true
};

var map = new L.map('map', mapOptions);

var osmlayer =  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data: &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

var rois = [];
var layerGroup = new L.LayerGroup();
layerGroup.addTo(map);

function addToMap(roiLevel) {
    layerGroup.clearLayers();
    let roi = L.geoJson(roiLevel);
    layerGroup.addLayer(roi);
}

$(document).ready(function () {
    let level = $("#slider").val();
    $("#sliderValue").text(level);
    $.ajax({
        type: "GET",
        url: "/getrois",
        success: function (response) {
            rois = response.data;
            addToMap(rois[level])
        }
    });
});

$(document).on('input', '#slider', function() {
    $("#sliderValue").text(this.value);
    let level = $(this).val();
    addToMap(rois[level]);
});
