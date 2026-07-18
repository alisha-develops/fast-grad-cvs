const printBtn = document.getElementById("print-btn");
const closeBtn = document.getElementById("close-btn");

if (printBtn) {
    printBtn.addEventListener("click", function () {
        window.print();
    });
}

if (closeBtn) {
    closeBtn.addEventListener("click", function () {
        window.close();
    });
}