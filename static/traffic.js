
function getPacketHTML(packet) {
    let layersHTML = `<div class="details">`
    for (const layerName in packet.layers) {
        if (Object.hasOwnProperty.call(packet.layers, layerName)) {
            const layer = packet.layers[layerName];
            let HTML = `
                <div class="layer">
                <h3>${layerName}</h3>
            `;
            for (const key in layer) {
                if (Object.hasOwnProperty.call(layer, key)) {
                    const value = layer[key];
                    HTML += `<p><b>${key}:</b> ${value}</p>`;
                }
            }
            HTML += `</div>`
            layersHTML += HTML;
        }
    }
    layersHTML += `</div>`;

    const template = `
    <div class="title">
        <span class="arrow">▶</span>
        <h2 class="summary">${packet.summary}</h2>
    </div>
    ${layersHTML}
    `;
    return template
}

function addPacket(packet) {
    let packetList = document.getElementById("packet-list");
    let packetItem = document.createElement("li");
    packetItem.classList.add("packet");
    packetItem.innerHTML = getPacketHTML(packet);
    packetItem.addEventListener('click', function() { this.classList.toggle("active"); }, false);

    packetList.insertBefore(packetItem, packetList.firstChild);
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
        console.error("Couldn't fetch from '/api/traffic':", error);
    });
}

window.onload = function () {
    fetchPackets();
    const updateInterval = 3 * 1000      //TODO: change this to take out of settings
    setInterval(fetchPackets, updateInterval);
}