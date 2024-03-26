const addedNotifications = new Set();

// Helper function to compare notification fields
function fieldsAreEqual(notification1, notification2) {
    const keys1 = Object.keys(notification1);
    for (const key of keys1) {
      if (notification1[key] !== notification2[key]) {
        return false;
      }
    }
    return true;
  }

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
                let alreadyShown = false;
                for (const shown of addedNotifications) {
                    if (fieldsAreEqual(notification, shown)) {
                        alreadyShown = true;
                        break;
                    }
                }

                if (!alreadyShown) {
                    addNotification(notification);
                    addedNotifications.add(notification);
                }
            }
        }
    })
    .catch(error => {
        console.error("Could't fetch from '/api/notifications':", error);
    });
}

const template = `
<a href="#">
<div class="notification-right-container">
    <span class="notification-date">2024-03-26 22:45:36</span>
    
    <svg class="notification-is-read" contentscripttype="text/ecmascript" contentstyletype="text/css" enable-background="new 0 0 2048 2048" height="32px" id="Layer_1" preserveAspectRatio="xMidYMid meet" version="1.1" viewBox="121.0 0 1550.0 2048" width="32px" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" zoomAndPan="magnify">
        <path d="M1671,694c0,26.667-9.333,49.333-28,68l-724,724l-136,136c-18.667,18.667-41.333,28-68,28s-49.333-9.333-68-28l-136-136  l-362-362c-18.667-18.667-28-41.333-28-68s9.333-49.333,28-68l136-136c18.667-18.667,41.333-28,68-28s49.333,9.333,68,28l294,295  l656-657c18.667-18.667,41.333-28,68-28s49.333,9.333,68,28l136,136C1661.667,644.667,1671,667.333,1671,694z"></path>
    </svg>

</div>
<h3>Device Added 192.168.1.142</h3>
<p>added 6e:db:8f:ad:9d:36 as 192.168.1.142</p>
</a>`

function addNotification(notification) {
    const list = document.getElementById("notification-list");
    let listItem = document.createElement('div');
    listItem.classList.add("notification-item");
    listItem.value = id;
        //TODO: change here innerHTML to template with params
    listItem.innerHTML = `<h3>${notification.name}</h3>`;

    list.insertBefore(listItem, list.firstChild);
}

window.onload = function () {
    const counter = document.getElementById("bell-counter");
    counter.hidden = true;
    fetchNotifications();
    const updateInterval = 15000      //TODO: change this to take out of settings
    setInterval(fetchNotifications, updateInterval);
}