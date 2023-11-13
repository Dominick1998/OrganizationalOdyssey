anychart.onDocumentReady(function () {
  // create data
  var data = {
    nodes: [
      {id: "Richard"},
      {id: "Larry"},
      {id: "Marta"},
      {id: "Jane"},
      {id: "Norma"},
      {id: "Frank"},
      {id: "Brett"}
    ],
    edges: [
      {from: "Richard", to: "Larry"},
      {from: "Richard", to: "Marta"},
      {from: "Larry",   to: "Marta"},
      {from: "Marta",   to: "Jane"},
      {from: "Jane",    to: "Norma"},
      {from: "Jane",    to: "Frank"},
      {from: "Jane",    to: "Brett"},
      {from: "Brett",   to: "Frank"}
    ]
  };

  // create a chart and set the data
  var chart = anychart.graph(data);

  // set the container id
  chart.container("container");

  // initiate drawing the chart
  chart.draw();
});

// set the layout type
function layoutType(type) {
  chart.layout().type(type);
}