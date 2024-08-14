const URL = "http://192.168.0.108:8002/audio-values";
const volumeDisplay = document.getElementById("volume-display");
const errorDisplay = document.getElementById("error-display");
const ctx = document.getElementById("volumeChart").getContext("2d");

const INTERVAL = 1000;
const volumeChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        label: "Volume",
        data: [],
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
        fill: true,
        cubicInterpolationMode: "monotone",
      },
    ],
  },
  options: {
    scales: {
      x: {
        type: "realtime",
        realtime: {
          delay: 0,
          refresh: INTERVAL,
          onRefresh: function (chart) {
            chart.data.datasets[0].data.push({
              x: Date.now(),
              y: latestVolume,
            });
          },
        },
      },
    },
  },
});

let latestVolume = 0;

const fetchVolume = async () => {
  try {
    const response = await fetch(URL);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const v = data.v;
    // if (v <= 0) {
    //   return;
    // }
    latestVolume = v;
    volumeDisplay.textContent = `Current Volume: ${latestVolume}`;
    errorDisplay.textContent = ""; // Clear any previous error message
    console.log(`Current Volume: ${latestVolume}`);
  } catch (error) {
    errorDisplay.textContent = "Error fetching volume. Please try again later.";
    console.error("Error fetching volume:", error);
  }
};

setInterval(fetchVolume, INTERVAL); // Poll every 5 seconds
