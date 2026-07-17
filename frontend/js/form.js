async function submitForm(){
    const fullName = document.querySelector("[name='fullName']").value;
    const response = await fetch("/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            fullName: fullName
        })
    });

    const result = await response.json();
    console.log(result);
}

