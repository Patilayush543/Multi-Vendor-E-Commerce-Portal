
/* ===============================
   SWITCH TABS (Login / Signup)
=============================== */
function showTab(tab) {
  document.getElementById('login').classList.remove('active');
  document.getElementById('signup').classList.remove('active');

  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

  document.getElementById(tab).classList.add('active');

  if (tab === 'login') {
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.body.classList.add("he-theme");
    document.body.classList.remove("she-theme");
  } else {
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
  }
}


/* ===============================
         LOGIN USER
=============================== */
function loginUser() {
  const username = document.getElementById("log-username").value.trim();
  const password = document.getElementById("log-password").value.trim();

  const savedUsers = JSON.parse(localStorage.getItem("users")) || [];

  const foundUser = savedUsers.find(
    user => user.username === username && user.password === password
  );

  if (!foundUser) {
    alert("Wrong username or password!");
    return;
  }

  localStorage.setItem("loggedUser", JSON.stringify(foundUser));

  alert("Login Successful!");
  window.location.href = "/";
}


/* ===============================
         REGISTER USER
=============================== */
function registerUser() {
  const username = document.getElementById("reg-username").value;
  const password = document.getElementById("reg-password").value;
  const gender = document.getElementById("reg-gender").value;

  let users = JSON.parse(localStorage.getItem("users")) || [];

  let newUser = {
    id: Date.now(),
    username,
    password,
    gender
  };

  users.push(newUser);
  localStorage.setItem("users", JSON.stringify(users));

  alert("User Registered Successfully!");
}


