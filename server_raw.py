import socket
import struct
import time

import cv2
import numpy as np

PORT = 8080
HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length

OUTPUT_PATH = 'received.png'


def recv_exact(sock, n):
    """TODO 4: Read exactly n bytes from a TCP stream.

    recv(k) may return fewer than k bytes, so loop until n bytes are collected.
    Returns the bytes, or None if the connection closed before n bytes arrived.
    """
    buffer = bytearray()
    while len(buffer) < n:
        chunk = sock.recv(n - len(buffer))
        if not chunk:          # empty bytes = peer closed the connection
            return None
        buffer.extend(chunk)
    return bytes(buffer)


def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)

    print(f"Server listening on port {PORT}...")
    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    try:
        # Wait for the first byte without consuming it, so the timer measures
        # the transfer itself and not the time the client spends preparing the image.
        if not conn.recv(1, socket.MSG_PEEK):
            print("Client closed the connection without sending data.")
            return
        start_time = time.time()

        # TODO 5: Read the exact header bytes using recv_exact (HEADER_SIZE bytes).
        header = recv_exact(conn, HEADER_SIZE)
        if header is None:
            print("Error: connection closed before the full header arrived.")
            return

        # TODO 6: Unpack the header fields using struct.unpack()
        height, width, payload_length = struct.unpack(HEADER_FORMAT, header)

        print(f"Header received: {width}x{height}, payload = {payload_length} bytes")

        pixels = height * width
        if pixels == 0 or payload_length % pixels != 0:
            print("Error: payload length does not match the image dimensions.")
            return
        channels = payload_length // pixels   # channels are not in the header: derive them

        # TODO 7: Read the exact payload bytes (payload_length) using recv_exact.
        payload = recv_exact(conn, payload_length)
        if payload is None:
            print("Error: connection closed before the full image arrived.")
            return

        # TODO 8: Reconstruct the raw numpy array and reshape it to (height, width, channels).
        img = np.frombuffer(payload, dtype=np.uint8).reshape((height, width, channels))
        cv2.imwrite(OUTPUT_PATH, img)
        print(f"Image reconstructed {img.shape} and saved as '{OUTPUT_PATH}'.")

        # TODO 9: Calculate and log network performance metrics (Latency, Packet loss, Throughput KB/s)
        elapsed = time.time() - start_time
        expected_bytes = HEADER_SIZE + payload_length
        received_bytes = HEADER_SIZE + len(payload)
        latency_ms = elapsed * 1000
        packet_loss = (expected_bytes - received_bytes) / expected_bytes * 100  # 0 on TCP
        throughput_kbps = (received_bytes / 1024) / elapsed if elapsed > 0 else float('inf')

        print(f"Raw Transfer Complete | Size: {HEADER_SIZE + payload_length} bytes")
        print(f"Metrics | Latency: {latency_ms:.3f} ms | Packet loss: {packet_loss:.2f} % | "
              f"Throughput: {throughput_kbps:.2f} KB/s")

    finally:
        conn.close()
        server_socket.close()


if __name__ == '__main__':
    run_server()
