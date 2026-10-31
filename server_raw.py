import socket
import struct
import time

import cv2
import numpy as np

PORT = 8080

HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length


def recv_exact(sock, n):
    """TODO 4: Implement a robust helper that reads exactly n bytes from a TCP stream.

    TCP is a byte stream: one recv() may return fewer bytes than requested,
    so we loop until we have n bytes. Returns None if the peer closes early.
    """
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(min(65536, n - len(buf)))
        if not chunk:          # connection closed before n bytes arrived
            return None
        buf.extend(chunk)
    return bytes(buf)


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
        # Stop with an error message if the connection closed before the full header arrived.
        header = recv_exact(conn, HEADER_SIZE)
        if header is None:
            print("Error: connection closed before the full header was received.")
            return

        # TODO 6: Unpack the header fields using struct.unpack()
        # Same format as the client: height (H), width (H), payload length (I), network byte order
        height, width, payload_length = struct.unpack('!HHI', header)

        print(f"Header received: {width}x{height}, payload = {payload_length} bytes")

        pixels = height * width
        if pixels == 0 or payload_length % pixels != 0:
            print("Error: payload length does not match the image dimensions.")
            return

        # TODO 7: Read the exact payload bytes (payload_length) using recv_exact.
        # Stop with an error message if the connection closed before the full image arrived.
        payload = recv_exact(conn, payload_length)
        if payload is None:
            print("Error: connection closed before the full image was received.")
            return

        end_time = time.time()

        # TODO 8: Reconstruct the raw numpy array and reshape it to (height, width, channels).
        channels = payload_length // pixels
        img = np.frombuffer(payload, dtype=np.uint8).reshape((height, width, channels))

        # Save the received image so it can be checked visually / compared with the original.
        cv2.imwrite('received_image.png', img)
        print("Received image saved as 'received_image.png'")

        # TODO 9: Calculate and log network performance metrics (Latency, Packet loss, Throughput KB/s)
        total_bytes = HEADER_SIZE + payload_length
        elapsed = end_time - start_time

        # Latency: total time (ms) from the first byte arriving until the last byte of the image.
        latency_ms = elapsed * 1000

        # Packet loss: % of expected bytes that never arrived. recv_exact guarantees we got
        # everything (TCP retransmits lost segments), so this is 0 % at application level.
        received_bytes = HEADER_SIZE + len(payload)
        packet_loss = (1 - received_bytes / total_bytes) * 100

        # Throughput in KB/s
        throughput_kbps = (total_bytes / 1024) / elapsed

        print(f"Raw Transfer Complete | Size: {HEADER_SIZE + payload_length} bytes")
        print(f"Metrics | Latency: {latency_ms:.3f} ms | Packet loss: {packet_loss:.2f} % | "
              f"Throughput: {throughput_kbps:.2f} KB/s")

    finally:
        conn.close()
        server_socket.close()


if __name__ == '__main__':
    run_server()
