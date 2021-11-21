from multiprocessing import Process
import os
import subprocess
import os 
import sys 
import time

print("Starting The Server") 
exec_path = sys.executable
subprocess.Popen([exec_path, os.path.join(os.getcwd(), "group15_live_video_server.py")])

time.sleep(2)
print("Starting The Server")
subprocess.Popen([exec_path, os.path.join(
    os.getcwd(), "group15_live_video_client.py")])



