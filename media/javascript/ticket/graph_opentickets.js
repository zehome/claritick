function graph_opentickets_init(renderTo, tickIntervalDays) {
    var options = {
        chart: {
            renderTo: renderTo,
            defaultSeriesType: 'area'
        },
        title: {
            text: 'Tickets ouverts'
        },
        xAxis: {
            type: 'datetime',
            tickInterval: tickIntervalDays * 24 * 3600 * 1000,
            tickWidth: 0,
            gridLineWidth: 1,
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
                }
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

        series: []
    };
    return options;
}

function graph_opentickets_load(options, dataget_url, interval) {
    dojo.byId(options.chart.renderTo).innerHTML = "<p>" + options.title.text +  ": Loading...</p>";
    dojo.xhrPost({
        url: dataget_url, 
        postData: dojo.toJson({"interval": interval}), 
        handleAs:"json",
        load: function(data)
        {
            if (! data.hs_charts) { 
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
