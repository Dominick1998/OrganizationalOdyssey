function createChart(data, containerId) {
    anychart.onDocumentReady(function () {
        var chart = anychart.graph(data);

        chart.edges().arrows().enabled(true);
        chart.nodes().labels().enabled(true).fontSize(12).fontWeight(600);
        chart.nodes().labels().format("{%name}");  // Ensure label is displayed

        chart.tooltip().useHtml(true);

        // Construct the format string with conditional display
        chart.nodes().tooltip().format(
            "Name: {%name}" +
            "{%if address%} <br> Address: {%address} {%end if%}" +
            "{%if location%} {%location} {%end if%}" +
            "{%if start_date%} <br> Start Date: {%start_date} {%end if%}" +
            "{%if end_date%} <br> End Date: {%end_date} {%end if%}" +
            "{%if description%} <br> Description: {%description} {%end if%}" +
            "{%if email%} <br> Email: {%email} {%end if%}" +
            "{%if phone_number%} <br> Phone: {%phone_number} {%end if%}"
        );

        chart.edges().tooltip().format("From: {%from_name} <br> To: {%to_name}");

        chart.container(containerId);
        chart.draw();
    });
}
