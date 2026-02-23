

console.log("script.js loaded");

// ONLY FOR HOMEPAGE
const btnHe = document.querySelector(".btnHe");
const btnShe = document.querySelector(".btnShe");
const body = document.body;

if (btnHe && btnShe) {
    btnHe.addEventListener("click", () => {
        body.className = "he-theme";
    });

    btnShe.addEventListener("click", () => {
        body.className = "she-theme";
    });
}
