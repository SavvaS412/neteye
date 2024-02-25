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
        
        for (const notification of data) {
            showNotification(notification);
        }
    })
    .catch(error => {
        console.error("Could't fetch from '/api/notifications':", error);
    });
}

window.onload = function () {
    const updateInterval = 15000      //TODO: change this to take out of settings
    setInterval(fetchNotifications, updateInterval);
}

const template = `
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="toast-image" viewBox="0 0 16 16">
<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
<path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
</svg>`

function showNotification(notification) {
    const toastBox = document.getElementById('toast-box');
    let anchor = document.createElement('a');
    anchor.href = "/notifications/" + notification.id;
    anchor.classList.add('toast');
    let toast = document.createElement('div');
    toast.classList.add('toast');
    toast.innerHTML = getNotificationHTML(notification);
    anchor.appendChild(toast);
    toastBox.appendChild(anchor);

    setTimeout(()=>{
        anchor.remove();
    },8000)
}

function getNotificationHTML(notification) {
    return template + notification.name;
}
