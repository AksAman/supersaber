const IP = "192.168.0.100";
const PORT = 8002;
const URL = `http://${IP}:${PORT}/audio-values`;
const WS_URL = `ws://${IP}:${PORT}/audio-values`;

const volumeDisplay = document.getElementById("volume-display");
const errorDisplay = document.getElementById("error-display");
const ctx = document.getElementById("volumeChart").getContext("2d");
const protocolElement = document.getElementById("protocol");
const body = document.querySelector("body");

const INTERVAL = 100;
let latestVolume = 0;

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

function connectWebSocket() {
  const ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    console.log("WebSocket connection opened.");
  };
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setVolume(data.v);
  };
  ws.onclose = () => {
    setVolume(0);
    console.log("WebSocket connection closed. Reconnecting in 5 seconds...");
    setTimeout(connectWebSocket, 5000);
  };
  ws.onerror = (error) => {
    setVolume(0);
    errorDisplay.textContent = "Error fetching volume. Please try again later.";
    console.error("WebSocket error:", error);
  };
}

const setVolume = (volume) => {
  latestVolume = volume;
  volumeDisplay.textContent = `Current Volume: ${latestVolume}`;
  errorDisplay.textContent = ""; // Clear any previous error message
  console.log(
    `Current Volume: ${latestVolume} (rgba(255, 255, 255, ${latestVolume})`
  );
};

const fetchVolume = async () => {
  try {
    const response = await fetch(URL);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const v = data.v;
    setVolume(v);
  } catch (error) {
    errorDisplay.textContent = "Error fetching volume. Please try again later.";
    console.error("Error fetching volume:", error);
    setVolume(0);
  }
};

function connectHTTP() {
  setInterval(fetchVolume, INTERVAL); // Poll every 5 seconds
}

const protocolUsed = "websocket";
protocolElement.textContent = `Using ${protocolUsed} protocol`;
if (protocolUsed === "http") {
  connectHTTP();
} else {
  connectWebSocket();
}
