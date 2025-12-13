function createTimeSeriesChart(canvasId, label, color, dataPoints) {
    const ctx = document.getElementById(canvasId);
    if (window[canvasId] && typeof window[canvasId].destroy === 'function') {
        window[canvasId].destroy();
    }

    // Downsample if too many points for smooth rendering
    const MAX_POINTS = 200;
    let displayData = dataPoints;
    if (dataPoints.length > MAX_POINTS) {
        const step = Math.ceil(dataPoints.length / MAX_POINTS);
        displayData = dataPoints.filter((_, i) => i % step === 0);
    }

    window[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: displayData.map(d => Math.round(d.time)),
            datasets: [{
                label: label,
                data: displayData.map(d => d.value),
                borderColor: color,
                backgroundColor: color.replace('1)', '0.1').replace(')', ', 0.1)'),
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                title: {
                    display: true,
                    text: label + ' Over Time',
                    font: { size: 16 }
                },
                tooltip: {
                    enabled: true
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time (minutes)'
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
