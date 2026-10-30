import os
import socket
import struct
import time

import cv2
import numpy as np

SERVER_IP = '127.0.0.1'
PORT = 8080
IMAGE_PATH = 'test_image.png'
HEADER_FORMAT = '!HHI'   # network byte order: height (2B), width (2B), payload length (4B)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # = 8
MODE = 'bulk'            # 'bulk' = header + whole payload; 'pixel' = one sendall() per pixel


def generate_test_image(image_path, width, height):
    # 1. Create a blank dark-gray canvas (BGR format)
    image = np.full((height, width, 3), 40, dtype=np.uint8)

    # 2. Diagonal color gradient across the background (numpy: same values as the nested loops)
    xs = (np.arange(width) / width * 255).astype(np.uint8)     # blue: left -> right
    ys = (np.arange(height) / height * 255).astype(np.uint8)   # green: top -> bottom
    image[:, :, 0] = xs[np.newaxis, :]
    image[:, :, 1] = ys[:, np.newaxis]

    # 3. Draw geometric shapes
    cv2.circle(image, (width // 2, height // 2), 80, (0, 0, 255), -1)       # red circle
    cv2.rectangle(image, (50, 50), (200, 150), (0, 255, 255), 3)            # yellow rectangle
    cv2.line(image, (50, height - 50), (width - 50, height - 50), (0, 255, 0), 4)  # green line

    # 4. Text overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, 'TCP IMAGE TEST', (width // 2 - 140, 60), font, 1.0, (255, 255, 255), 2)
    cv2.putText(image, f'{width}x{height} px', (width // 2 - 60, height // 2 + 120),
                font, 0.7, (255, 255, 255), 1)

    # 5. Save the image file
    cv2.imwrite(image_path, image)
    print(f"Test image successfully generated and saved as '{image_path}' ({width}x{height} pixels).")


def send_pixel_by_pixel(sock, header, img):
    """Send the header, then every pixel in its own sendall() call.

    Pixels are sent row by row (top to bottom, left to right).
    Each pixel is `channels` bytes (BGR order for a colour image, as read by OpenCV).
    Returns the number of sendall() calls made.
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
        generate_test_image(IMAGE_PATH, 640, 480)

    img = cv2.imread(IMAGE_PATH, cv2.IMREAD_COLOR)   # always 3 channels (BGR)
    if img is None:
        print(f"Error: {IMAGE_PATH} not found.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Disable Nagle's algorithm so that small sends are not merged
    # by TCP into larger segments (true pixel-by-pixel transmission).
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    client_socket.connect((SERVER_IP, PORT))
    print(f"Connected to server at {SERVER_IP}:{PORT} (mode: {MODE})")

    # TODO 2: specifying height, width and channels from image shape
    height, width, channels = img.shape

    payload = img.tobytes()
    payload_length = len(payload)   # = height * width * channels

    try:
        start_time = time.time()

        # TODO 3: Construct fixed-size header specifying height (2 bytes), width (2 bytes)
        # and payload length (4 bytes) using struct.pack()
        header = struct.pack(HEADER_FORMAT, height, width, payload_length)

        # TODO 4: Transmit header and raw pixel data
        if MODE == 'pixel':
            calls = send_pixel_by_pixel(client_socket, header, img)
        else:
            client_socket.sendall(header)
            client_socket.sendall(payload)
            calls = 2

        elapsed = time.time() - start_time
        total_bytes = HEADER_SIZE + payload_length
        throughput = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else float('inf')

        print(f"Sent raw image {width}x{height}x{channels} "
              f"({payload_length} bytes) in {elapsed:.4f} seconds "
              f"using {calls} send call(s) ({throughput:.2f} MB/s).")

    finally:
        client_socket.close()


if __name__ == '__main__':

    run_client()
