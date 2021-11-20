import socket
import time
import cv2
import pickle
import struct
import pyshine as ps

mode = 'get'
name = 'CLIENT RECEIVING AUDIO'
audio, context = ps.audioCapture(mode=mode)
ps.showPlot(context, name)

# create socket with TCP connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get IP Address
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

port = 7802

print(host_name)
socket_address = (host_ip, port)

client_socket.connect(socket_address)
print("Client program connected to: ", socket_address)
fps, start_time, frames_to_count, cnt = (0, 0, 20, 0)
data = b""
payload_size = struct.calcsize("Q")
while True:
	while len(data) < payload_size:
		packet = client_socket.recv(4*1024)  # 4K
		if not packet:
			break
		data += packet
	packed_msg_size = data[:payload_size]
	data = data[payload_size:]
	msg_size = struct.unpack("Q", packed_msg_size)[0]
	
	if( cnt == frames_to_count):
		try:
			fps = round(frames_to_count/(time.time()-start_time))
			start_time = time.time()
			cnt = 0
		except:
			pass
	cnt += 1

	while len(data) < msg_size:
		data += client_socket.recv(4*1024)
	frame_data = data[:msg_size]
	data = data[msg_size:]
	frame = pickle.loads(frame_data)
	audio.put(frame)

client_socket.close()
