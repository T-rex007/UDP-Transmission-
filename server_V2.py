import struct
import pickle
import pyaudio
import wave
import threading
import socket
from concurrent.futures import ThreadPoolExecutor
import time
import cv2
import base64
import numpy as np
import os
import threading 
import queue
import imutils
import time 
import sys
import subprocess

fifo_q = queue.Queue(maxsize = 10)


root_path = os.getcwd()
video_name = "castaways.mp4"
video_path = os.path.join(root_path, video_name)
camera_index = 0

# Uing an mp4 video
# cap = cv2.VideoCapture(video_path)

cap = cv2.VideoCapture(camera_index)

# Retrieve the frame rate of the video
target_fps = cap.get(cv2.CAP_PROP_FPS)

print("Frame Rate of the video \"{}\": {} fps".format(video_name, target_fps))
frame_period = 1/target_fps

print("Time taken for One period: ".format(frame_period))

# This is server code to send video and audio frames over UDP/TCP
# For details visit pyshine.com
fifo_q = queue.Queue(maxsize=10)

command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(
    video_name, 'temp.wav')
os.system(command)

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 9900
socket_address = (host_ip, port)
server_socket.bind(socket_address)
print('Listening at:', socket_address)
target_fps = cap.get(cv2.CAP_PROP_FPS)
global TS
TS = (0.5/target_fps)
BREAK = False
print('FPS:', target_fps, TS)
totalNoFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
durationInSeconds = float(totalNoFrames) / float(target_fps)
d = cap.get(cv2.CAP_PROP_POS_MSEC)
print(durationInSeconds, d)

FR_ADJUST = 0.001


def videoToQ():

    FRAME_WIDTH = 500
    FRAME_HEIGHT = 500
    while(cap.isOpened()):
        try:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (FRAME_HEIGHT, FRAME_WIDTH))
            fifo_q.put(frame)
        except:
            sys.exit()
    print('Player closed')
    BREAK = True
    cap.release()


def videoStream():
    global TS
    fps, st, frames_to_count, count = (0, 0, 1, 0)
    cv2.namedWindow('TRANSMITTING VIDEO')
    cv2.moveWindow('TRANSMITTING VIDEO', 10, 30)
    while True:
        msg, client_addr = server_socket.recvfrom(BUFF_SIZE)
        print('GOT connection from ', client_addr)
        while(True):
            frame = fifo_q.get()
            encoded, buffer = cv2.imencode(
                '.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            server_socket.sendto(message, client_addr)
            frame = cv2.putText(frame, 'FPS: '+str(round(fps, 1)),
                                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if(count == frames_to_count):
                try:
                    fps = (frames_to_count/(time.time()-st))
                    st = time.time()
                    count = 0
                    if fps > target_fps:
                        TS += FR_ADJUST
                    elif fps < target_fps:
                        TS -= FR_ADJUST
                    else:
                        pass
                except:
                    pass
            count = count + 1

            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(int(1000*TS)) & 0xFF
            if key == ord('q'):
                os._exit(1)
                TS = False
                break


def audioStream():
    s = socket.socket()
    s.bind((host_ip, (port-1)))

    s.listen(5)
    CHUNK = 1024
    # wf = wave.open("temp.wav", 'rb')
    p = pyaudio.PyAudio()
    print('server listening at', (host_ip, (port-1)))
    audio_stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=CHUNK)

    client_socket, addr = s.accept()

    while True:
        if client_socket:
            while True:
                data = audio_stream(CHUNK)
                a = pickle.dumps(data)
                message = struct.pack("Q", len(a))+a
                client_socket.sendall(message)


with ThreadPoolExecutor(max_workers=3) as executor:
    executor.submit(audioStream)
    executor.submit(videoToQ)
    executor.submit(videoStream)









