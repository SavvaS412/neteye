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
            //console.log(data); // For demonstration, you can replace this with your desired processing logic //TODO: delete
            
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
            removeOldDevices(data);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
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
                <span class="arrow">&#9654;</span>
                <span class="device-info">
                  <span class="name">${device.name}</span>
                  <span class="ip">${device.ip}</span>
                  <span class="status-circle" style="background: ${device.is_available ? 'rgb(136, 238, 136)' : 'rgb(238, 136, 136)'};"></span>
                  <span class="latency">${device.latency}ms</span>
                </span>
                <div class="details">
                  <p>MAC Address: ${device.mac}</p>
                  <p>Status: ${device.is_available ? 'Up' : 'Destination Host Unreachable'}</p>
                </div>`;    //&#9655 for white
    
                listItem.addEventListener("click", function() {
                    const details = this.querySelector(".details");
                    const arrow = this.querySelector(".arrow");
                    this.classList.toggle("active");
                    arrow.classList.toggle("active");
                    details.classList.toggle("active");
                });
    
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


    fetchDevices();
    const updateInterval = 5000; //TODO: change this to take out of settings (5 sec)
    setInterval(fetchDevices, updateInterval);
    window.addEventListener('resize', () => { // Add event listener for window resize
        updateMap(); 
        svg.selectAll('.node').selectAll("circle").attr('r', document.getElementById('map').clientWidth * 0.04);
    });

    setTimeout(() => {centerForce = 0.001; console.log(centerForce);}, 1000);

    function connectNodes(source, target) {
        if (source !== target){
            links.push({
                source: source,
                target: target,
              });
        }
    }

    function unconnectNodes(device) {
        const filteredLinks = links.filter(link => link.source !== device && link.target !== device);
        links.length = 0; // Clear existing elements
        links.push(...filteredLinks); // Add filtered elements back
        console.log("links after", links);
    }

    function addNode(device){
        nodes.push(device);
        connectNodes(device, nodes[0]);
        updateMap();
    }

    function removeNode(device){
        console.log("removing", device);

        const index = nodes.indexOf(device);
        if (index !== -1) {
          nodes.splice(index, 1);
        }

        console.log("links before", links);
        unconnectNodes(device);
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
        .attr('r', width * 0.04) // Radius of the circle
        .style("fill", "#8E8")
        .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended)
        );

        g.append('text')
          .attr("class", "name")
          .text(function (d) { return d.name });
        g.append('text')
          .attr("class", "ip")
          .text(function (d) { return d.ip });
        node
          .exit()
          .remove();

        // update simulation
        console.log(centerForce);
        simulation
        .nodes(nodes)
        .force('center', d3.forceCenter(width / 2, height / 2).strength(centerForce)) // Centering force
        .force("link", d3.forceLink(links).distance(width / 10 + 80))
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
        svg.selectAll('.link')
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
    }

});