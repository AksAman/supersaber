import json
import random
import ssl
import time

import adafruit_connection_manager
import adafruit_requests
import socketpool
import wifi
from config import REQUEST_TIMEOUT


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
        self._rms_level = self._alpha * new_value + (1 - self._alpha) * self._previous_rms_level
        self._previous_rms_level = self._rms_level

    def reset(self):
        self._rms_level = 0
        self._previous_rms_level = 0


pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
if wifi.radio.ap_info:
    rssi = wifi.radio.ap_info.rssi
    ssid = wifi.radio.ap_info.ssid
    address = wifi.radio.ipv4_address
    print(f"SSID: {ssid}")
    print(f"RSSI: {rssi}")
    print(f"address: {address}")


class HttpAudioDecoder(CustomDecoder):

    def __init__(self, endpoint: str, on_error_callback=None, error_threshold=3, *args, **kwargs):
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
        try:
            v, success = get_volume_from_server(endpoint=self.endpoint)
            if not success:
                self.on_error()

            self.temp_rms_level = v * 100
            return v
        except Exception as e:
            print("Error fetching data from endpoint", e)
            self.on_error()

        return 0

    def animate(self):
        # Fetch the audio data from the endpoint
        # and set the rms_level
        self.get_rms_from_server()
        new_value = self.temp_rms_level
        self._rms_level = self._alpha * new_value + (1 - self._alpha) * self._previous_rms_level
        self._previous_rms_level = self._rms_level
        time.sleep(0.005)


def get_volume_from_server(endpoint: str):
    try:
        response = requests.get(endpoint, timeout=REQUEST_TIMEOUT)
        print(response.status_code)
        if not response.status_code == 200:
            print("Error fetching data from endpoint", endpoint, response.status_code)
            return 0, False
        data = response.json()
        v = data.get("v", 0)
        print("Fetched data from endpoint", endpoint, v)
        return v, True
    except Exception as e:
        print("Error fetching data from endpoint", endpoint, e)

    return 0, False


async def update_decoder_rms(decoder: HttpAudioDecoder):
    try:
        v, success = get_volume_from_server(endpoint=decoder.endpoint)
        decoder.temp_rms_level = v

    except Exception as e:
        print("Error fetching data from endpoint", e)

    return 0


