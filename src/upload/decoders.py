import random
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


pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
rssi = wifi.radio.ap_info.rssi

ssid = wifi.radio.ap_info.ssid
print(f"SSID: {ssid}")
print(f"RSSI: {rssi}")


class HttpAudioDecoder(CustomDecoder):

    def __init__(self, endpoint: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.temp_rms_level = 0
        # return if wifi is not connected
        if not wifi.radio.connected:
            print("Wifi is not connected")
            return

    def get_rms_from_server(self):
        print("Fetching data from endpoint", self.endpoint)
        try:
            with requests.get(self.endpoint) as response:
                print("-" * 40)
                print("JSON Response: ", response.json())
                print("-" * 40)
                data = response.json()
                rms = data.get("v", 0)
                self.temp_rms_level = rms * 100
                return rms
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


async def update_decoder_rms(decoder: HttpAudioDecoder):
    print("Fetching data from endpoint", decoder.endpoint)
    try:
        with requests.get(decoder.endpoint) as response:
            print("-" * 40)
            print("JSON Response: ", response.json())
            print("-" * 40)
            data = response.json()
            rms = data.get("v", 0)
            decoder.temp_rms_level = rms * 100
            print("get rms:", rms)
            return rms

    except Exception as e:
        print("Error fetching data from endpoint", e)

    return 0
