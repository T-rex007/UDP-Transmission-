import struct
import pickle
import pyaudio
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import base64
import numpy as np
import cv2
import socket

BUFF_SIZE = 65536

BREAK = False
# UDP 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print("Host IP: ",host_ip)
port = 9900


msg = b'hola'
client_socket.sendto(msg, (host_ip, port))
	

def videoThread():

	cv2.namedWindow('RECEIVING VIDEO')
	cv2.moveWindow('RECEIVING VIDEO', 10, 360)
	fps, start_time, frames_to_count, count = (0, 0, 20, 0)
	while True:
		packet, _ = client_socket.recvfrom(BUFF_SIZE)
		data = base64.b64decode(packet, ' /')
		npdata = np.fromstring(data, dtype=np.uint8)

		frame = cv2.imdecode(npdata, 1)
		frame = cv2.putText(frame, 'Frame Rate: '+str(fps), (10, 40),
		                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0,0 ), 2)
		frame = cv2.putText(frame, 'Frame Rate: '+str(fps), (10, 40),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,0 ), 1)
		cv2.imshow("RECEIVING VIDEO", frame)
		key = cv2.waitKey(1) & 0xFF

		if key == ord('q'):
			client_socket.close()
			sys.exit()
			break

		if(count == frames_to_count):
			try:
				fps = round(frames_to_count/(time.time()-start_time))
				start_time= time.time()
				count = 0
			except:
				pass
		count += 1

	client_socket.close()
	cv2.destroyAllWindows()


def audioThread():

	p = pyaudio.PyAudio()
	CHUNK = 1024
	stream = p.open(format=p.get_format_from_width(2),
                 channels=2,
                 rate=44100,
                 output=True,
                 frames_per_buffer=CHUNK)

	# create socket
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket_address = (host_ip, port-1)
	print('Server listening at', socket_address)
	client_socket.connect(socket_address)
	print("CLIENT is CONNECTED TO", socket_address)
	data = b""
	payload_size = struct.calcsize("Q")
	while True:
		try:
			while len(data) < payload_size:
				packet = client_socket.recv(4*1024)  # 4K
				if not packet:
					break
				data += packet
			packed_msg_size = data[:payload_size]
			data = data[payload_size:]
			msg_size = struct.unpack("Q", packed_msg_size)[0]
			while len(data) < msg_size:
				data += client_socket.recv(4*1024)
			frame_data = data[:msg_size]
			data = data[msg_size:]
			frame = pickle.loads(frame_data)
			stream.write(frame)

		except:

			break

	client_socket.close()
	print('Audio closed', BREAK)
	os._exit(1)


with ThreadPoolExecutor(max_workers=2) as executor:
	executor.submit(audioThread)
	executor.submit(videoThread)
