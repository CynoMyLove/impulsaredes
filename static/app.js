document.addEventListener("DOMContentLoaded", () => {
    const hasResults = document.body.dataset.hasResults === "true";

    if (hasResults) {
        const resultsSection = document.getElementById("resultados");

        if (resultsSection) {
            setTimeout(() => {
                resultsSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }, 250);
        }

        cargarGraficas();
    }
});

function cargarGraficas() {
    const dataElement = document.getElementById("chart-data");

    if (!dataElement || typeof Chart === "undefined") {
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);

    const metricas = chartData.metricas;
    const interaccion = chartData.interaccion;
    const engagement = chartData.engagement;

    const opcionesBase = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 13
                    }
                }
            }
        }
    };

    const graficaBarras = document.getElementById("graficaBarras");
    const graficaPastel = document.getElementById("graficaPastel");
    const graficaDona = document.getElementById("graficaDona");

    if (graficaBarras) {
        new Chart(graficaBarras, {
            type: "bar",
            data: {
                labels: metricas.labels,
                datasets: [
                    {
                        label: "Resultados estimados",
                        data: metricas.values,
                        backgroundColor: [
                            "#087f45",
                            "#2f9e75",
                            "#2563eb",
                            "#f59e0b",
                            "#ef4444"
                        ],
                        borderRadius: 8
                    }
                ]
            },
            options: {
                ...opcionesBase,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    if (graficaPastel) {
        new Chart(graficaPastel, {
            type: "pie",
            data: {
                labels: interaccion.labels,
                datasets: [
                    {
                        data: interaccion.values,
                        backgroundColor: [
                            "#2f9e75",
                            "#f59e0b",
                            "#ef4444"
                        ]
                    }
                ]
            },
            options: opcionesBase
        });
    }

    if (graficaDona) {
        new Chart(graficaDona, {
            type: "doughnut",
            data: {
                labels: engagement.labels,
                datasets: [
                    {
                        data: engagement.values,
                        backgroundColor: [
                            "#087f45",
                            "#dbe4ea"
                        ]
                    }
                ]
            },
            options: opcionesBase
        });
    }
}