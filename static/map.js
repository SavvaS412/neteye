document.addEventListener('DOMContentLoaded', function () {
    const svg = d3.select('#map')
    .append('svg')
    .attr('width', '100%')
    .attr('height', '100%');

    const width = document.getElementById('map').clientWidth;
    const height = document.getElementById('map').clientHeight;

    let nodes=[];
    let links=[];

    let centerForce = 1;

    const simulation = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-200)) // Repulsion between nodes
    .force('link', d3.forceLink(links).distance(100)) // Link force
    .force('center', d3.forceCenter(width / 2, height / 2).strength(centerForce)) // Centering force
    .on('tick', ticked).alphaDecay(0.0002);

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

                /*interactive map*/
                const foundNode = nodes.find(node => node.ip === device.ip); // Find node with matching IP
                if (foundNode) {
                    // Update existing node's fields if needed
                    for (const key in device) {
                        if (device[key] !== foundNode[key]) { // Check for differences in each field
                            foundNode[key] = device[key]; // Update the field in the existing node
                        }
                    }
                } else {
                    addNode(device);
                }
            });

            for (const node of nodes) {
                const reverseFoundNode = data.find(device => device.ip === node.ip);
                if (!reverseFoundNode) {
                    removeNode(node);
                }
            }
            /*end interactive map*/

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
    window.addEventListener('resize', () => { // Add event listener for window resize
        updateMap(); 
        svg.selectAll('.node').selectAll("circle").attr('r', document.getElementById('map').clientWidth * 0.03);
    });

    setTimeout(() => {centerForce = 0.0001; console.log(centerForce);}, 1000);

    function connectNodes(source, target) {
        links.push({
          source: source,
          target: target,
        });
    }

    function addNode(device){
        nodes.push(device);
        connectNodes(device, nodes[0]);
        updateMap();
    }

    function removeNode(device){
        const index = nodes.indexOf(device);
        if (index !== -1) {
          nodes.splice(index, 1);
        }
        updateMap();
    }

    function updateMap(){
        const width = document.getElementById('map').clientWidth;
        const height = document.getElementById('map').clientHeight;

        //links
        var link = svg.selectAll('.link').data(links);
        link.enter()
            .insert('line', '.node')
            .attr('class', 'link')
            .style('stroke', '#d9d9d9');
        link
            .exit()
            .remove()

        var node = svg.selectAll('.node').data(nodes);
        var g = node.enter()
                  .append('g')
                  .attr('class', 'node');
        g.append('circle')
        .attr('r', width * 0.03) // Radius of the circle
        .style("fill", "#8E8")
        .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended)
        );

        g.append('text')
          .attr("class", "text")
          .text(function (d) { return d.name });
        node
          .exit()
          .remove();

        // update simulation
        console.log(centerForce);
        simulation
        .nodes(nodes)
        .force('center', d3.forceCenter(width / 2, height / 2).strength(centerForce)) // Centering force
        .force("link", d3.forceLink(links).distance(width / 10 + 50))
        .restart();
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
        .attr('cy', d => d.y)
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
          })
          ;
    }
    
});
