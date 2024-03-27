

function addPacket(packet) {
    console.log(packet);
}

function fetchPackets() {
    fetch("/api/traffic", {
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
            for (const packet of data) {
                addPacket(packet);
            }
        }
    })
    .catch(error => {
        console.error("Could't fetch from '/api/notifications':", error);
    });
}

window.onload = function () {
    fetchPackets();
    const updateInterval = 5 * 1000      //TODO: change this to take out of settings
    setInterval(fetchPackets, updateInterval);
}