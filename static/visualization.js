function createChart(employerData)
{
    anychart.onDocumentReady(function () {
    // create data
    var data = employerData;

    // create a chart and set the data
    var chart = anychart.graph(data);

    chart.edges().arrows().enabled(true);

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