function createChart(employerData) {
    anychart.onDocumentReady(function () {
        // create data
        var employerChart = createGraph(employerData, "employer_chart_container");
        // set layout for employer chart
        layoutType(employerChart, "forceDirected");

        // create employee chart
        var employeeChart = createGraph(employeeData, "employee_chart_container");
        // set layout for employee chart
        layoutType(employeeChart, "forceDirected");

        // create institutions chart
        var institutionsChart = createGraph(institutionsData, "institutions_chart_container");
        // set layout for institutions chart
        layoutType(institutionsChart, "forceDirected");

        // create employee-employer relationships
        createRelations(employeeEmployerRelations, employeeChart, employerChart, institutionsChart);
    });
}

function createGraph(data, containerId) {
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
        var nodeFormat = "Name: {%name} </br> Address: {%address} " +
                                "</br> Start Date: {%start_date} </br> End Date: {%end_date} " +
                                "</br> Description: {%description}";
        chart.nodes().tooltip().format(nodeFormat);
        chart.edges().tooltip().format("From: {%from_name} </br> To: {%to_name}");

        // set the container id
        chart.container(containerId);

        // apply the recommended forceDirected layout
        chart.layout("forceDirected");

        // initiate drawing the chart
        chart.draw();

        return chart;
    }

    function layoutType(chart, type) {
        chart.layout().type(type);
    }
    function createRelations(relationsData, employeeChart, employerChart, institutionsChart) {
        var relations = anychart.data.tree(relationsData, "as-tree");
    
        var employeeToInstitutionMapping = {};
        var employerToInstitutionMapping = {};
    
        relations.traverse(function (item) {
            if (item.get("from_type") === "employee") {
                var employeeId = item.get("from");
                var institutionId = item.get("to");
                if (!employeeToInstitutionMapping[employeeId]) {
                    employeeToInstitutionMapping[employeeId] = [];
                }
                employeeToInstitutionMapping[employeeId].push(institutionId);
            } else if (item.get("from_type") === "employer") {
                var employerId = item.get("from");
                var institutionId = item.get("to");
                if (!employerToInstitutionMapping[employerId]) {
                    employerToInstitutionMapping[employerId] = [];
                }
                employerToInstitutionMapping[employerId].push(institutionId);
            }
        });
    
        // Create employee to institution edges
        for (var employeeId in employeeToInstitutionMapping) {
            var institutionIds = employeeToInstitutionMapping[employeeId];
            institutionIds.forEach(function (institutionId) {
                employeeChart.append(employeeId, institutionId);
            });
        }
    
        // Create institution to employer edges
        for (var employerId in employerToInstitutionMapping) {
            var institutionIds = employerToInstitutionMapping[employerId];
            institutionIds.forEach(function (institutionId) {
                institutionsChart.append(institutionId, employerId);
            });
        }
    }
