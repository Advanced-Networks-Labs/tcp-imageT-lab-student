
import socket
import struct
import time
import cv2
import numpy as np

PORT = 8080
HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length


def recv_exact(sock, n):
    """Read exactly n bytes from a TCP stream."""

    data = b''

    while len(data) < n:
        packet = sock.recv(n - len(data))

        if not packet:
            return None

        data += packet

    return data



def run_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)

    print(f"Server listening on port {PORT}...", flush=True)

    try:
        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        with conn:
            start_time = time.time()

            # Read the exact header bytes
            header = recv_exact(conn, HEADER_SIZE)

            if header is None:
                print("Error: Incomplete header received.")
                return

            # Unpack height, width and payload length
            height, width, payload_length = struct.unpack('!HHI', header)

            print(f"Header received: {width}x{height}, payload = {payload_length} bytes")

            pixels = height * width

            if pixels == 0 or payload_length % pixels != 0:
                print("Error: Invalid image dimensions or payload length.")
                return

            channels = payload_length // pixels

            if channels not in (1, 3, 4):
                print("Error: Unsupported number of channels.")
                return

            # Receive the image payload
            payload = recv_exact(conn, payload_length)

            if payload is None:
                print("Error: Incomplete image received.")
                return

            # Reconstruct the image
            image = np.frombuffer(payload, dtype=np.uint8)

            if channels == 1:
                received_image = image.reshape((height, width))
            else:
                received_image = image.reshape((height, width, channels))

            # Calculate performance metrics
            elapsed = time.time() - start_time
            latency_ms = elapsed * 1000
            packet_loss = 0.0

            throughput_kbps = (payload_length / 1024) / elapsed if elapsed > 0 else 0.0

            print(f"Raw Transfer Complete | Size: {HEADER_SIZE + payload_length} bytes")
            print(
                f"Metrics | Latency: {latency_ms:.3f} ms | "
                f"Packet loss: {packet_loss:.2f} % | "
                f"Throughput: {throughput_kbps:.2f} KB/s"
            )

            # Save the received image
            success = cv2.imwrite("received_image.png", received_image)

            if success:
                print("Image saved successfully!")
                print("Saved at:", __import__("os").path.abspath("received_image.png"))
            else:
                print("Error: Could not save the image.")

    finally:
        server_socket.close()


if __name__ == '__main__':
    run_server()
