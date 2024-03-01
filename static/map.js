document.addEventListener('DOMContentLoaded', function () {
    const svg = d3.select('#map')
    .append('svg')
    .attr('width', '100%')
    .attr('height', '100%');

    const width = document.getElementById('map').parentNode.clientWidth;
    const height = document.getElementById('map').parentNode.clientHeight;

    let nodes=[{
        "ip": "192.168.1.1",
        "is_available": true,
        "latency": 1,
        "mac": "d4:35:1d:78:41:b5",
        "name": "OpenWrt.lan"
      }]


    const simulation = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-30)) // Repulsion between nodes
    .force('link', d3.forceLink().distance(100)) // Link force
    .force('center', d3.forceCenter(width / 2, height / 2)) // Centering force
    .on('tick', ticked);

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

            nodes = data;
            updateMap();

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


    fetchDevices();
    const updateInterval = 5000; //TODO: change this to take out of settings (5 sec)
    setInterval(fetchDevices, updateInterval);

    
    function updateMap() {
        const nodeJoin = svg.selectAll('.node')
        .data(nodes, d => d.ip); // Use 'ip' or another unique property as the key


        nodeJoin.enter() 
        .append('circle')
        .text("lol")
        .attr('class', 'node')
        .attr('r', width * 0.03) // Radius of the circle
        .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended)
        );

        // Position nodes based on a circular layout
        nodeJoin
        .attr('cx', (d, i) => Math.cos(i / nodes.length * 2 * Math.PI) * 200 + width / 2)
        .attr('cy', (d, i) => Math.sin(i / nodes.length * 2 * Math.PI) * 200 + height / 2);    


        nodeJoin.exit() // Nodes to remove
        .remove();

        // Restart simulation with updated nodes
        simulation.nodes(nodes).alpha(1).restart();
    }

    // Define drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Tick function to update node positions
    function ticked() {
        svg.selectAll('.node')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    }
});
