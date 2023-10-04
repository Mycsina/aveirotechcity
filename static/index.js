function closeDiv(id) {
    let obj = String(id);
    document.getElementById(obj).style.display = "none";
};

function openSidebar(id) {
    document.getElementById('sidebar').style.display = "flex";
    //fetch imagem google
};

function openModal(id) {
    document.getElementById('graphModal').style.display = "flex";
    //fetch gráfico
};

window.addEventListener("popstate", (event) => {
    console.log(
        `location: ${document.location}, state: ${JSON.stringify(event.state)}`,
    );
});