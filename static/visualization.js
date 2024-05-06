// Initializes the chart creation process by setting up the document to be ready for visualization
function createChart(visualizationData) {
    console.log("Visualization data:", visualizationData);
    anychart.onDocumentReady(function () {
        var chart = initializeChart(visualizationData);
        bindNodeClickEvent(chart, visualizationData);
        drawChart(chart);
        console.log("Chart created successfully");
    });
}

// Initializes the graph chart with provided data using AnyChart library
function initializeChart(visualizationData) {
    var chart = anychart.graph(visualizationData);
    chart.edges().arrows().enabled(true);
    chart.nodes().labels().enabled(true).format("{%name}" + " , ").fontSize(12).fontWeight(600);
    chart.tooltip().useHtml(true);
    chart.nodes().tooltip().format("{%name}");
    chart.edges().tooltip().format("Parent: {%from} -> Child: {%to} ({%title})");
    chart.container('chart_container');
    return chart;
}

// Binds click events to nodes in the chart, allowing for further interaction
function bindNodeClickEvent(chart, visualizationData) {
    chart.listen("click", function(e) {
        var tag = e.domTarget.tag;
        if (tag && tag.type === 'node') {
            console.log("Node clicked:", tag);
            var node = findNodeById(visualizationData.nodes, tag.id);
            console.log("Found Node:", node);
            if (node) {
                updateInfoPanel(node);
            } else {
                console.log("Node not found for ID:", tag.id);
            }
        } else {
            console.log("No node clicked or non-node element clicked");
        }
    });
}

// Finds a node in the array of nodes by its ID
function findNodeById(nodes, id) {
    return nodes.find(node => node.id == id);
}

// Renders the chart onto the page
function drawChart(chart) {
    chart.draw();
}

// Updates the information panel with details of the selected node
function updateInfoPanel(node) {
    console.log("updateInfoPanel called with node:", node);
    var infoPanel = document.getElementById('infoPanel');
    var content = generateInfoContent(node);
    infoPanel.innerHTML = content;
    console.log("infoPanel content updated:", content);
}

// Generates HTML content for displaying detailed information about a node
function generateInfoContent(node) {
    var content = `<div class="pb-5">
                        <strong>${node.kind}: ${node.name}</strong><br>`;
    if (node.kind === "Employer") {
        content += `Address: ${node.headquarters_address}<br>
                    Start Date: ${node.start_date}<br>
                    End Date: ${node.end_date || 'Active'}<br>`;
        if (node.description) {
            content += `Description: ${node.description}`;
        }
    } else if (node.kind === "Employee") {
        content += `Email: ${node.email_address}<br>
                    Phone: ${node.phone_number}<br>
                    Address: ${node.employee_address}`;
    }
    content += `</div>`;
    return content;
}