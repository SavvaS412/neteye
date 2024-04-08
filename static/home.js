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

/* new geo */
let geojson;
let projection;
let geoGenerator = d3.geoPath()
  .projection(projection);

let graticule = d3.geoGraticule();

let circles = [
    [35, 31]
];

let geoCircle = d3.geoCircle().precision(1);
let width = document.getElementById("geo-map").clientWidth;
let height = document.getElementById("geo-map").clientHeight;
let state = {
  scale: 1500,
  translateX: width/2,
  translateY:  height/2,
  centerLon: 35,
  centerLat: 31,
  rotateLambda: 0.1,
  rotatePhi: 0,
  rotateGamma: 0
}

function initMenu() {
  d3.select('#menu')
    .selectAll('.slider.item input')
    .on('input', function(d) {
      let attr = d3.select(this).attr('name');
      state[attr] = this.value;
      d3.select(this.parentNode.parentNode).select('.value').text(this.value);
      update()
    });
}

function update() {
  // Update projection
  projection = d3.geoMercator()
  geoGenerator.projection(projection);

  projection
    .scale(state.scale)
    .translate([state.translateX, state.translateY])
    .center([state.centerLon, state.centerLat])
    .rotate([state.rotateLambda, state.rotatePhi, state.rotateGamma])

  // Update world map
  let u = d3.select('g.map')
    .selectAll('path')
    .data(geojson.features)

  u.enter()
    .append('path')
    .merge(u)
    .attr('class', 'country')
    .attr('d', geoGenerator)
    .on('click', function(e){
      if (d3.select(this).attr('class') == 'country selected') {
        d3.select(this).attr('class', 'country')
        .append('title')
        .text(d=>d.properties.name);
        //TODO - remove tooltip and add title
      }
      else{
        let country = d3.select(this);
        country.attr('class', 'country selected');
        country.append("div").attr("class", "tooltip")
        .append("span").attr("class", "country-name").text(d=>d.properties.name);
        console.log(d=>d.properties);
        //TODO - add other properties and remove title
      }
    })
    .append('title')
    .text(d=>d.properties.name);

  // Update projection center
  let projectedCenter = projection([state.centerLon, state.centerLat]);
  d3.select('.projection-center')
    .attr('cx', projectedCenter[0])
    .attr('cy', projectedCenter[1]);

  // Update graticule
  d3.select('.graticule path')
    .datum(graticule())
    .attr('d', geoGenerator);

  // Update circles
  u = d3.select('.circles')
    .selectAll('path')
    .data(circles.map(function(d) {
      geoCircle.center(d);
      geoCircle.radius(0.1/1);
      return geoCircle();
    }));

  u.enter()
    .append('path')
    .merge(u)
    .attr('d', geoGenerator);
}


//d3.json('https://gist.githubusercontent.com/d3indepth/f28e1c3a99ea6d84986f35ac8646fac7/raw/c58cede8dab4673c91a3db702d50f7447b373d98/ne_110m_land.json')
d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson")
	.then(function(json) {
		geojson = json;
		initMenu();
		update();

        const svg = d3.select("#geo-map");
        svg.style('pointer-events', 'all');
        svg.call(d3.zoom().scaleExtent([1/8, 8]).on('zoom', (event) => {
            const g = svg.select('g');
            g.attr('transform', event.transform);   //scale(${event.transform.k})translate(${event.transform.x}, ${event.transform.y})
        }))
	});

/* Geo Map */
// let mapState = {
//     scale: 4020,
//     centerLon: 0,       //horizontal
//     centerLat: 0,       //vertical
//     rotateLambda: 0.1
// };

// const svg = d3.select("svg"),
//     width = document.getElementById("geo-map").clientWidth,
//     height = document.getElementById("geo-map").clientHeight;
//     console.log(width, height);

// // Map and projection
// const projection = d3.geoMercator()
//     .center([35.0 ,31.4])                // GPS of location to zoom on
//     .scale(4020)                       // This is like the zoom
//     .translate([ width/2, height/2 ])


// // Create data for circles:
// const markers = [
// ];

// // Load external data and boot
// d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").then( function(data){

//     // Filter data
//     // data.features = data.features.filter( d => d.properties.name=="Israel")

//     // Draw the map
//     svg.append("g")
//         .selectAll("path")
//         .data(data.features)
//         .join("path")
//           .attr("fill", "#b8b8b8")
//           .attr("d", d3.geoPath()
//               .projection(projection)
//           )
//         .style("stroke", "black")
//         .style("opacity", .3)

//     // Add circles:
//     svg
//       .selectAll("myCircles")
//       .data(markers)
//       .join("circle")
//         .attr("cx", d => projection([d.long, d.lat])[0])
//         .attr("cy", d => projection([d.long, d.lat])[1])
//         .attr("r", 14)
//         .style("fill", "69b3a2")
//         .attr("stroke", "#69b3a2")
//         .attr("stroke-width", 3)
//         .attr("fill-opacity", .4)
// })
/* END Geo Map */

function fetchStatistics() {
    fetch("/api/statistics")
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

  