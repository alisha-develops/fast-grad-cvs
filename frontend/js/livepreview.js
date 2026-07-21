function updatePreview() {
    const inputsWithPreview = document.querySelectorAll("[data-preview]");

    inputsWithPreview.forEach(function (input) {
        const targetId = input.dataset.preview;
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            targetElement.textContent = input.value;
        }
    });
}

const allPreviewInputs = document.querySelectorAll("[data-preview]");

allPreviewInputs.forEach(function (input) {
    input.addEventListener("input", updatePreview);
});

updatePreview();