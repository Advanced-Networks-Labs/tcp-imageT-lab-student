import socket
import struct
import time
import cv2
import numpy as np

SERVER_IP = "127.0.0.1"
PORT = 8080

IMAGE_PATH = "test_image.png"

HEADER_SIZE = 8

# Choose: "normal" or "pixel"
MODE = "pixel"


def generate_test_image():
    image = np.zeros((480, 640, 3), dtype=np.uint8)

    for y in range(480):
        for x in range(640):
            image[y, x] = [
                int(x * 255 / 640),
                int(y * 255 / 480),
                150
            ]

    cv2.putText(
        image,
        "TCP IMAGE TRANSMISSION",
        (80, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    cv2.imwrite(IMAGE_PATH, image)


def send_pixel_by_pixel(client_socket, image, header):
    client_socket.sendall(header)
    send_calls = 1

    height, width, channels = image.shape

    for y in range(height):
        for x in range(width):
            pixel = image[y, x].tobytes()
            client_socket.sendall(pixel)
            send_calls += 1

    return send_calls


def run_client():

    generate_test_image()

    image = cv2.imread(IMAGE_PATH)

    if image is None:
        print("Error: Cannot read image.")
        return

    height, width, channels = image.shape

    payload = image.tobytes()
    payload_size = len(payload)

    header = struct.pack(
        "!HHI",
        height,
        width,
        payload_size
    )

    print("Image:", width, "x", height)
    print("Payload:", payload_size, "bytes")
    print("Mode:", MODE)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER_IP, PORT))

        start_time = time.perf_counter()

        if MODE == "normal":
            client.sendall(header)
            client.sendall(payload)
            send_calls = 2

        elif MODE == "pixel":
            send_calls = send_pixel_by_pixel(
                client,
                image,
                header
            )

        else:
            print("Invalid mode!")
            return

        end_time = time.perf_counter()

        elapsed = end_time - start_time

        throughput = (payload_size / 1024) / elapsed

        print("Send calls:", send_calls)
        print("Transfer time:", round(elapsed, 4), "seconds")
        print("Throughput:", round(throughput, 2), "KB/s")
        print("Image sent successfully!")

    except Exception as error:
        print("Error:", error)

    finally:
        client.close()


if __name__ == "__main__":
    run_client()