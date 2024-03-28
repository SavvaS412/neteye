    // Dictionary object to store devices by their IP addresses
    let DATA_RECIEVED = 0;
    let DATA_SENT = 0;
    let DATA_TOTAL = 0;
    let UDP = 0;
    let TCP = 0;
    let OTHER = 0;

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
            removeOldDevices(data);
            updateDeviceCount(Object.keys(devicesDict).length);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }

    function updateDeviceCount(length) {
        let count = document.getElementById("device-count");
        count.innerText = `Devices Connected: ${length}`;
    }

    function renderDevices() {
        // Clear previous device list
        const activeDevicesList = document.getElementById('devices-list');

        // Loop through devices in the dictionary and add them to the list
        Object.values(devicesDict).forEach(device => {
            const deviceItems = document.querySelectorAll(".device-item");
            const deviceItemsArray = Array.from(deviceItems);
            const foundItem = deviceItemsArray.find(item => {
                // Safely access the IP text content while handling potential errors
                const ipElement = item.querySelector(".device-info .ip");
              
                if (ipElement) {
                  const deviceIP = ipElement.textContent.trim(); // Get IP and trim whitespace
                  return deviceIP === device.ip; // Compare with target IP
                } else {
                  console.warn("Device item missing IP element:", item); // Log a warning if IP element is absent
                  return false; // Skip this item if IP element is not found
                }
              });

            if (foundItem)
            {
                const nameElement = foundItem.querySelector(".device-info .name");
                const latencyElement = foundItem.querySelector(".latency");
                const statusCircle = foundItem.querySelector(".status-circle");

                // Update name only if changed
                if (device.name && nameElement.textContent.trim() !== device.name) {
                  nameElement.textContent = device.name;
                }
              
                // Update latency only if changed
                if (device.latency && latencyElement.textContent.trim() !== device.latency + "ms") {
                  latencyElement.textContent = device.latency + "ms";
                  
                    blinkStatusCircle(statusCircle);
              
                }
              
                // Update status circle color based on availability
                statusCircle.style.background = device.is_available
                  ? "rgb(136, 238, 136)" /* green */
                  : "rgb(238, 136, 136)"; /* red */
            }
            else {
                const listItem = document.createElement('li');
                listItem.classList.add("device-item");
                listItem.innerHTML = `
                <span class="device-info">
                  <span class="name">${device.name}</span>
                  <span class="ip">${device.ip}</span>
                  <span class="status-circle" style="background: ${device.is_available ? 'rgb(136, 238, 136)' : 'rgb(238, 136, 136)'};"></span>
                  <span class="latency">${device.latency}ms</span>
                </span>`;    //&#9655 for white
    
                activeDevicesList.appendChild(listItem);
            }

        });
    }

    function removeOldDevices(data) {
        const activeDevicesList = document.getElementById('devices-list');
        /* check for reverse existence, removal */
        const existingItems = activeDevicesList.querySelectorAll(".device-item");
        // Loop through existing items and check against data
        for (const existingItem of existingItems) {
            const existingIP = existingItem.querySelector(".device-info .ip").textContent.trim();
            const foundDevice = data.find(device => device.ip === existingIP);

            if (!foundDevice) {
                // Remove the item if not found in data
                activeDevicesList.removeChild(existingItem);
            }
        }
    }

    
function blinkStatusCircle(statusCircle) {
    statusCircle.classList.add("blink");

    setTimeout(() => {
        statusCircle.classList.remove("blink");
    }, 3000);
}

function updateTrafficStats(){
    let sent = document.getElementById("sent");
    let recieved = document.getElementById("recieved");
    let total = document.getElementById("total");

    sent.innerText = `Data Sent: ${DATA_SENT} bytes`;
    recieved.innerText = `Data Recieved: ${DATA_RECIEVED} bytes`;
    total.innerText = `Data Total: ${DATA_TOTAL} bytes`;
}
function updateProtocolStats(){
    let tcp = document.getElementById("tcp");
    let udp = document.getElementById("udp");
    let other = document.getElementById("other");

    tcp.innerText = `TCP: ${TCP} packets`;
    udp.innerText = `UDP: ${UDP} packets`;
    other.innerText = `Other: ${OTHER} packets`;
}

function fetchStatistics() {
    fetch("/api/capture_statistics")
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle the JSON data here
        if (!(DATA_RECIEVED == data.data_recieved && DATA_SENT == data.data_sent 
            && DATA_TOTAL == data.data_total && TCP == data.tcp && UDP == data.udp && OTHER == data.other))
            {
                DATA_RECIEVED = data.data_recieved; 
                DATA_SENT = data.data_sent;
                DATA_TOTAL = data.data_total;
                TCP = data.tcp;
                UDP = data.udp;
                OTHER = data.other;
                updateTrafficStats();
                updateProtocolStats();
            }
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

fetchDevices();
fetchStatistics();
const updateInterval = 5000; //TODO: change this to take out of settings (5 sec)
setInterval(fetchDevices, updateInterval);
setInterval(fetchStatistics, updateInterval);

  