mapboxgl.accessToken = "pk.eyJ1IjoibXljc2luYSIsImEiOiJja3lvY3E4ZjMwZzkzMm5veWNmc2RiOTJwIn0.MKFG5e9EjMVfKq9WerC7Mg";
const map = new mapboxgl.Map({
    style: "mapbox://styles/mapbox/satellite-streets-v12",
    center: [{{ lng }}, {{ lat }}],
    zoom: 17,
    pitch: 70,
    bearing: -90,
    container: 'map',
    antialias: true
});

map.on('style.load', () => {
    // Insert the layer beneath any symbol layer.
    const layers = map.getStyle().layers;
    const labelLayerId = layers.find(
        (layer) => layer.type === 'symbol' && layer.layout['text-field']
    ).id;

    // The 'building' layer in the Mapbox Streets
    // vector tileset contains building height data
    // from OpenStreetMap.
    map.addLayer({
        'id': 'add-3d-buildings',
        'source': 'composite',
        'source-layer': 'building',
        'filter': ['==', 'extrude', 'true'],
        'type': 'fill-extrusion',
        'minzoom': 15,
        'paint': {
        'fill-extrusion-color': '#9b8145',

        // Use an 'interpolate' expression to
        // add a smooth transition effect to
        // the buildings as the user zooms in.
        'fill-extrusion-height': [
            'interpolate',
            ['linear'],
            ['zoom'],
            15,
            0,
            15.05,
            ['get', 'height']
        ],
        'fill-extrusion-base': [
            'interpolate',
            ['linear'],
            ['zoom'],
            15,
            0,
            15.05,
            ['get', 'min_height']
        ],
        'fill-extrusion-opacity': 0.90
        }
    },
    labelLayerId
    );
});

let colors = ['#91822e', '#2e7b2e', '#7474f0', '#ef4562', '#594c04', '#10e010', '#3d3d82', '#e60909'];
let colorIndex = 0;
let markers = [];
let counter = 0;

function loggg() {
    markers.forEach(marker => {
        console.log(marker);
    })
}

fetch('http://127.0.0.1:9092/get_locations')
    .then(response => response.json())
    .then(data => {
        data.forEach(item => {
            let marker = new mapboxgl.Marker({color: colors[colorIndex++ % colors.length]})
                .setLngLat([item.longitude, item.latitude])
                .addTo(map);
            marker["id"] = counter++;
            markers.push(
                marker
            );
        });
    })
    .finally(() => {
        markers.forEach(marker => {
            marker.getElement().addEventListener("click", () => {
                console.log(marker['id']);
            })
        })
    });

function closeDiv(id) {
    let obj = JSON.stringify(id);
    document.getElementById(obj).style.display = "none";
};