const bio = document.querySelector("#bio")
const interests = document.querySelector("#interests")
const goals = document.querySelector("#goals")

// querySelector is the first found element, querySelectorAll is all elements that match the selecto
//      in an array by order that elements are found
// It's good to use IDs with querySelector and classes with querySelectorAll

function showBio() {
    bio.classList.remove("hidden");
    interests.classList.add("hidden");
    goals.classList.add("hidden");
}

function showInterests() {
    bio.classList.add("hidden");
    interests.classList.remove("hidden");
    goals.classList.add("hidden");
}

function showGoals() {
    bio.classList.add("hidden");
    interests.classList.add("hidden");
    goals.classList.remove("hidden");
}