class WebsocketAudioDecoder(HttpAudioDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_ws()

    def reset(self):
        super().reset()
        self.setup_ws()

    def setup_ws(self):
        from websockets import Session  # type: ignore

        socket = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        self.wsession = Session(socket, ssl=ssl_context, iface=None)
        print(f"endpoint: {self.endpoint}")
        self.ws_client = self.wsession.client(self.endpoint)

    def get_volume_from_server(self):
        try:
            result = self.ws_client.recv()
            data = json.loads(result)
            # print(f"RECEIVED: <{result}>")
            v = data.get("v", 0)
            # print(f"\t parsed: v:{v}")
            return v, True
        except Exception:
            self.on_error()
            return 0, False

    def get_rms_from_server(self):
        try:
            v, success = self.get_volume_from_server()
            if not success:
                self.on_error()

            self.temp_rms_level = v * 100
            return v
        except Exception as e:
            print("Error fetching data from endpoint", e)
            self.on_error()

        return 0


class MQTTAudioDecoder(CustomDecoder):
    def __init__(
        self,
        host: str,
        port: int,
        topics: list[str],
        username: str | None = None,
        password: str | None = None,
        on_message_callback=None,
        on_value_callback=None,
        on_error_callback=None,
        use_smoothing: bool = True,
        error_threshold=3,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.topics = topics
        self.username = username
        self.password = password
        self.temp_rms_level = 0
        self.error_count = 0
        self.error_threshold = error_threshold
        self.on_message_callback = on_message_callback
        self.on_error_callback = on_error_callback
        self.on_value_callback = on_value_callback
        self.use_smoothing = use_smoothing
        self.socket_timeout = 0.15
        self.client = self.init_mqtt_publisher()
        self.last_time = time.monotonic()

    def on_connect(self, mqtt_client, userdata, flags, rc):
        # This function will be called when the mqtt_client is connected
        # successfully to the broker.
        print("Connected to MQTT Broker!")
        print("Flags: {0}\n RC: {1}".format(flags, rc))

    def on_disconnect(self, mqtt_client, userdata, rc):
        # This method is called when the mqtt_client disconnects
        # from the broker.
        print("Disconnected from MQTT Broker!")

    def on_subscribe(self, mqtt_client, userdata, topic, granted_qos):
        # This method is called when the mqtt_client subscribes to a new feed.
        print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

    def on_unsubscribe(self, mqtt_client, userdata, topic, pid):
        # This method is called when the mqtt_client unsubscribes from a feed.
        print("Unsubscribed from {0} with PID {1}".format(topic, pid))

    def on_publish(self, mqtt_client, userdata, topic, pid):
        # This method is called when the mqtt_client publishes data to a feed.
        print("Published to {0} with PID {1}".format(topic, pid))

    def on_message(self, client, topic, message):
        try:
            if self.on_message_callback:
                self.on_message_callback(topic, message)

            # new_time = time.monotonic()
            # passed = new_time - self.last_time
            # print("\t -------- on_message loop", passed)
            # self.last_time = new_time
            v = float(message)
            # data = json.loads(message)
            # v = data.get("v", 0)
            # now = time.time()
            # print(f"\t {now} parsed: v:{v}")
            # self._rms_level = v
            if self.use_smoothing:
                new_value = v
                self._rms_level = self._alpha * new_value + (1 - self._alpha) * self._previous_rms_level
                self._previous_rms_level = self._rms_level
            else:
                self._rms_level = v

            if self.on_value_callback:
                self.on_value_callback(self._rms_level)
        except Exception as e:
            print(f"Error parsing message: {message}, {e}")
            self.on_error()

    def init_mqtt_publisher(self):
        import adafruit_minimqtt.adafruit_minimqtt as MQTT

        pool = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        client = MQTT.MQTT(
            broker=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            socket_pool=pool,
            ssl_context=ssl_context,
            socket_timeout=self.socket_timeout,
        )
        client.on_connect = self.on_connect  # type: ignore
        client.on_disconnect = self.on_disconnect  # type: ignore
        client.on_subscribe = self.on_subscribe  # type: ignore
        client.on_unsubscribe = self.on_unsubscribe  # type: ignore
        client.on_publish = self.on_publish  # type: ignore
        client.on_message = self.on_message

        client.connect()
        for topic in self.topics:
            client.subscribe(topic)
            print(f"\t Subscribed to {topic}")
        return client

    def loop(self):
        self.client.loop(timeout=self.socket_timeout)

    def reset(self):
        self.error_count = 0
        self.client.disconnect()
        self.client = self.init_mqtt_publisher()
        super().reset()

    def on_error(self):
        self.error_count += 1
        if self.error_count >= self.error_threshold and self.on_error_callback:
            self.on_error_callback(self)

    def animate(self):
        # Fetch the audio data from the endpoint
        # and set the rms_level
        new_value = self.temp_rms_level
        self._rms_level = self._alpha * new_value + (1 - self._alpha) * self._previous_rms_level
        self._previous_rms_level = self._rms_level


class UDPAudioDecoder(CustomDecoder):
    def __init__(
        self,
        host: str,
        port: int,
        on_value_callback=None,
        on_error_callback=None,
        error_threshold=3,
        sleep_time=0.005,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.temp_rms_level = 0
        self.error_count = 0
        self.on_value_callback = on_value_callback
        self.error_threshold = error_threshold
        self.on_error_callback = on_error_callback
        self.sleep_time = sleep_time
        self.udp_size = 1024
        self.udp_buffer = bytearray(self.udp_size)
        self.sock = self.init_udp_socket()

    def init_udp_socket(self):
        pool = socketpool.SocketPool(wifi.radio)

        sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)  # UDP socket
        sock.bind((self.host, self.port))
        print(f"UDP socket bound to {self.host}:{self.port}")
        return sock

    def on_error(self):
        self.error_count += 1
        if self.error_count >= self.error_threshold and self.on_error_callback:
            self.on_error_callback(self)

    def get_rms_from_server(self):
        try:
            self.udp_buffer = bytearray(self.udp_size)
            data, addr = self.sock.recvfrom_into(self.udp_buffer)
            print(f"data: {data}, addr: {addr}")
            if not data:
                return 0, False

            v = float(data)
            if self.on_value_callback:
                self.on_value_callback(v)
            return v, True
        except Exception:
            self.on_error()
            return 0, False

    def animate(self):
        # Fetch the audio data from the endpoint
        # and set the rms_level
        v, success = self.get_rms_from_server()
        if not success:
            return

        new_value = v
        self._rms_level = self._alpha * new_value + (1 - self._alpha) * self._previous_rms_level
        self._previous_rms_level = self._rms_level

    def loop(self):
        print("looping")
        self.animate()
        time.sleep(self.sleep_time)
