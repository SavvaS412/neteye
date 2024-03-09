// Dictionary object to store devices by their IP addresses
const devicesDict = {};

function fetchDevices() {
    fetch("/api/map")
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle the JSON data here
        console.log(data); // For demonstration, you can replace this with your desired processing logic
        
        // Update devices dictionary with the latest information
        data.forEach(device => {
            if (device.is_available) {
                const ip = device.ip;
                if (devicesDict[ip]) {
                    // If device already exists, update its information
                    Object.assign(devicesDict[ip], device);
                } else {
                    // If device is new, add it to the dictionary
                    devicesDict[ip] = device;
                }
            }
        });

        // Render the latest device information
        renderDevices();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function renderDevices() {
    // Clear previous device list
    const devicesContainer = document.getElementById('devices-container');
    devicesContainer.innerHTML = '';

    // Create a list of current active devices
    const activeDevicesList = document.createElement('ul');

    // Loop through devices in the dictionary and add them to the list
    Object.values(devicesDict).forEach(device => {
        const listItem = document.createElement('li');
        listItem.textContent = `${device.name} ${device.ip} ${device.mac} ${device.latency} ${device.is_available}`;
        activeDevicesList.appendChild(listItem);
    });

    // Append the list to the container
    devicesContainer.appendChild(activeDevicesList);
}

window.onload = function () {
    fetchDevices();
    const updateInterval = 15000; //TODO: change this to take out of settings
    setInterval(fetchDevices, updateInterval);
};
