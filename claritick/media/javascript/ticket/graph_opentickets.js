function graph_opentickets_init(renderTo, tickIntervalDays, title, defaultSeriesType) {
    if (! defaultSeriesType)
        defaultSeriesType = 'area';
    if (! title)
        title = 'Inconnu';

    var options = {
        chart: {
            renderTo: renderTo,
            defaultSeriesType: defaultSeriesType,
            zoomType: 'x'
        },
        credits: {
            enabled: false
        },
        title: {
            text: title
        },
        xAxis: {
            type: 'datetime',
            tickInterval: tickIntervalDays * 24 * 3600 * 1000,
            tickWidth: 0,
            gridLineWidth: 1,
            labels: {
                y: 25,
                rotation: 90
            }
        },
        yAxis: {
            title: {
                text: null
            },
            labels: {
                align: 'left',
                x: 3,
                y: 16,
                formatter: function() {
                    return Highcharts.numberFormat(this.value, 0);
                },
            },
            showFirstLabel: false
        },

        tooltip: {
            shared: true,
            crosshairs: true
        },

        plotOptions: {
            area: {
                stacking: 'normal',
                lineWidth: 2
            }
        },
        exporting: {
            enabled: true
        },

        series: []
    };
    return options;
}

function graph_opentickets_load(options, dataget_url, interval) {
    dojo.byId(options.chart.renderTo).innerHTML = "<p>" + options.title.text +  ": Loading...</p>";
    dojo.xhrPost({
        headers: { 'X-CSRFToken': dojo.cookie("csrftoken") },
        url: dataget_url, 
        postData: dojo.toJson({"interval": interval}), 
        handleAs:"json",
        load: function(data)
        {
            if (! data.hs_charts || ! data.hs_charts.length) { 
                dojo.byId(options.chart.renderTo).innerHTML = "<p>" + options.title.text +  ": no data.</p>";
            } else {
                dojo.forEach(data.hs_charts, function(chart_data, index) {
                    var serie = {
                        name: chart_data.name,
                        data: []
                    };
                    dojo.forEach(chart_data.data, function(d, idx) {
                        serie.data.push([ Date.parse(d[0]), d[1] ]);
                    });
                    options.series.push(serie);
                    new Highcharts.Chart(options);
                });
            }
        }
    });
}
