#!/usr/bin/python3

import cv2
import imutils
import socket
import numpy as np
import time
import base64

"""
Description: This is client code to receive video frames over UDP.
Authurs: Sana Aziz - sana.aziz@my.uwi.edu, 
         Varune Jaggernath - varune.jaggernath@my.uwi.edu, 
         Justin Dookran - justin.dookran@my.uwi.edu,  
         Tyrel Cadogan - tyrel.cadogan@my.uwi.edu,
"""
# Maximum size of the UDP datagram in bytes
BUFF_SIZE = 65536 

# Setup clinet for datatransfer via UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

# get Hostname and Ip address
host_name = socket.gethostname()
print("Host Name: ",host_name)
# Get IP address
host_ip = socket.gethostbyname(host_name)
print(host_ip)

# port Number 
port = 9900
msg = b'Whyrel'
socket_address = (host_ip, port)
# Send test message
client_socket.sendto(msg, socket_address)
fps, start_time, frames_to_count, cnt = (0, 0, 20, 0)
print("Press \"q\" to close program.")

while True:
    # Recieve packets 
    packet, tmp = client_socket.recvfrom(BUFF_SIZE)
    # Decode from base64 to string
    data = base64.b64decode(packet, ' /')
    # Create Numpy array from string
    npdata = np.fromstring(data, dtype=np.uint8)
    # Decode Frames from arrray
    frame = cv2.imdecode(npdata, 1)
    # Put text on frame (wraped in black for better visibility)
    frame = cv2.putText(frame, 'FPS: '+str(fps), (10, 40),cv2.FONT_HERSHEY_SIMPLEX , 0.7, (0, 0, 0), 2)
    frame = cv2.putText(frame, 'FPS: '+str(fps), (10, 40),cv2.FONT_HERSHEY_SIMPLEX , 0.7, (0, 0, 255), 1)
    cv2.imshow("RECEIVING VIDEO", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        # Close Stream
        client_socket.close()
        break
    if cnt == frames_to_count:
        try:
            # Calculate Frame Rate 
            fps = round(frames_to_count/(time.time()-start_time))
            start_time = time.time()
            cnt = 0
        except:
            pass
    cnt += 1
