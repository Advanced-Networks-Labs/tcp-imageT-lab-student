
import socket
import struct
import time
import cv2
import numpy as np

PORT = 8080
HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length


# TODO 4: Receive exactly n bytes
def recv_exact(sock, n):

    data = b''

    while len(data) < n:
        packet = sock.recv(n - len(data))

        if not packet:
            return None

        data += packet

    return data


def run_server():

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)

    print(f"Server listening on port {PORT}...")

    conn, addr = server_socket.accept()

    print(f"Connection established with {addr}")

    try:

        # Wait for first byte without consuming it
        if not conn.recv(1, socket.MSG_PEEK):
            print("Client closed the connection without sending data.")
            return

        start_time = time.time()

        # TODO 5: Read exact header
        header = recv_exact(conn, HEADER_SIZE)

        if header is None:
            print("Error: Connection closed before header was received.")
            return

        # TODO 6: Unpack header
        height, width, payload_length = struct.unpack('!HHI', header)

        print(
            f"Header received: {width}x{height}, "
            f"payload = {payload_length} bytes"
        )

        # Validate dimensions
        pixels = height * width

        if pixels == 0 or payload_length % pixels != 0:
            print("Error: payload length does not match dimensions.")
            return

        channels = payload_length // pixels

        if channels not in (1, 3, 4):
            print("Error: Invalid number of image channels.")
            return

        # TODO 7: Read exact image payload
        payload = recv_exact(conn, payload_length)

        if payload is None:
            print("Error: Connection closed before full image arrived.")
            return

        end_time = time.time()

        # TODO 8: Reconstruct image
        img = np.frombuffer(payload, dtype=np.uint8)

        img = img.reshape((height, width, channels))

        print("Image successfully reconstructed!")

        # Display received image
        cv2.imshow("Received TCP Image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # TODO 9: Calculate network performance metrics

        elapsed = end_time - start_time

        latency_ms = elapsed * 1000

        # TCP does not expose packet loss directly.
        # No retransmission information is collected here.
        packet_loss = 0.0

        throughput_kbps = (payload_length / 1024) / elapsed if elapsed > 0 else 0

        print(
            f"Raw Transfer Complete | "
            f"Size: {HEADER_SIZE + payload_length} bytes"
        )

        print(
            f"Metrics | Latency: {latency_ms:.3f} ms | "
            f"Packet loss: {packet_loss:.2f} % | "
            f"Throughput: {throughput_kbps:.2f} KB/s"
        )

    except Exception as e:
        print("Server error:", e)

    finally:

        conn.close()
        server_socket.close()

        cv2.destroyAllWindows()

        print("Server closed.")


if __name__ == '__main__':
    run_server()
