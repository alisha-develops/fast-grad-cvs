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

    document.querySelector('.steppage[data-step="' + currentStep + '"]').classList.remove("active");

    let newButton = document.querySelector('.steppage[data-step"' + currentStep + '"]')
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
    const page = document.querySelector('.steppage[data-step="' + step +'"]');
    let ok = true;
    page.querySelectorAll('[required]').forEach(el => {
        el.style.borderColor = '';
        if (!el.value.trim()) { 
            el.style.borderColor = '#c0392b'; 
            ok = false; 
        }
    });
    return ok;
}

async function submitForm() {
    const form = document.getElementById("cvform");
    const formData = new FormData(form);

    const data = {
        fullName: formData.get("fullName"),
        studentId: formData.get("studentId"),
        email: formData.get("email"),
        phone: formData.get("phone"),
        cgpa: formData.get("cgpa"),
        degreeProgram: formData.get("degreeProgram"),
        linkedin: formData.get("linkedin"),
        portfolio: formData.get("portfolio"),
        objective: formData.get("objective")
    };

    console.log(data);

    const response = await fetch("/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
        console.log("Submit failed:", result);
        return;
    }

    console.log("Saved:", result);
}