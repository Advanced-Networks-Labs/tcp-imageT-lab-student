import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length

def recv_exact(sock, n):
    """TODO 3: Implement a robust helper to read exactly n bytes from a TCP stream 
    to handle fragmentation."""
    pass

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)
    
    print(f"Server listening on port {PORT}...")
    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    try:
        start_time = time.time()

        # TODO 4: Read exact header bytes using recv_exact
        header_bytes = recv_exact(conn, HEADER_SIZE)
        if not header_bytes:
            return

        # TODO 5: Unpack header fields (height, width, payload_length)
        # height, width, payload_length = struct.unpack('!H H I', header_bytes)
        raise NotImplementedError("TODO 4 & 5: Implement header reading and unpacking")

        # TODO 6: Read exact payload bytes based on payload_length
        payload_bytes = recv_exact(conn, payload_length)

        # TODO 7: Reconstruct the raw numpy array and reshape to (height, width, 3)
        # reconstructed_img = np.frombuffer(payload_bytes, dtype=np.uint8).reshape((height, width, 3))
        raise NotImplementedError("TODO 7: Reconstruct raw pixel array")

        transfer_duration = time.time() - start_time
        print(f"Raw Transfer Complete | Size: {HEADER_SIZE + payload_length} bytes | Time: {transfer_duration:.4f}s")
        
        cv2.imwrite('received_raw_image.png', reconstructed_img)

    finally:
        conn.close()
        server_socket.close()

if __name__ == '__main__':
    run_server()
