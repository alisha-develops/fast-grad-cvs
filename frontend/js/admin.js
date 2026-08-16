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

function openSync() {
    document.getElementById("syncbackdrop").classList.add("open");
    document.getElementById("syncwindow").classList.add("open");
    runSyncPreview();
}

function closeSync() {
    document.getElementById("syncbackdrop").classList.remove("open");
    document.getElementById("syncwindow").classList.remove("open");
}

let bufferedNewLines = [];
let bufferedUpdatedLines = [];
let bufferedSummary = null;

async function runSyncPreview() {
    document.getElementById("syncloading").classList.remove("hidden");
    document.getElementById("syncsummaryonly").classList.add("hidden");
    document.getElementById("syncresults").classList.add("hidden");
    document.getElementById("syncdone").classList.add("hidden");

    bufferedNewLines = [];
    bufferedUpdatedLines = [];
    bufferedSummary = null;

    let processedCount = 0;
    const syncLoadingDiv = document.getElementById("syncloading");

    const response = await fetch("/admin/sync-preview", { method: "POST" });
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let leftover = "";

    while (true) {
        const chunk = await reader.read();
        if (chunk.done) {
            break;
        }

        const text = leftover + decoder.decode(chunk.value, { stream: true });
        const lines = text.split("\n");
        leftover = lines.pop();

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line === "") {
                continue;
            }

            if (line.indexOf("SUMMARY:") === 0) {
                bufferedSummary = JSON.parse(line.substring(8));
                continue;
            }

            if (line.indexOf("NEW FROM V1:") === 0) {
                bufferedNewLines.push(line);
                processedCount = processedCount + 1;
                syncLoadingDiv.textContent = "Checking submissions... (" + processedCount + " found so far)";
            } else if (line.indexOf("UPDATING:") === 0) {
                bufferedUpdatedLines.push(line);
                processedCount = processedCount + 1;
                syncLoadingDiv.textContent = "Checking submissions... (" + processedCount + " found so far)";
            } else if (line.indexOf("checking existing students") === 0) {
                syncLoadingDiv.textContent = line;
            } else if (line.indexOf("found") === 0) {
                syncLoadingDiv.textContent = line;
            } else if (line.indexOf("checking...") === 0) {
                syncLoadingDiv.textContent = line;
            }
            
        }
    }

    document.getElementById("syncloading").classList.add("hidden");

    if (bufferedSummary) {
        const totalPending = bufferedSummary.new_count + bufferedSummary.updated_count;
        const summaryOnlyText = document.getElementById("syncsummaryonlytext");

        if (totalPending > 0) {
            summaryOnlyText.textContent = totalPending + " submission" + (totalPending === 1 ? " is" : "s are") + " not synced yet.";
            document.getElementById("syncsummaryonly").classList.remove("hidden");
        } else {
            document.getElementById("syncdone").classList.remove("hidden");
            document.getElementById("syncdone").textContent = "Everything is already up to date.";
        }
    }
}

function revealSyncDetails() {
    document.getElementById("syncsummaryonly").classList.add("hidden");
    document.getElementById("syncresults").classList.remove("hidden");

    const newListDiv = document.getElementById("syncnewlist");
    const updatedListDiv = document.getElementById("syncupdatedlist");
    newListDiv.innerHTML = "";
    updatedListDiv.innerHTML = "";

    for (let i = 0; i < bufferedNewLines.length; i++) {
        const entry = document.createElement("p");
        entry.textContent = bufferedNewLines[i];
        newListDiv.appendChild(entry);
    }

    for (let i = 0; i < bufferedUpdatedLines.length; i++) {
        const entry = document.createElement("p");
        entry.textContent = bufferedUpdatedLines[i];
        updatedListDiv.appendChild(entry);
    }

    const summaryText = document.getElementById("syncsummary");
    summaryText.textContent = bufferedSummary.new_count + " new students will be synced, " + bufferedSummary.updated_count + " will get their recent resubmission synced, " + bufferedSummary.unchanged_count + " are already up to date, " + bufferedSummary.error_count + " errors";

    document.getElementById("syncconfirmbtn").classList.remove("hidden");
}

async function runSyncConfirm() {
    document.getElementById("syncconfirmbtn").classList.add("hidden");

    const summaryText = document.getElementById("syncsummary");
    const newListDiv = document.getElementById("syncnewlist");
    const updatedListDiv = document.getElementById("syncupdatedlist");
    newListDiv.innerHTML = "";
    updatedListDiv.innerHTML = "";
    summaryText.textContent = "Starting sync...";

    const response = await fetch("/admin/sync-confirm", { method: "POST" });
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let leftover = "";
    let finalSummary = null;

    while (true) {
        const chunk = await reader.read();
        if (chunk.done) {
            break;
        }

        const text = leftover + decoder.decode(chunk.value, { stream: true });
        const lines = text.split("\n");
        leftover = lines.pop();

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line === "") {
                continue;
            }

            if (line.indexOf("SUMMARY:") === 0) {
                finalSummary = JSON.parse(line.substring(8));
                continue;
            }

            if (line.indexOf("NEW FROM V1:") === 0) {
                const entry = document.createElement("p");
                entry.textContent = line;
                newListDiv.appendChild(entry);
            } else if (line.indexOf("UPDATING:") === 0) {
                const entry = document.createElement("p");
                entry.textContent = line;
                updatedListDiv.appendChild(entry);
            } else {
                summaryText.textContent = line;
            }
        }
    }

    const doneDiv = document.getElementById("syncdone");
    doneDiv.classList.remove("hidden");
    if (finalSummary) {
        doneDiv.textContent = "Done! " + finalSummary.new_count + " new students synced, " + finalSummary.updated_count + " recent resubmissions synced.";
    } else {
        doneDiv.textContent = "Done!";
    }

    setTimeout(function () {
        window.location.reload();
    }, 2000);
}

document.getElementById("syncopen").addEventListener("click", openSync);
document.getElementById("syncclose").addEventListener("click", closeSync);
document.getElementById("syncbackdrop").addEventListener("click", closeSync);
document.getElementById("syncconfirmbtn").addEventListener("click", runSyncConfirm);
document.getElementById("syncnowbtn").addEventListener("click", revealSyncDetails);