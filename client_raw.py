import os
import socket
import struct
import time

import cv2
import numpy as np

   # Nom : FAKROUNE
   # Prenom : Fakhreddine
   # Groupe : master 1 G1

SERVER_IP = '127.0.0.1'
PORT = 8080
IMAGE_PATH = 'test_image.png'
WIDTH, HEIGHT = 640, 480

# 'raw'   -> header + the whole payload in one sendall()
# 'pixel' -> header, then every pixel in its own sendall() call
MODE = 'pixel'


def generate_test_image(image_path, width, height):
    # 1. Blank dark-gray canvas (BGR format)
    image = np.full((height, width, 3), 40, dtype=np.uint8)

    # 2. Diagonal-ish color gradient (vectorised, much faster than nested loops)
    image[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)[None, :]    # Blue: left -> right
    image[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, None]   # Green: top -> bottom

    # 3. Geometric shapes
    cv2.circle(image, (width // 2, height // 2), 80, (0, 0, 255), -1)       # Red circle
    cv2.rectangle(image, (50, 50), (200, 150), (0, 255, 255), 3)            # Yellow rectangle
    cv2.line(image, (50, height - 50), (width - 50, height - 50), (0, 255, 0), 4)  # Green line

    # 4. Text overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, 'TCP IMAGE TEST', (width // 2 - 140, 60), font, 1.0, (255, 255, 255), 2)
    cv2.putText(image, f'{width}x{height} px', (width // 2 - 60, height // 2 + 120), font, 0.7, (255, 255, 255), 1)

    # 5. Save
    cv2.imwrite(image_path, image)
    print(f"Test image successfully generated and saved as '{image_path}' ({width}x{height} pixels).")


def send_pixel_by_pixel(sock, header, img):
    """Send the header, then every pixel in its own sendall() call.

    Pixels are sent row by row (top to bottom, left to right).
    Each pixel is `channels` bytes (BGR order for a colour image, as read by OpenCV).
    """
    height, width, _ = img.shape
    sock.sendall(header)
    calls = 1
    for y in range(height):
        for x in range(width):
            sock.sendall(img[y, x].tobytes())
            calls += 1
    return calls


def run_client():
    # TODO 1: Prepare the generated test image
    if not os.path.exists(IMAGE_PATH):
        generate_test_image(IMAGE_PATH, WIDTH, HEIGHT)

    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(f"Error: {IMAGE_PATH} not found.")
        return

    # TODO 2: specifying height, width and channels from image shape
    height, width, channels = img.shape

    payload = img.tobytes()
    payload_length = len(payload)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Disable Nagle's algorithm so that small sends are not merged
    # by TCP into larger segments (true pixel-by-pixel transmission).
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    client_socket.connect((SERVER_IP, PORT))
    print(f"Connected to server at {SERVER_IP}:{PORT} (mode: {MODE})")

    try:
        start_time = time.time()

        # TODO 3: Fixed-size header: height (2 bytes) + width (2 bytes) + payload length (4 bytes)
        # '>' = big-endian (network byte order), H = unsigned short (2 bytes), I = unsigned int (4 bytes)
        header = struct.pack('>HHI', height, width, payload_length)

        # TODO 4: Transmit header and raw pixel data
        if MODE == 'pixel':
            calls = send_pixel_by_pixel(client_socket, header, img)
        else:
            client_socket.sendall(header + payload)
            calls = 1

        elapsed = time.time() - start_time
        throughput = (payload_length / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0

        print(f"Sent raw image {width}x{height}x{channels} "
              f"({payload_length} bytes) in {elapsed:.4f} seconds "
              f"using {calls} send call(s) ({throughput:.2f} MB/s).")

    finally:
        client_socket.close()


if __name__ == '__main__':
    run_client()
