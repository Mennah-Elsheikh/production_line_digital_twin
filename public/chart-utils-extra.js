function createHistogram(canvasId, label, labels, dataPoints, color) {
    const ctx = document.getElementById(canvasId);
    if (window[canvasId] && typeof window[canvasId].destroy === 'function') {
        window[canvasId].destroy();
    }

    window[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: dataPoints,
                backgroundColor: color,
                borderColor: color.replace('0.6', '1'),
                borderWidth: 1,
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Lead Time Distribution',
                    font: { size: 16 }
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Lead Time (minutes)' }
                },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Frequency' }
                }
            }
        }
    });
}

function createStackedBarChart(canvasId, title, labels, busyData, idleData) {
    const ctx = document.getElementById(canvasId);
    if (window[canvasId] && typeof window[canvasId].destroy === 'function') {
        window[canvasId].destroy();
    }

    window[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Busy',
                    data: busyData,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                },
                {
                    label: 'Idle',
                    data: idleData,
                    backgroundColor: 'rgba(201, 203, 207, 0.7)',
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: { size: 16 }
                },
            },
            scales: {
                x: { stacked: true },
                y: {
                    stacked: true,
                    max: 100,
                    ticks: { callback: v => v + '%' }
                }
            }
        }
    });
}
