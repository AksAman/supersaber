import paho.mqtt.client as mqtt

from sabersocket.app.audio.calculator import init_ear, list_devices, run_fft_on_audio
from sabersocket.app.logger import logger
from sabersocket.app.settings import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC, RMS_THRESHOLD, WLED_TOPIC


def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None):
    logger.info("Connected with result code " + str(rc) + " flags: " + str(flags) + userdata)
    client.subscribe(MQTT_TOPIC)
    client.subscribe(WLED_TOPIC)


def on_message(client, userdata, msg):
    pass
    # logger.info(f">>> Received message: {msg.payload.decode()} on topic {msg.topic}")


def on_publish(client, userdata, mid, reason_code, properties):
    logger.info("<<< Message Published...")


def on_disconnect(client, userdata, rc, *args, **kwargs):
    logger.info("Disconnected with result code " + str(rc))


def init_mqtt_publisher():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish
    return client


def map(val, in_min, in_max, out_min, out_max):
    return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def main():
    client = init_mqtt_publisher()
    client.connect(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, keepalive=60)
    print("Connected to MQTT Broker...")

    try:
        list_devices()
        # device = int(input("Enter the audio device: "))
        ear = init_ear()

        def on_data_callback(data):
            average_magnitude, max_magnitude, min_magnitude, rms, volume_normalized = data
            logger.debug(
                f"last_max: {RMS_THRESHOLD}, rms: {rms}, average: {average_magnitude}, max: {max_magnitude}, min: {min_magnitude}, volume_normalized: {volume_normalized}"
            )
            data = volume_normalized
            client.publish(MQTT_TOPIC, payload=data)
            VAL = volume_normalized
            if volume_normalized > 0:
                VAL = map(volume_normalized, 0, 10, 0, 255)
            print(f"{VAL=}")
            client.publish(WLED_TOPIC, VAL)

        run_fft_on_audio(ear=ear, on_data_callback=on_data_callback)

        client.loop_forever()

        # while True:
        #     time.sleep(0.01)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
