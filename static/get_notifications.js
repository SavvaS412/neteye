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

        if (data.length > 0) {
            for (const notification of data) {
                addNotification(notification);
            }
        }
    })
    .catch(error => {
        console.error("Could't fetch from '/api/notifications':", error);
    });
}

function addNotification(notification) {
    const list = document.getElementById("notification-list");
    let listItem = document.createElement('li');
    listItem.innerHTML = `<h3>${notification}</h3>`;

    list.insertBefore(listItem, list.firstChild);
}

window.onload = function () {
    const counter = document.getElementById("bell-counter");
    counter.hidden = true;
    fetchNotifications();
    const updateInterval = 15000      //TODO: change this to take out of settings
    setInterval(fetchNotifications, updateInterval);
}