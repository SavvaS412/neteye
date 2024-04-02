document.addEventListener("DOMContentLoaded", function () {

    if (document.URL.includes('/notifications'))
    {
        if (window.innerWidth < 700) {
            const element = document.getElementById("notification-item");
            element.classList.add("selected");
        }
        else {
            const element = document.getElementsByClassName("notification-bell");
            element.item(0).classList.add("selected");
        }
    }

    else
    {
        // Add 'selected' class to the home link initially
        let selector;
        if (document.URL.endsWith('/')){
            selector = 1;
        }
        if (document.URL.endsWith('/traffic')){
            selector = 2;
        }
        if (document.URL.endsWith('/map')){
            selector = 3;
        }
        if (document.URL.endsWith('/settings')){
            selector = 4;
        }

        document.querySelector("nav ul li:nth-child(" + selector + ")").classList.add("selected");
    }

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

// Function to add notification box as a list item
function addNotificationToList() {
    const notificationBox = document.querySelector('.notification-box');
    const menu = document.getElementById('menu');
    const notification_ref = document.getElementById('notification-ref');
    const listItem = document.getElementById('notification-item');

    if (window.innerWidth < 700) {
        if (!listItem) {
            const newListItem = document.createElement('li');
            newListItem.id = 'notification-item';
            if (notification_ref.children.item(1) && notification_ref.children.item(1).classList.contains("selected"))
                newListItem.className = "selected";
            const anchor = document.createElement('a');
            anchor.href = "/notifications";

            const notificationRefContent = notification_ref.innerHTML;
            const newElement = document.createElement('div');
            newElement.className = "notification-box-item";
            newElement.innerHTML = notificationRefContent;
            notificationBox.replaceChild(newElement, notification_ref);

            anchor.innerHTML = notificationBox.innerHTML;
            newListItem.appendChild(anchor);
            menu.appendChild(newListItem);
            notificationBox.style.display = 'none'; // Hide the original notification box
        }
    } else {
        notificationBox.style.display = 'block'; // Show the original notification box

        if (listItem) {
            const notificationBoxItem = document.querySelector('.notification-box-item');

            const newElement = document.createElement('a');
            newElement.href = "/notifications";
            newElement.id = "notification-ref";
            newElement.innerHTML = notificationBoxItem.innerHTML;
            notificationBox.replaceChild(newElement, notificationBoxItem);
            notificationBox.appendChild(newElement);
                
            if (listItem.classList.contains("selected")){
                const bell = notificationBox.children.item(0).children.item(1);
                if (!bell.classList.contains("selected"))
                    bell.classList.add("selected");
            }
            menu.removeChild(listItem); // Remove the notification item from the menu
            
        }
    }
}

// Initial call to the function
addNotificationToList();

// Event listener for window resize
window.addEventListener('resize', addNotificationToList);
