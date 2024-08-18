import socket

from sabersocket.app.protocols.base import Publisher


class UDPPublisher(Publisher):
    def __init__(self, host: str, port: int):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

    @property
    def broker_address(self):
        return (self.host, self.port)

    def connect(self):
        pass  # No connection needed for UDP

    def publish(self, topic: str, payload: str):
        self.udp_socket.sendto(payload.encode(), self.broker_address)

    def disconnect(self):
        self.udp_socket.close()
