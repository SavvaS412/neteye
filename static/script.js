document.addEventListener("DOMContentLoaded", function () {
    // Add 'selected' class to the home link initially
    if (document.URL.endsWith('/')){
        var selector = 1;
    }
    if (document.URL.endsWith('/capture')){
        var selector = 2;
    }
    if (document.URL.endsWith('/map')){
        var selector = 3;
    }
    if (document.URL.endsWith('/settings')){
        var selector = 4;
    }

    document.querySelector("nav ul li:nth-child(" + selector + ")").classList.add("selected");

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
