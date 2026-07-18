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