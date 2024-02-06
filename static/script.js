document.addEventListener("DOMContentLoaded", function () {
    // Add 'selected' class to the home link initially
    document.querySelector("nav ul li:first-child").classList.add("selected");

    // Add 'selected' class to the clicked link and remove from others
    document.querySelectorAll("nav ul li").forEach(function (item) {
        item.addEventListener("click", function () {
            document.querySelectorAll("nav ul li").forEach(function (el) {
                el.classList.remove("selected");
            });
            this.classList.add("selected");
        });
    });
});
