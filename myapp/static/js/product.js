console.log("product.js ready");

// Get URL like /product/she/12/
const pathParts = window.location.pathname.split("/").filter(Boolean);

// pathParts = ["product", "she", "12"]
const cat = pathParts[1]; 
const id = pathParts[2];

console.log("CAT:", cat, "ID:", id);

let product;

if (cat === "he") {
    const he_cloths = [...heData_trend, ...heData_MS];
    product = he_cloths.find(p => p.id == id);
} 
else if (cat === "she") {
    const she_cloths = [...sheData_trend, ...sheData_MS];
    product = she_cloths.find(p => p.id == id);
}

const box = document.getElementById("productDetails");

if (!product) {
    box.innerHTML = "<h1>Product Not Found</h1>";
} else {
    box.innerHTML = `
        <img src="${product.img}">
        <h1>${product.title}</h1>
        <h2>${product.brand}</h2>

        <div>
            <span class="price">${product.price}</span>
            <span class="old-price">${product.oldPrice}</span>
        </div>

        <p>${product.description || "No description available"}</p>

        <a class="buy-btn" href="${product.link}" target="_blank">Buy Now</a>
    `;
}
