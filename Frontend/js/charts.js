/**
 * Chart.js Configuration & Management
 * Dynamic charts with dark theme styling
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: 'rgba(255,255,255,0.7)',
                        font: { family: 'Inter', size: 12 },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 17, 40, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: 'rgba(255,255,255,0.8)',
                    borderColor: 'rgba(124, 58, 237, 0.3)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { family: 'Inter', weight: '600' },
                    bodyFont: { family: 'JetBrains Mono' },
                    displayColors: true,
                    boxPadding: 4
                }
            },
            scales: {
                x: {
                    ticks: { color: 'rgba(255,255,255,0.5)', font: { size: 11 } },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                },
                y: {
                    ticks: { color: 'rgba(255,255,255,0.5)', font: { size: 11 } },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                }
            }
        };
    }

    createPerformanceChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const models = data.map(d => d.name);
        const colors = [
            'rgba(59, 130, 246, 0.8)',
            'rgba(124, 58, 237, 0.8)',
            'rgba(0, 245, 255, 0.8)',
            'rgba(0, 230, 118, 0.8)',
            'rgba(255, 171, 0, 0.8)',
        ];

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: models,
                datasets: [
                    {
                        label: 'Accuracy',
                        data: data.map(d => (d.accuracy * 100).toFixed(1)),
                        backgroundColor: 'rgba(59, 130, 246, 0.6)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                        barPercentage: 0.7
                    },
                    {
                        label: 'Precision',
                        data: data.map(d => (d.precision * 100).toFixed(1)),
                        backgroundColor: 'rgba(124, 58, 237, 0.6)',
                        borderColor: 'rgba(124, 58, 237, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                        barPercentage: 0.7
                    },
                    {
                        label: 'Recall',
                        data: data.map(d => (d.recall * 100).toFixed(1)),
                        backgroundColor: 'rgba(0, 245, 255, 0.6)',
                        borderColor: 'rgba(0, 245, 255, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                        barPercentage: 0.7
                    },
                    {
                        label: 'F1-Score',
                        data: data.map(d => (d.f1 * 100).toFixed(1)),
                        backgroundColor: 'rgba(0, 230, 118, 0.6)',
                        borderColor: 'rgba(0, 230, 118, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                        barPercentage: 0.7
                    },
                    {
                        label: 'ROC-AUC',
                        data: data.map(d => (d.roc_auc * 100).toFixed(1)),
                        backgroundColor: 'rgba(255, 171, 0, 0.6)',
                        borderColor: 'rgba(255, 171, 0, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                        barPercentage: 0.7
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        ...this.defaultOptions.plugins.legend,
                        position: 'top'
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: (val) => val + '%'
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    createFeatureChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const top10 = data.slice(0, 10);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top10.map(d => d.feature || d.shap_importance ? d.feature : d.feature),
                datasets: [{
                    label: 'Importance',
                    data: top10.map(d => d.shap_importance || d.importance || 0),
                    backgroundColor: top10.map((_, i) => {
                        const colors = [
                            'rgba(0, 245, 255, 0.7)',
                            'rgba(124, 58, 237, 0.7)',
                            'rgba(59, 130, 246, 0.7)',
                            'rgba(244, 114, 182, 0.7)',
                            'rgba(0, 230, 118, 0.7)',
                            'rgba(255, 171, 0, 0.6)',
                            'rgba(255, 109, 0, 0.6)',
                            'rgba(156, 163, 175, 0.6)',
                            'rgba(139, 92, 246, 0.6)',
                            'rgba(96, 165, 250, 0.6)',
                        ];
                        return colors[i % colors.length];
                    }),
                    borderWidth: 0,
                    borderRadius: 4,
                    barPercentage: 0.65
                }]
            },
            options: {
                ...this.defaultOptions,
                indexAxis: 'y',
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ...this.defaultOptions.scales.x,
                        beginAtZero: true
                    },
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            font: { size: 11, family: 'JetBrains Mono' }
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart',
                    delay: (context) => context.dataIndex * 100
                }
            }
        });
    }

    createRadarChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Get top 3 models
        const topModels = data.slice(0, 3);
        const colors = [
            { bg: 'rgba(0, 245, 255, 0.15)', border: 'rgba(0, 245, 255, 0.8)' },
            { bg: 'rgba(124, 58, 237, 0.15)', border: 'rgba(124, 58, 237, 0.8)' },
            { bg: 'rgba(244, 114, 182, 0.15)', border: 'rgba(244, 114, 182, 0.8)' },
        ];

        this.charts[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'],
                datasets: topModels.map((m, i) => ({
                    label: m.name,
                    data: [
                        m.accuracy * 100,
                        m.precision * 100,
                        m.recall * 100,
                        m.f1 * 100,
                        m.roc_auc * 100
                    ],
                    backgroundColor: colors[i].bg,
                    borderColor: colors[i].border,
                    borderWidth: 2,
                    pointBackgroundColor: colors[i].border,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        ...this.defaultOptions.plugins.legend,
                        position: 'bottom'
                    },
                    tooltip: this.defaultOptions.plugins.tooltip
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: 'rgba(255,255,255,0.3)',
                            backdropColor: 'transparent',
                            font: { size: 10 },
                            stepSize: 20
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.06)'
                        },
                        pointLabels: {
                            color: 'rgba(255,255,255,0.6)',
                            font: { size: 12, weight: '500' }
                        },
                        angleLines: {
                            color: 'rgba(255,255,255,0.06)'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    createConfusionMatrix(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Find best model's confusion matrix
        let cm = null;
        for (const [name, metrics] of Object.entries(data)) {
            if (metrics.confusion_matrix) {
                cm = metrics.confusion_matrix;
                break;
            }
        }

        if (!cm) return;

        const tn = cm[0][0], fp = cm[0][1], fn = cm[1][0], tp = cm[1][1];

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['True Negative', 'False Positive', 'False Negative', 'True Positive'],
                datasets: [{
                    label: 'Count',
                    data: [tn, fp, fn, tp],
                    backgroundColor: [
                        'rgba(0, 230, 118, 0.6)',
                        'rgba(255, 171, 0, 0.6)',
                        'rgba(255, 109, 0, 0.6)',
                        'rgba(0, 245, 255, 0.6)'
                    ],
                    borderColor: [
                        'rgba(0, 230, 118, 1)',
                        'rgba(255, 171, 0, 1)',
                        'rgba(255, 109, 0, 1)',
                        'rgba(0, 245, 255, 1)'
                    ],
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.6
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: { display: false },
                    title: {
                        display: true,
                        text: `TN: ${tn} | FP: ${fp} | FN: ${fn} | TP: ${tp}`,
                        color: 'rgba(255,255,255,0.5)',
                        font: { size: 12, family: 'JetBrains Mono' }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutBounce'
                }
            }
        });
    }

    drawGauge(canvasId, value, color) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height - 10;
        const radius = 120;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Background arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
        ctx.lineWidth = 20;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
        ctx.lineCap = 'round';
        ctx.stroke();

        // Gradient segments
        const segments = [
            { start: Math.PI, end: Math.PI * 1.33, color: '#00e676' },
            { start: Math.PI * 1.33, end: Math.PI * 1.66, color: '#ffab00' },
            { start: Math.PI * 1.66, end: Math.PI * 1.83, color: '#ff6d00' },
            { start: Math.PI * 1.83, end: Math.PI * 2, color: '#ff1744' },
        ];

        segments.forEach(seg => {
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, seg.start, seg.end);
            ctx.lineWidth = 20;
            ctx.strokeStyle = seg.color + '20';
            ctx.lineCap = 'butt';
            ctx.stroke();
        });

        // Value arc
        const endAngle = Math.PI + (value / 100) * Math.PI;

        const gradient = ctx.createLinearGradient(
            centerX - radius, centerY, centerX + radius, centerY
        );
        gradient.addColorStop(0, '#00e676');
        gradient.addColorStop(0.5, '#ffab00');
        gradient.addColorStop(0.75, '#ff6d00');
        gradient.addColorStop(1, '#ff1744');

        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, endAngle);
        ctx.lineWidth = 20;
        ctx.strokeStyle = color || gradient;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Glow effect
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, endAngle);
        ctx.lineWidth = 24;
        ctx.strokeStyle = (color || '#00f5ff') + '15';
        ctx.lineCap = 'round';
        ctx.stroke();

        // Needle tip glow
        const tipX = centerX + radius * Math.cos(endAngle);
        const tipY = centerY + radius * Math.sin(endAngle);

        const glowGradient = ctx.createRadialGradient(tipX, tipY, 0, tipX, tipY, 15);
        glowGradient.addColorStop(0, (color || '#00f5ff') + '60');
        glowGradient.addColorStop(1, (color || '#00f5ff') + '00');

        ctx.beginPath();
        ctx.arc(tipX, tipY, 15, 0, Math.PI * 2);
        ctx.fillStyle = glowGradient;
        ctx.fill();
    }
}

// Initialize Chart Manager
const chartManager = new ChartManager();