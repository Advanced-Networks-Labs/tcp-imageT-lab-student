import socket
import struct
import time
import cv2

PORT = 8080
HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length



def recv_exact(sock, n):
    """TODO 4: Implement a robust helper that reads exactly n bytes from a TCP stream.
    """
    raise NotImplementedError("TODO 4: Implement recv_exact")


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
        raise NotImplementedError("TODO 5: Read the header")

        # TODO 6: Unpack the header fields using struct.unpack()
        raise NotImplementedError("TODO 6: Unpack the header")

        print(f"Header received: {width}x{height}, payload = {payload_length} bytes")

        pixels = height * width
        if pixels == 0 or payload_length % pixels != 0:
            print("Error: payload length does not match the image dimensions.")
            return
       

        # TODO 7: Read the exact payload bytes (payload_length) using recv_exact.
        # Stop with an error message if the connection closed before the full image arrived.
        raise NotImplementedError("TODO 7: Read the payload")

        # TODO 8: Reconstruct the raw numpy array and reshape it to (height, width, channels).
     
        raise NotImplementedError("TODO 8: Reconstruct the raw pixel array")
        
        # TODO 9: Calculate and log network performance metrics (Latency, Packet loss, Throughput KB/s)
        
        raise NotImplementedError("TODO 9: Calculate network performance metrics")
 
        print(f"Raw Transfer Complete | Size: {HEADER_SIZE + payload_length} bytes")
        print(f"Metrics | Latency: {latency_ms:.3f} ms | Packet loss: {packet_loss:.2f} % | "
              f"Throughput: {throughput_kbps:.2f} KB/s")
        

             

    finally:
        conn.close()
        server_socket.close()


if __name__ == '__main__':
    run_server()
