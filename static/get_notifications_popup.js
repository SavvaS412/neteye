function fetchNotifications() {
    fetch("/api/notifications", {
        method: "GET"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle the JSON data here
        console.log(data); // For demonstration, you can replace this with your desired processing logic
        const counter = document.getElementById("bell-counter");

        if (data.length > 0) {
            if (data.length > 9)
                counter.innerText = "+9";
            else
                counter.innerText = data.length;
            counter.hidden = false;
            for (const notification of data) {
                showNotification(notification);
            }
        }
        else {
            counter.hidden = true;
        }
    })
    .catch(error => {
        console.error("Couldn't fetch from '/api/active-notifications':", error);
    });
}

window.onload = function () {
    fetchNotifications();
    const updateInterval = 15000      //TODO: change this to take out of settings
    setInterval(fetchNotifications, updateInterval);
}

window.addEventListener("scroll", changeNotificationBoxPosition , false);

const template = `
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="toast-image" viewBox="0 0 16 16">
<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
<path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
</svg>`//TODO replace <?xml version="1.0" ?><svg height="1792" viewBox="0 0 1792 1792" width="1792" xmlns="http://www.w3.org/2000/svg"><path d="M1152 1376v-160q0-14-9-23t-23-9h-96v-512q0-14-9-23t-23-9h-320q-14 0-23 9t-9 23v160q0 14 9 23t23 9h96v320h-96q-14 0-23 9t-9 23v160q0 14 9 23t23 9h448q14 0 23-9t9-23zm-128-896v-160q0-14-9-23t-23-9h-192q-14 0-23 9t-9 23v160q0 14 9 23t23 9h192q14 0 23-9t9-23zm640 416q0 209-103 385.5t-279.5 279.5-385.5 103-385.5-103-279.5-279.5-103-385.5 103-385.5 279.5-279.5 385.5-103 385.5 103 279.5 279.5 103 385.5z"/></svg>

function showNotification(notification) {
    const toastBox = document.getElementById('toast-box');
    let anchor = document.createElement('a');
    anchor.href = "/notifications/" + notification.id;
    anchor.classList.add('toast');
    let toast = document.createElement('div');
    toast.classList.add('toast', 'fade-in');
    toast.innerHTML = getNotificationHTML(notification);
    anchor.appendChild(toast);
    toastBox.appendChild(anchor);

    setTimeout(() => {
        toast.classList.remove('fade-in'); // Remove 'fade-in' class
        toast.classList.add('fade-out'); // Add 'fade-out' class
        setTimeout(() => {
            anchor.remove(); // Remove the notification from DOM after fade out
        }, 3000); // Wait for 3 seconds for fade out animation to complete
    }, 10000); // TODO: Wait for 6 seconds before starting fade-out animation (2 seconds fade-in + 8 seconds visible)  - change this to take out of settings

}

function getNotificationHTML(notification) {
    return template + `
    <h3 class="notification-toast-name">${notification.name}</h3>
    <p class="notification-toast-type">${notification.type}</p>
    <p class="notification-toast-date">${notification.date}</p>`;
}

function changeNotificationBoxPosition () {
    function changeToFixed(toastBox) {
        toastBox.style.position = "fixed"
        toastBox.style.top = 0;
    }
    function changeToAbsolute(toastBox) {
        toastBox.style.position = "absolute"
        toastBox.style.top = null;
    }
    var toastBox = document.getElementById("toast-box");
    this.scrollY > 64 ? changeToFixed(toastBox) : changeToAbsolute(toastBox);
    console.log(toastBox.style.top);
}
