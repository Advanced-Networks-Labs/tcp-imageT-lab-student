import cv2
import socket
import struct
import time

SERVER_IP = '127.0.0.1'
PORT = 8080
IMAGE_PATH = 'sample_image.png'

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    print(f"Connected to server at {SERVER_IP}:{PORT}")

    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print("Error: sample_image.png not found.")
        return

    height, width, channels = img.shape
    payload = img.tobytes()
    payload_length = len(payload)

    try:
        start_time = time.time()

        # TODO 1: Construct a fixed-size header specifying height (2 bytes), 
        # width (2 bytes), and payload_length (4 bytes) using struct '!H H I'
        # header = struct.pack(...)
        raise NotImplementedError("TODO 1: Implement header packing for raw image dimensions and length")

        # TODO 2: Transmit header and raw pixel payload via TCP socket using sendall()
        # client_socket.sendall(header + payload)
        raise NotImplementedError("TODO 2: Implement reliable TCP transmission for raw pixels")

        elapsed = time.time() - start_time
        print(f"Sent raw image ({payload_length} bytes) in {elapsed:.4f} seconds.")

    finally:
        client_socket.close()

if __name__ == '__main__':
    run_client()
