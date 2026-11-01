import socket
import struct
import time
import cv2
import numpy as np

HOST = "0.0.0.0"
PORT = 8080

HEADER_SIZE = 8
MAX_IMAGE_BYTES = 50 * 1024 * 1024


def recv_exact(sock, size):

    data = bytearray()

    while len(data) < size:

        chunk = sock.recv(size - len(data))

        if not chunk:
            return None

        data.extend(chunk)

    return bytes(data)


def run_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen(1)

    print("Server is listening on port", PORT)

    try:

        conn, address = server.accept()

        with conn:

            print("Connected with:", address)

            first_byte = conn.recv(1, socket.MSG_PEEK)

            if not first_byte:
                print("No data received.")
                return

            start_time = time.perf_counter()

            header = recv_exact(conn, HEADER_SIZE)

            if header is None:
                print("Error receiving header.")
                return

            height, width, payload_size = struct.unpack(
                "!HHI",
                header
            )

            print("Image:", width, "x", height)
            print("Payload:", payload_size, "bytes")

            if height == 0 or width == 0:
                print("Invalid image dimensions.")
                return

            if payload_size == 0 or payload_size > MAX_IMAGE_BYTES:
                print("Invalid image size.")
                return

            if payload_size % (height * width) != 0:
                print("Invalid image data.")
                return

            channels = payload_size // (height * width)

            if channels not in (1, 3, 4):
                print("Unsupported number of channels.")
                return

            payload = recv_exact(conn, payload_size)

            if payload is None:
                print("Incomplete image received.")
                return

            end_time = time.perf_counter()

            elapsed = end_time - start_time

            image_array = np.frombuffer(
                payload,
                dtype=np.uint8
            )

            if channels == 1:
                image = image_array.reshape((height, width))
            else:
                image = image_array.reshape(
                    (height, width, channels)
                )

            cv2.imwrite("received_image.png", image)

            print("Image received successfully!")
            print("Transfer time:", round(elapsed, 4), "seconds")
            print("Throughput:", round((payload_size / 1024) / elapsed, 2), "KB/s")
            print("Packet loss: Not measured (TCP provides reliable delivery)")
            print("Image saved as received_image.png")

            try:
                cv2.imshow("Received Image", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            except cv2.error:
                print("Image saved, but display is not available.")

    except Exception as error:
        print("Server error:", error)

    finally:
        server.close()


if __name__ == "__main__":
    run_server()