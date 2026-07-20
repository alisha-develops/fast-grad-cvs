let currentStep =1;
function goStep(step) {
    if(step > currentStep && !validateStep(currentStep)) {
        return;
    }

    document.querySelector('.steppage[data-step="' + currentStep + '"]').classList.remove("active");

    let currentButton = document.querySelector('.step[data-step="' + currentStep + '"]')
    currentButton.classList.remove("active");
    currentButton.classList.add("done");

    currentStep = step;

    document.querySelector('.steppage[data-step="' + currentStep + '"]').classList.add("active");

    let newButton = document.querySelector('.step[data-step="' + currentStep + '"]')
    newButton.classList.remove("done");
    newButton.classList.add("active");

    let progress = (currentStep / 5) * 100;
    document.getElementById("progress-fill").style.width = progress + "%";

    document.querySelector(".formpanel").scrollTo({
        top: 0,
        behavior: "smooth"
    });

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

function validateStep(step) {
    const page = document.querySelector('.steppage[data-step="' + step + '"]');
    let ok = true;

    const requiredFields = page.querySelectorAll("[required]");
    requiredFields.forEach(function (el) {
        el.style.borderColor = "";
        if (!el.value.trim()) {
            el.style.borderColor = "#c0392b";
            ok = false;
        }
    });

    return ok;
}

// function previewUpdates(){
//     const allFields = document.querySelectorAll("[name]");
//     allFields.forEach(function(el) {
//         el.addEventListener("input", refreshPreview);
//         el.addEventListener("change", refreshPreview);
//     })
// }

function markCheckboxes (){
    const areasGroup = document.getElementById('areas-group');
    const checkboxes = areasGroup.querySelectorAll("input");

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            const checkedBoxes = areasGroup.querySelectorAll("input:checked");
            if (checkedBoxes.length > 3) {
                checkbox.checked = false;
                return;
            }
            if (checkbox.checked) {
                checkbox.parentElement.classList.add("checked");
            } else {
                checkbox.parentElement.classList.remove("checked");
            }
            refreshPreview();
        });
    });
}

let uploadedPhotoUrl = null;

function photoUpload (){
    const photoInput = document.getElementById("photoinput");

    photoInput.addEventListener("change", async function (){
        const file = this.files[0];
        if (!file) {
            return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            const photoPreview = document.getElementById("photo-preview");
            photoPreview.innerHTML = '<img src="' + event.target.result + '"/>';
        };
        reader.readAsDataURL(file);

        const uploadData = new FormData();
        uploadData.append("photo", file);

        try {
            const response = await fetch("/upload-photo", {
                method: "POST",
                body: uploadData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error("Upload failed");
            }

            uploadedPhotoUrl = result.url;
        } catch (err) {
            alert("Photo upload failed: " + err.message);
            uploadedPhotoUrl = null;
        }
    })
}

function collectFormData() {
    const form = document.getElementById("cvform");
    const formData = new FormData(form);
    const data = {};

    formData.forEach(function(value, key) {
        if (key !== "areasOfInterest") {
            data[key] = value;
        }
    });

    const checkedAreas = document.querySelectorAll('input[name="areasOfInterest"]:checked');
    const areaValues = [];
    checkedAreas.forEach(function(box){
        areaValues.push(box.value);
    });
    data.areasOfInterest = areaValues.join(", ");

    data.photoUrl = uploadedPhotoUrl;

    return data;
}

async function submitForm() {

    if (!validateStep(5)) {
        return;
    }

    let submit = document.getElementById("submit");
    submit.disabled = true;
    submit.textContent = "Submitting...";

    let data = collectFormData();

    try {

        let response = await fetch("/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        let result = await response.json();

        if (response.ok) {

            document.getElementById("cvform").style.display = "none";
            document.querySelector(".stepbar").style.display = "none";
            document.querySelector(".progress").style.display = "none";

            document.getElementById("success-name").textContent = data.fullName;
            document.getElementById("success").style.display = "block";

        } else {

            document.getElementById("form-error").textContent = "Submission failed.";
            document.getElementById("form-error").style.display = "block";

            submit.disabled = false;
            submit.textContent = "Submit Profile ✓";
        }

    } catch (error) {

        document.getElementById("form-error").textContent = "Something went wrong.";
        document.getElementById("form-error").style.display = "block";

        submit.disabled = false;
        submit.textContent = "Submit Profile ✓";
    }
}

// previewUpdates();
markCheckboxes();
photoUpload();
// refreshPreview();