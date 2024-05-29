// Function to create a chart using the AnyChart library
// Parameters:
//   data: The data to be visualized in the chart
//   containerId: The ID of the HTML container element where the chart will be rendered
function createChart(data, containerId) {
    // Ensure the chart is created only after the document is fully loaded
    anychart.onDocumentReady(function () {
        // Create a graph chart with the provided data
        var chart = anychart.graph(data);

        // Enable arrows on the edges of the graph
        chart.edges().arrows().enabled(true);
        // Enable labels on the nodes, set font size and weight
        chart.nodes().labels().enabled(true).fontSize(12).fontWeight(600);
        // Format the node labels to display the 'name' field
        chart.nodes().labels().format("{%name}");

        // Enable HTML in tooltips for richer content display
        chart.tooltip().useHtml(true);

        // Construct the format string for node tooltips with conditional display of fields
        chart.nodes().tooltip().format(
            "Name: {%name}" +
            "{%if address%} <br> Address: {%address} {%end if%}" + // Display address if available
            "{%if location%} {%location} {%end if%}" +             // Display location if available
            "{%if start_date%} <br> Start Date: {%start_date} {%end if%}" + // Display start date if available
            "{%if end_date%} <br> End Date: {%end_date} {%end if%}" +       // Display end date if available
            "{%if description%} <br> Description: {%description} {%end if%}" + // Display description if available
            "{%if email%} <br> Email: {%email} {%end if%}" +                 // Display email if available
            "{%if phone_number%} <br> Phone: {%phone_number} {%end if%}"     // Display phone number if available
        );

        // Format the tooltips for edges to show the 'from' and 'to' node names
        chart.edges().tooltip().format("From: {%from_name} <br> To: {%to_name}");

        // Set the container element where the chart will be rendered
        chart.container(containerId);
        // Draw the chart in the specified container
        chart.draw();
    });
}
