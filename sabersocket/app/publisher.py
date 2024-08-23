import sys
from typing import Literal

from sabersocket.app.audio.calculator import init_ear, list_devices, run_fft_on_audio
from sabersocket.app.logger import logger
from sabersocket.app.protocols.base import Publisher
from sabersocket.app.protocols.mqtt_publisher import MQTTPublisher
from sabersocket.app.protocols.udp_publisher import UDPPublisher
from sabersocket.app.settings import (
    BOOSTER,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPIC,
    RMS_THRESHOLD,
    UDP_BROKER_HOST,
    UDP_BROKER_PORT,
    WLED_TOPIC,
)


def map(val, in_min, in_max, out_min, out_max):
    return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def main(publisher: Publisher):
    publisher.connect()
    print("Connected to Broker...")

    try:
        list_devices()
        ear = init_ear()

        zero_published = False

        def on_data_callback(data):
            average_magnitude, max_magnitude, min_magnitude, rms, volume_normalized = data
            data = volume_normalized * BOOSTER
            nonlocal zero_published
            if data == 0.0:
                if not zero_published:
                    publisher.publish(MQTT_TOPIC, str(data))
                    zero_published = True

                logger.debug("No sound detected")
                return
            logger.debug(
                f"last_max: {RMS_THRESHOLD}, rms: {rms}, average: {average_magnitude}, max: {max_magnitude}, min: {min_magnitude}, volume_normalized: {volume_normalized}"
            )
            publisher.publish(MQTT_TOPIC, str(data))

            VAL = volume_normalized
            if volume_normalized > 0:
                VAL = map(volume_normalized, 0, 10, 0, 255)
            logger.debug(f"{VAL=}")
            publisher.publish(WLED_TOPIC, str(VAL))

        run_fft_on_audio(ear=ear, on_data_callback=on_data_callback)

        while True:
            pass  # Keep the script running

    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        logger.error("Exiting...")
    finally:
        publisher.disconnect()


if __name__ == "__main__":
    args = sys.argv
    protocol: Literal["udp", "mqtt"] | None = None
    if len(args) > 1:
        if args[1] == "udp":
            protocol = "udp"
        elif args[1] == "mqtt":
            protocol = "mqtt"
        else:
            print("Invalid argument. Use 'udp' or 'mqtt'")
            sys.exit(1)
    else:
        print("No argument provided. exiting...")
        sys.exit(1)

    # Choose the publisher type here
    use_mqtt = protocol == "mqtt"
    if use_mqtt:
        print("Using MQTT Publisher...")
        publisher = MQTTPublisher(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    else:
        print("Using UDP Publisher...")
        publisher = UDPPublisher(host=UDP_BROKER_HOST, port=UDP_BROKER_PORT)
    main(publisher)
