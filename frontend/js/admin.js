function openTrash() {
    document.getElementById("trashbackdrop").classList.add("open");
    document.getElementById("trashwindow").classList.add("open");
    loadTrash();
}
function closeTrash() {
    document.getElementById("trashbackdrop").classList.remove("open");
    document.getElementById("trashwindow").classList.remove("open");
}

