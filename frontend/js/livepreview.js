function getInputValue(fieldName) {
    const input = document.querySelector('[name="' + fieldName + '"]');
    if (input) {
        return input.value;
    }
    return "";
}

function updateText(fieldName, targetId) {
    const target = document.getElementById(targetId);
    if (target) {
        target.textContent = getInputValue(fieldName);
    }
}

function updateList(fieldName, targetId, splitBy) {
    const target = document.getElementById(targetId);
    if (!target) {
        return;
    }

    const value = getInputValue(fieldName);
    target.innerHTML = "";

    if (!value.trim()) {
        return;
    }

    const parts = value.split(splitBy);

    for (let i = 0; i < parts.length; i++) {
        const trimmed = parts[i].trim();
        if (trimmed) {
            const item = document.createElement("span");
            item.textContent = trimmed;
            item.style.marginRight = "6px";
            target.appendChild(item);
        }
    }
}

function updateCheckboxes(checkboxName, targetId) {
    const target = document.getElementById(targetId);
    if (!target) {
        return;
    }

    target.innerHTML = "";

    const checkedBoxes = document.querySelectorAll('input[name="' + checkboxName + '"]:checked');

    checkedBoxes.forEach(function (box) {
        const item = document.createElement("span");
        item.textContent = box.value;
        item.style.marginRight = "6px";
        target.appendChild(item);
    });
}

function updateFypSupervisor() {
    const supValue = getInputValue("fypSupervisor");
    const target = document.getElementById("cv-fyp-sup");

    if (!target) {
        return;
    }

    if (supValue.trim()) {
        target.textContent = "Supervisor: " + supValue;
    } else {
        target.textContent = "";
    }
}

function updatePreview() {
    updateText("fullName", "cv-name");
    updateText("degreeProgram", "cv-prog");
    updateText("studentId", "cv-id");
    updateText("email", "cv-email");
    updateText("phone", "cv-phone");
    updateText("cgpa", "cv-cgpa");
    updateText("linkedin", "cv-linkedin");
    updateText("portfolio", "cv-portfolio");
    updateText("objective", "cv-obj");
    updateText("education", "cv-edu");
    updateText("fypTitle", "cv-fyp-title");
    updateText("fypDesc", "cv-fyp-desc");
    updateText("internship", "cv-intern");
    updateText("leadership", "cv-leadership");

    updateFypSupervisor();

    updateList("electiveCourses", "cv-courses", ",");
    updateList("technicalSkills", "cv-skills", "\n");
    updateList("personalSkills", "cv-personal", ",");
    updateList("certifications", "cv-certs", "\n");
    updateList("honors", "cv-honors", "\n");

    updateCheckboxes("areasOfInterest", "cv-areas");
}

const allInputs = document.querySelectorAll("input, textarea, select");

allInputs.forEach(function (input) {
    input.addEventListener("input", updatePreview);
    input.addEventListener("change", updatePreview);
});

updatePreview();