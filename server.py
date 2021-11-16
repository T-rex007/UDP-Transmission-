# This is server code to send video and audio frames over UDP/TCP

from concurrent.futures import ThreadPoolExecutor
import cv2
import imutils
import socket
import numpy as np
import time
import base64
import threading
import wave
import pyaudio
import pickle
import struct
import sys
import queue
import os


que = queue.Queue(maxsize=10)

filename = 'castaways.mp4'

file_path = os.path.join(os.getcwd(), filename)
command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(
    file_path, 'temp.wav')
os.system(command)

BUFF_SIZE = 65536
## UDP transmission protocol
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 9688
socket_address = (host_ip, port)
server_socket.bind(socket_address)
print('Listening at:', socket_address)

cap = cv2.VideoCapture(file_path)
TARGET_FPS = cap.get(cv2.CAP_PROP_FPS)
global TS
TS = (0.5/TARGET_FPS)
BREAK = False
print('FPS:', TARGET_FPS, TS)
totalNoFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
durationInSeconds = float(totalNoFrames) / float(TARGET_FPS)
d = cap.get(cv2.CAP_PROP_POS_MSEC)
print(durationInSeconds, d)


def video_stream_gen():

    WIDTH = 400
    while(cap.isOpened()):
        try:
            _, frame = cap.read()
            frame = imutils.resize(frame, width=WIDTH)
            que.put(frame)
        except:
            sys.exit()
    print('Player closed')
    BREAK = True
    cap.release()


def video_stream():
    global TS
    fps, start_time, frames_to_count, cnt = (0, 0, 1, 0)
    cv2.namedWindow('TRANSMITTING {} VIDEO'.format(filename))
    cv2.moveWindow('TRANSMITTING {} VIDEO'.format(filename), 10, 30)
    while True:
        msg, client_addr = server_socket.recvfrom(BUFF_SIZE)
        print('Connected to ', client_addr)

        while(True):
            frame = que.get()
            encoded, buffer = cv2.imencode(
                '.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            server_socket.sendto(message, client_addr)

			# wrap text in black 
            frame = cv2.putText(frame, 'FPS: '+str(round(fps, 1)),
                                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 0), 2)
            frame = cv2.putText(frame, 'FPS: '+str(round(fps, 1)),
                                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
			
            if cnt == frames_to_count:
                try:
                    fps = (frames_to_count/(time.time()-start_time))
                    start_time = time.time()
                    count = 0
                    if fps > TARGET_FPS:
                        TS += 0.001
                    elif fps < TARGET_FPS:
                        TS -= 0.001
                    else:
                        pass
                except:
                    pass
            count += 1

            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(int(1000*TS)) & 0xFF
            if key == ord('q'):
                os._exit(1)
                TS = False
                break


def audio_stream():
    s = socket.socket()
    s.bind((host_ip, (port-1)))

    s.listen(5)
    CHUNK = 1024
    wf = wave.open("temp.wav", 'rb')
    p = pyaudio.PyAudio()
    print('server listening at', (host_ip, (port-1)))
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    frames_per_buffer=CHUNK)

    client_socket, addr = s.accept()

    while True:
        if client_socket:
            while True:
                data = wf.readframes(CHUNK)
                a = pickle.dumps(data)
                message = struct.pack("Q", len(a))+a
                client_socket.sendall(message)


with ThreadPoolExecutor(max_workers=3) as executor:
    executor.submit(audio_stream)
    executor.submit(video_stream_gen)
    executor.submit(video_stream)
