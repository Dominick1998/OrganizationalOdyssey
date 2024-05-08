function createChart(data, containerId) {
    anychart.onDocumentReady(function () {
        var chart = anychart.graph(data);

        chart.edges().arrows().enabled(true);
        chart.nodes().labels().enabled(true).fontSize(12).fontWeight(600);
        chart.nodes().labels().format("{%name}");  // Ensure label is displayed

        chart.tooltip().useHtml(true);
        var nodeFormat = getNodeFormat(data.nodes[0]);  // Determine format based on the first node's type
        chart.nodes().tooltip().format(nodeFormat);
        chart.edges().tooltip().format("From: {%from_name} </br> To: {%to_name}");

        chart.container(containerId);
        chart.draw();
    });
}

function getNodeFormat(node) {
    let formatString = "Name: {%name}";

    if (node.type === 'employer') {
        formatString += " </br> Address: {%address}" +
                        "</br> Start Date: {%start_date} </br> End Date: {%end_date}" +
                        "</br> Description: {%description}";
    } else if (node.type === 'employee') {
        formatString += " </br> Email: {%email}" +
                        "</br> Phone Number: {%phone_number}";
    } else if (node.type === 'institution') {
        formatString += " </br> Location: {%location}" +
                        "</br> Description: {%description}";
    }
    return formatString;
}