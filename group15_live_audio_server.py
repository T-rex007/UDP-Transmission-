#!/usr/bin/python3

"""
Description: This is server code to receive audio frames over TCP.
Authurs: Sana Aziz - sana.aziz@my.uwi.edu, 
         Varune Jaggernath - varune.jaggernath@my.uwi.edu, 
         Justin Dookran - justin.dookran@my.uwi.edu,  
         Tyrel Cadogan - tyrel.cadogan@my.uwi.edu,
"""
import socket
import cv2
import pickle
import struct
import time
import pyshine as ps
from datetime import datetime
import pandas as pd

data_static = {"frame_rate": [],
               "time_stamp": []
               }

mode = 'send'
name = 'SERVER TRANSMITTING AUDIO'
audio, context = ps.audioCapture(mode=mode)
#ps.showPlot(context,name)

# Create socket with TCP connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 7802
backlog = 5
print(host_name)
print("Backlog: ", backlog)
socket_address = (host_ip, port)
print('STARTING SERVER AT', socket_address, '...')
server_socket.bind(socket_address)
server_socket.listen(backlog)
fps, start_time, frames_to_count, cnt = (0, 0, 20, 0)

while True:
	client_socket, addr = server_socket.accept()
	print('GOT CONNECTION FROM:', addr)
	if client_socket:

		while(True):
			frame = audio.get()
            # Serialize frame
			a = pickle.dumps(frame)
			message = struct.pack("Q", len(a))+a
			client_socket.sendall(message)
			if cnt == frames_to_count:
				data_static['frame_rate'].append(fps)
				data_static['time_stamp'].append(datetime.now().strftime("%H:%M:%S"))
				tmp = data_static["frame_rate"]
				tmp = [i for i in tmp]
				try:
					avg = sum(tmp)/len(tmp)
					print("Recieve an AverageFrame rate of: ", avg)
					pd.DataFrame(data_static).to_csv("Server_audio_data.csv")
				except:
					pass
				try:
					fps = round(frames_to_count/(time.time()-start_time))
					start_time = time.time()
					cnt = 0
				except:
					pass
			cnt += 1
			print(cnt)
			print("FPS:", fps)
	else:
		break

client_socket.close()
