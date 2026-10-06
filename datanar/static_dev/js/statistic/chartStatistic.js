// Включение тултипов Bootstrap
const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]'
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);

const chartsConfig = [
  { scriptId: "browserData", canvasId: "browserChart" },
  { scriptId: "osData", canvasId: "osChart" },
  { scriptId: "countryData", canvasId: "countryChart" },
  { scriptId: "cityData", canvasId: "cityChart" },
];

chartsConfig.forEach(({ scriptId, canvasId }) => {
  const scriptElement = document.getElementById(scriptId);
  const canvasElement = document.getElementById(canvasId);

  if (!scriptElement || !canvasElement) return;

  const rawData = JSON.parse(scriptElement.textContent || "{}");

  const labels = Object.keys(rawData);
  const data = Object.values(rawData);

  new Chart(canvasElement.getContext("2d"), {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          borderWidth: 1,
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          display: false,
        },
      },
      responsive: true,
    },
  });
});