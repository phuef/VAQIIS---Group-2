var mapOptions = {
    center: [51.9607, 7.6261],
    zoom: 13,
    zoomControl: true,
    dragging: true,
    attributionControl: true
};

var map = new L.map('map', mapOptions);

var osmlayer =  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data: &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

var rois = [];

$(document).ready(function () {
    let level = $("#slider").val();
    $("#sliderValue").text(level);
    $.ajax({
        type: "GET",
        url: "/getrois",
        success: function (response) {
            rois = response.data;
            console.log(rois);
            L.geoJson(rois[level]).addTo(map);
        }
    });
});

$(document).on('input', '#slider', function() {
    $("#sliderValue").text(this.value);
});