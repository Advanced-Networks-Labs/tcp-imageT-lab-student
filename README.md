
# TCP Image Transmission Using Python

## 1. Project Description

This project implements image transmission between a client and a server using TCP sockets in Python.

The objective is to send an image from the client to the server and compare two transmission methods:

- **Normal Mode:** Sends the image data using a small number of `sendall()` calls.
- **Pixel-by-Pixel Mode:** Sends the image one pixel at a time.

## 2. Technologies Used

- Python
- TCP Sockets
- OpenCV (cv2)
- NumPy
- Struct
- Time

## 3. Project Files

- `client_raw.py`: Generates and sends the image.
- `server_raw.py`: Receives and reconstructs the image.
- `README.md`: Project documentation.

## 4. How to Run the Project

### Step 1: Install the required libraries

```bash
pip install numpy opencv-python
```

### Step 2: Start the server

```bash
python server_raw.py
```

### Step 3: Start the client

Open another terminal and execute:

```bash
python client_raw.py
```

## 5. Transmission Modes

The transmission mode is selected in the client code:

```python
MODE = "normal"
```

To test Pixel-by-Pixel mode, change it to:

```python
MODE = "pixel"
```

The server must be restarted before each new test.

## 6. Performance Evaluation

The project evaluates the following parameters:

- Transfer Time: Time required to send and receive the image data.
- Throughput: Amount of data transferred per second.
- Number of Send Calls: Number of `sendall()` calls made by the client.
- Packet Loss: Not directly measured by this application. TCP provides reliable and ordered data delivery.

## 7. Expected Results

Normal Mode uses fewer send calls and is expected to be faster.

Pixel-by-Pixel Mode uses many send calls and is expected to take more time.

The actual performance results depend on the computer and network conditions.

## 8. Conclusion

This project demonstrates image transmission using TCP sockets in Python and compares two different sending methods. The experiment illustrates how the number of sending operations can affect transmission performance.
