#!/usr/bin/python3
"""
Authurs: Sana Aziz, 
         Varune ...., 
         Justin ...., 
         Tyrel Cadogan
email: tyrel.cadogan@my.uwi.edu
"""


# This is server code to send video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64

# Video source 
video_source = 0
# for a 256 pixel image 
BUFF_SIZE = 65536 
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

# Get hostname and IP
host_name = socket.gethostname()
host_ip =  socket.gethostbyname(host_name)
print(host_ip)
port = 9999
socket_address = (host_ip,port)
server_socket.bind(socket_address)
print('Listening at:',socket_address)

# Create video capture object that streams form your webcam/ any path specified
cap = cv2.VideoCapture(video_source)
fps,st,frames_to_count,cnt = (0,0,20,0)

while True:
	msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
	print('GOT connection from ',client_addr)
	WIDTH=400
	while(cap.isOpened()):
		_,frame = cap.read()
		frame = imutils.resize(frame,width=WIDTH)
        # encode image to a base64 string
		encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
		message = base64.b64encode(buffer)
		server_socket.sendto(message,client_addr)
        # Write test to frame
		frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255, 0),2)
		cv2.imshow('TRANSMITTING VIDEO',frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			server_socket.close()
			break
		if cnt == frames_to_count:
			try:
				fps = round(frames_to_count/(time.time()-st))
				st=time.time()
				cnt=0
			except:
				pass
		cnt+=1
