import {notification_toast, notification_full} from "./notification.js"

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
        data.forEach(element => {
            // ava({
            //     icon: 'success',
            //     text: 'This is a Success Alert',
            //     btnText: 'Okay',
            //     progressBar: true,
            //     toast: false,
            // });
            notification_toast();
            notification_toast();
            notification_toast();
        });
        console.log(data); // For demonstration, you can replace this with your desired processing logic
    })
    .catch(error => {
        console.error("Could't fetch from '/api/notifications':", error);
    });
}

window.onload = function () {
    const updateInterval = 15000      //TODO: change this to take out of settings
    setInterval(fetchNotifications, updateInterval);
}
