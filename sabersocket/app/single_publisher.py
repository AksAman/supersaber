import random
import time

import click
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(rc))
    client.subscribe(userdata["topic"])


def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")


def on_publish(client, userdata, mid):
    print("Message Published...")


@click.command()
@click.option(
    "--broker",
    type=click.Choice(["mosquitto", "emqx"]),
    required=True,
    help="MQTT broker to use",
)
@click.option(
    "--role",
    type=click.Choice(["publisher", "consumer"]),
    required=True,
    help="Role: publisher or consumer",
)
@click.option("--message", type=str, default="", help="Message to publish (only for publisher)")
@click.option(
    "--count",
    type=int,
    default=1,
    help="Number of messages to publish (only for publisher)",
)
@click.option(
    "--delay",
    type=float,
    default=1.0,
    help="Delay between messages in seconds (only for publisher)",
)
@click.option(
    "--topic",
    type=str,
    default="test-topic",
    help="Topic to subscribe/publish (only for publisher)",
)
def mqtt_cli(broker, role, message, count, delay, topic):
    if broker == "mosquitto":
        host = "localhost"
        port = 1883
    elif broker == "emqx":
        host = "localhost"
        port = 1885

    client = mqtt.Client(userdata={"topic": topic})

    if role == "consumer":
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(host, port, 60)
        client.loop_forever()
    elif role == "publisher":
        client.on_publish = on_publish
        client.connect(host, port, 60)
        client.loop_start()
        i = 0
        while count == -1 or i < count:
            print(f"Publishing message: {message} on topic: {topic}")
            client.publish(topic, message)
            if count > 1:
                time.sleep(delay)
            i += 1
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    mqtt_cli()
