if (window.location.search.indexOf("autoprint=1") !== -1) {
    window.addEventListener("load", function () {
        window.print();
    });
}

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
    const response = await fetch("/admin/trashdata");
    const students = await response.json();

    const tbody = document.getElementById("trashtbody");
    const empty = document.getElementById("trashempty");
    const table = document.getElementById("trtable");

    tbody.innerHTML ="";

    if (students.length === 0) {
        table.style.display = "none";
        emptyMsg.style.display = "block";
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
    await fetch("/admin/restore"+ dbId, { method: "POST" });
    loadTrash();
    window.location.reload();
}

document.getElementById("trashopen").addEventListener("click", openTrash);
document.getElementById("trclose").addEventListener("click", closeTrash);
document.getElementById("trashbackdrop").addEventListener("click", closeTrash);