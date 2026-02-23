const feedbacks = [
    {
        img: "/static/image/user1.jpg",
        name: "Rohit Sharma",
        rating: 5,
        feedback: "Bhai product mast quality ka hai, totally worth it!"
    },
    {
        img: "/static/image/user2.jpg",
        name: "Anjali Verma",
        rating: 4,
        feedback: "Delivery fast thi, design bhi achha hai."
    },
    {
        img: "/static/image/user3.jpg",
        name: "Amit Singh",
        rating: 5,
        feedback: "Service top-notch! Highly recommended."
    },
    {
        img: "/static/image/user4.jpg",
        name: "Rohit Sharma",
        rating: 5,
        feedback: "Bhai product mast quality ka hai, totally worth it!"
    },
    {
        img: "/static/image/user2.jpg",
        name: "Anjali Verma",
        rating: 4,
        feedback: "Delivery fast thi, design bhi achha hai."
    },
    {
        img: "/static/image/user3.jpg",
        name: "Amit Singh",
        rating: 5,
        feedback: "Service top-notch! Highly recommended."
    }
];


const feedbackContainer = document.getElementById("feedback-container");
const track = document.querySelector(".feedback-track");
const dotsContainer = document.querySelector(".fb-dots");


let index = 0;


feedbacks.forEach((item,i)=> {
    const card = document.createElement("div");
    card.className = "feedback-card";

    const left = document.createElement("div");
    left.className = "left-circle";

    const img = document.createElement("img");
    img.src = item.img;

    const right = document.createElement("div");
    right.className = "right-box";

    const stars = document.createElement("div");
    stars.className = "stars";

    stars.innerHTML = "★".repeat(item.rating) + "☆".repeat(5 - item.rating);

    const feed = document.createElement("p");
    feed.className = "feedback-text";
    feed.innerText = item.feedback;

    left.appendChild(img);
    right.appendChild(stars);
    right.appendChild(feed);

    card.appendChild(left);
    card.appendChild(right);

    track.appendChild(card);

    const dot = document.createElement("span");
    dot.className = "fb-dot";
    if (i === 0) dot.classList.add("fb-active");
    dot.addEventListener("click", () => goToSlide(i));
    dotsContainer.appendChild(dot);
});



const dots = document.querySelectorAll(".fb-dot");

function updateSlider() {
    track.style.transform = `translateX(-${index * 100}%)`;

    dots.forEach(dot => dot.classList.remove("fb-active"));
    dots[index].classList.add("fb-active");
}

function nextSlide() {
    index = (index + 1) % feedbacks.length;
    updateSlider();
}

function prevSlide() {
    index = (index - 1 + feedbacks.length) % feedbacks.length;
    updateSlider();
}

function goToSlide(i) {
    index = i;
    updateSlider();
}

setInterval(nextSlide, 2000);

document.querySelector(".fb-next").addEventListener("click", nextSlide);
document.querySelector(".fb-prev").addEventListener("click", prevSlide);
