import random
import time
import adafruit_requests
import adafruit_connection_manager
import wifi


class CustomDecoder:
    def __init__(self, rms_level=0, min: int = 0, max: int = 300, alpha=0.16):
        self._rms_level = rms_level
        self._previous_rms_level = 0
        self._alpha = alpha  # Smoothing factor
        self.min = min
        self.max = max

    @property
    def rms_level(self):
        return self._rms_level

    @rms_level.setter
    def rms_level(self, value):
        self._rms_level = value

    def animate(self):
        new_value = random.randint(self.min, self.max)
        self._rms_level = (
            self._alpha * new_value + (1 - self._alpha) * self._previous_rms_level
        )
        self._previous_rms_level = self._rms_level

    def reset(self):
        self._rms_level = 0
        self._previous_rms_level = 0


pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
rssi = wifi.radio.ap_info.rssi

ssid = wifi.radio.ap_info.ssid
print(f"SSID: {ssid}")
print(f"RSSI: {rssi}")


class HttpAudioDecoder(CustomDecoder):

    def __init__(
        self, endpoint: str, on_error_callback=None, error_threshold=3, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.temp_rms_level = 0
        self.error_count = 0
        self.error_threshold = error_threshold
        self.on_error_callback = on_error_callback
        # return if wifi is not connected
        if not wifi.radio.connected:
            print("Wifi is not connected")
            return

    def reset(self):
        self.error_count = 0
        super().reset()

    def on_error(self):
        self.error_count += 1
        if self.error_count >= self.error_threshold and self.on_error_callback:
            self.on_error_callback(self)

    def get_rms_from_server(self):
        print("Fetching data from endpoint", self.endpoint)
        try:
            v, success = get_volume_from_server(endpoint=self.endpoint)
            if not success:
                self.on_error()

            self.temp_rms_level = v * 100
            return v
        except Exception as e:
            print("Error fetching data from endpoint", e)

        return 0

    def animate(self):
        # Fetch the audio data from the endpoint
        # and set the rms_level
        self.get_rms_from_server()
        new_value = self.temp_rms_level
        self._rms_level = (
            self._alpha * new_value + (1 - self._alpha) * self._previous_rms_level
        )
        self._previous_rms_level = self._rms_level
        time.sleep(0.05)


def get_volume_from_server(endpoint: str):
    try:
        with requests.get(endpoint) as response:
            if not response.status_code == 200:
                print("Error fetching data from endpoint", response.status_code)
                return 0, False
            print("-" * 40)
            print("JSON Response: ", response.json())
            print("-" * 40)
            data = response.json()
            v = data.get("v", 0)
            return v, True

    except Exception as e:
        print("Error fetching data from endpoint", e)

    return 0, False


async def update_decoder_rms(decoder: HttpAudioDecoder):
    print("Fetching data from endpoint", decoder.endpoint)
    try:
        v, success = get_volume_from_server(endpoint=decoder.endpoint)
        decoder.temp_rms_level = v

    except Exception as e:
        print("Error fetching data from endpoint", e)

    return 0
