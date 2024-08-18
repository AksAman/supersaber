import socket

from sabersocket.app.settings import UDP_BROKER_HOST, UDP_BROKER_PORT

# Define the host and port to listen on


def main():
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the host and port
    udp_socket.bind((UDP_BROKER_HOST, UDP_BROKER_PORT))

    print(f"Listening for UDP packets on {UDP_BROKER_HOST}:{UDP_BROKER_PORT}...")

    try:
        while True:
            # Receive data from the socket
            data, addr = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Received message: {data.decode()} from {addr}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        udp_socket.close()


if __name__ == "__main__":
    main()
