#!/usr/bin/python3
"""
Authurs: Sana Aziz,
         Varune ....,
         Justin ....,
         Tyrel Cadogan
email: tyrel.cadogan@my.uwi.edu
Description: This is server code to send video frames over UDP
"""


import cv2
import imutils
import socket
import numpy as np
import time
import base64
import pandas as pd
from datetime import datetime

data_static = {"frame_rate": [],
		"time_stamp": []
}
# Video source
video_source = 0
# for a 256 pixel image
BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

# Get hostname and IP
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 9900
socket_address = (host_ip, port)
server_socket.bind(socket_address)
print('Listening at:', socket_address)

# Create video capture object that streams form your webcam/ any path specified
print("Opening Webcam capture object.")
cap = cv2.VideoCapture(video_source)
fps, st, frames_to_count, cnt = (0, 0, 20, 0)

while True:
	msg, client_addr = server_socket.recvfrom(BUFF_SIZE)
	print('GOT connection from ', client_addr)
	WIDTH = 400
	while(cap.isOpened()):
		ret, frame = cap.read()
		frame = cv2.resize(frame, (WIDTH, WIDTH))
        # encode image to a base64 string
		encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
		message = base64.b64encode(buffer)
		server_socket.sendto(message, client_addr)
        # Write frame per second on each frame
		frame = cv2.putText(frame, 'FPS: '+str(fps), (10, 40),
		                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
		frame = cv2.putText(frame, 'FPS: '+str(fps), (10, 40),
		                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
		cv2.imshow('TRANSMITTING VIDEO', frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			server_socket.close()
			break
		if cnt == frames_to_count:
			data_static['frame_rate'].append(fps)
			data_static['time_stamp'].append(datetime.now().strftime("%H:%M:%S"))
			tmp = data_static["frame_rate"]
			tmp = [i for i in tmp]
			try:
				avg = sum(tmp)/len(tmp)
				print("Recieve an AverageFrame rate of: ", avg)
				pd.DataFrame(data_static).to_csv("Server_video_data.csv")
			except:
				pass
				
			try:
				fps = round(frames_to_count/(time.time()-st))
				st = time.time()
				cnt = 0
			except:
				pass
		cnt += 1
