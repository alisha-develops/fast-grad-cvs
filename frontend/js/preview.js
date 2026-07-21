if (window.location.search.indexOf("autoprint=1") !== -1) {
    window.addEventListener("load", function () {
        setTimeout(function () {
            window.print();
        }, 300);
    });
}

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