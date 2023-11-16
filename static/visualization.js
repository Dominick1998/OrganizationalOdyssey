function createChart(employerData)
{
    anychart.onDocumentReady(function () {
    // create data
    var data = employerData;

    // create a chart and set the data
    var chart = anychart.graph(data);

    chart.edges().arrows().enabled(true);

    // enable labels of nodes
    chart.nodes().labels().enabled(true);

    // configure labels of nodes
    chart.nodes().labels().format("{%name}");
    chart.nodes().labels().fontSize(12);
    chart.nodes().labels().fontWeight(600);

    chart.tooltip().useHtml(true);
    chart.nodes().tooltip().format("Name: {%name} </br> Address: {%address}");
    chart.edges().tooltip().format("From: {%from_name} </br> To: {%to_name}")

    // set the container id
    chart.container("container");

    // initiate drawing the chart
    chart.draw();
    });

    // set the layout type
    function layoutType(type) {
      chart.layout().type(type);
    }
}