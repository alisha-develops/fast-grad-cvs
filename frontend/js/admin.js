function openTrash() {
    document.getElementById("trashbackdrop").classList.add("open");
    document.getElementById("trashwindow").classList.add("open");
    loadTrash();
}
function closeTrash() {
    document.getElementById("trashbackdrop").classList.remove("open");
    document.getElementById("trashwindow").classList.remove("open");
}

async function loadTrash() {
    const response = await fetch("/admin/trash-data");
    const students = await response.json();

    const tbody = document.getElementById("trashtbody");
    const empty = document.getElementById("trashempty");
    const table = document.getElementById("trtable");

    tbody.innerHTML ="";

    if (students.length === 0) {
        table.style.display = "none";
        empty.style.display = "block";
        return;
    }

    table.style.display = "table";
    empty.style.display = "none";

    students.forEach(function (student) {
        const row = document.createElement("tr");

        const namepart = document.createElement("td");
        namepart.innerHTML = "<strong>" + student.full_name + "</strong>";
        row.appendChild(namepart);

        const idpart = document.createElement("td");
        idpart.textContent = student.student_id;
        row.appendChild(idpart);

        const programpart = document.createElement("td");
        if (student.degree_program) {
            programpart.textContent = student.degree_program;
        } else {
            programpart.textContent = "—";
        }
        row.appendChild(programpart);

        const emailpart = document.createElement("td");
        emailpart.textContent = student.email;
        row.appendChild(emailpart);

        const action = document.createElement("td");
        const restore = document.createElement("button");
        restore.textContent = "Restore";
        restore.className = "btn-preview";
        restore.onclick = function () {
            restoreStudent(student.id);
        };
        action.appendChild(restore);
        row.appendChild(action);

        tbody.appendChild(row);
    });
}

async function restoreStudent(dbId) {
    await fetch("/admin/restore/"+ dbId, { method: "POST" });
    loadTrash();
    window.location.reload();
}

document.getElementById("trashopen").addEventListener("click", openTrash);
document.getElementById("trclose").addEventListener("click", closeTrash);
document.getElementById("trashbackdrop").addEventListener("click", closeTrash);
let selectedIds = new Set();

function saveSelection() {
    const idArray = Array.from(selectedIds);
    sessionStorage.setItem("selectedCvIds", JSON.stringify(idArray));
}

function loadSelection() {
    const storedIds = sessionStorage.getItem("selectedCvIds");
    if (storedIds) {
        const idArray = JSON.parse(storedIds);
        for (let i = 0; i < idArray.length; i++) {
            selectedIds.add(idArray[i]);
        }
    }
}

function restoreCheckboxesOnPage() {
    const checkboxes = document.querySelectorAll(".student-checkbox");
    for (let i = 0; i < checkboxes.length; i++) {
        if (selectedIds.has(checkboxes[i].value)) {
            checkboxes[i].checked = true;
        } else {
            checkboxes[i].checked = false;
        }
    }
}

function updateMatchingButtonLabel() {
    const matchingButton = document.getElementById("select-all-matching-btn");
    if (selectedIds.size > 0) {
        matchingButton.textContent = "Deselect all";
    } else {
        matchingButton.textContent = "Select all matching students";
    }
}

function handleCheckboxChange(event) {
    const checkbox = event.target;
    const studentId = checkbox.value;

    if (checkbox.checked) {
        selectedIds.add(studentId);
    } else {
        selectedIds.delete(studentId);
    }

    saveSelection();
    updateExportButtonLabel();
    updateMatchingButtonLabel();
}

function handlePageSelectAllClick(event) {
    const isChecked = event.target.checked;
    const checkboxes = document.querySelectorAll(".student-checkbox");

    for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = isChecked;
        if (isChecked) {
            selectedIds.add(checkboxes[i].value);
        } else {
            selectedIds.delete(checkboxes[i].value);
        }
    }

    saveSelection();
    updateExportButtonLabel();
    updateMatchingButtonLabel();
}

async function handleSelectAllMatchingClick() {
    if (selectedIds.size > 0) {
        selectedIds.clear();
        restoreCheckboxesOnPage();
        document.querySelector(".select-all-checkbox").checked = false;
    } else {
        const searchValue = document.getElementById("search-input").value;
        const filterValue = document.getElementById("filter-select").value;
        const url = "/admin/matching-ids?search=" + encodeURIComponent(searchValue) + "&program=" + encodeURIComponent(filterValue);

        const response = await fetch(url);
        const idList = await response.json();

        for (let i = 0; i < idList.length; i++) {
            selectedIds.add(String(idList[i]));
        }

        restoreCheckboxesOnPage();
    }

    saveSelection();
    updateExportButtonLabel();
    updateMatchingButtonLabel();
}

function updateExportButtonLabel() {
    const exportButton = document.getElementById("export-button");
    exportButton.textContent = "Export " + selectedIds.size + " CVs";

    if (selectedIds.size > 0) {
        exportButton.classList.remove("export-button-hidden");
    } else {
        exportButton.classList.add("export-button-hidden");
    }
}

function handleExportClick() {
    if (selectedIds.size === 0) {
        alert("Please select at least one student.");
        return;
    }

    const idArray = Array.from(selectedIds);
    const idString = idArray.join(",");
    const exportUrl = "/admin/export-cvs?ids=" + encodeURIComponent(idString);

    window.open(exportUrl, "_blank");
    sessionStorage.removeItem("selectedCvIds");
}

loadSelection();
restoreCheckboxesOnPage();
updateExportButtonLabel();
updateMatchingButtonLabel();

const studentCheckboxes = document.querySelectorAll(".student-checkbox");
for (let i = 0; i < studentCheckboxes.length; i++) {
    studentCheckboxes[i].addEventListener("change", handleCheckboxChange);
}

document.querySelector(".select-all-checkbox").addEventListener("change", handlePageSelectAllClick);
document.getElementById("select-all-matching-btn").addEventListener("click", handleSelectAllMatchingClick);
document.getElementById("export-button").addEventListener("click", handleExportClick);