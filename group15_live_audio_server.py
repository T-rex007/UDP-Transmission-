import socket
import cv2
import pickle
import struct
import time
import pyshine as ps

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

	else:
		break

client_socket.close()
