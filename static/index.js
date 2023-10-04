const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

if(urlParams.has('id')) {
    const id = urlParams.get('id');
    openSidebar(id);
}

function closeDiv(id) {
    let obj = String(id);
    document.getElementById(obj).style.display = "none";
};

function openSidebar(id) {
    document.getElementById('main').style.display = "flex";
    document.getElementById('sidebar').style.display = "flex";
    fetch('http://127.0.0.1:9092/get_place_photo')
        .then(response => response.json())
        .finally(() => {
            document.getElementById('locationImg').src = response;
        });
};

function openModal(id) {
    document.getElementById('graphModal').style.display = "flex";
    //fetch gráfico
};