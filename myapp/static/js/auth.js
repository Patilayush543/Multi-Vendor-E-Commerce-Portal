// TAB SWITCHING
function openTab(formId) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.form').forEach(f => f.classList.remove('active'));

    // Activate clicked tab
    event.target.classList.add('active');

    // Show selected form
    document.getElementById(formId).classList.add('active');
}

// CLOSE PAGE (X button)
function closePage() {
    window.location.href = "/";   // index page par bhej dega
}



function openTab(tab) {
    document.querySelectorAll(".form").forEach(f => f.classList.remove("active"));
    document.getElementById(tab).classList.add("active");

    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    event.target.classList.add("active");
}





function getCSRF() {
    return document.cookie.split('csrftoken=')[1];
}


/* LOGIN */
function clearLoginErrors() {
    document.getElementById("err-log-email").innerText = "";
    document.getElementById("err-log-password").innerText = "";
}

function loginUser() {
    clearLoginErrors();

    let email = document.getElementById("log-email").value.trim();
    let password = document.getElementById("log-password").value.trim();

    let valid = true;

    if (!email.includes("@gmail.com")) {
        document.getElementById("err-log-email").innerText = "Enter your Gmail!";
        valid = false;
    }

    if (password === "") {
        document.getElementById("err-log-password").innerText = "Password required!";
        valid = false;
    }

    if (!valid) return;

    fetch("/login-user/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRF(),
        },
        body: `email=${email}&password=${password}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "error") {
            document.getElementById("err-log-email").innerText = data.msg;
        } else {
            window.location.href = "/";
        }
    });
}



/* SIGNUP */
function clearSignupErrors() {
    document.getElementById("err-email").innerText = "";
    document.getElementById("err-password").innerText = "";
    document.getElementById("err-repass").innerText = "";
}

function registerUser() {
    clearSignupErrors();

    let email = document.getElementById("reg-email").value.trim();
    let password = document.getElementById("reg-password").value.trim();
    let repassword = document.getElementById("reg-repassword").value.trim();
    let gender = document.getElementById("reg-gender").value;

    let valid = true;

    // Gmail check
    const gmailPattern = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;
    if (!gmailPattern.test(email)) {
        document.getElementById("err-email").innerText = "Enter a valid Gmail only!";
        valid = false;
    }

    // Strong password
    const strongPass = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*<>?|])[A-Za-z\d!@#$%^&*<>?|]{8,}$/;
    if (!strongPass.test(password)) {
        document.getElementById("err-password").innerText =
            "Min 8 chars, uppercase, lowercase, number & special char required.";
        valid = false;
    }

    // Password match
    if (password !== repassword) {
        document.getElementById("err-repass").innerText = "Passwords do not match!";
        valid = false;
    }

    if (!valid) return; // STOP HERE IF ERRORS

    // Send to backend
    fetch("/register-user/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRF(),
        },
        body: `email=${email}&password=${password}&gender=${gender}`
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === "error") {
                document.getElementById("err-email").innerText = data.msg;
            } else {
                alert("Signup successful!");
            }
        });
}
