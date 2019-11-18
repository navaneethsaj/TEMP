import socket            
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import time
import threading
from sys import getsizeof

def sendimage(data): 
    global host
    global port
    global comp_size 
    timestamp = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)               
    s.connect((host, port)) 
    is_success, im_buf_arr = cv2.imencode(".jpg", data)
    comp_size += getsizeof(im_buf_arr)
    s.sendall(im_buf_arr)
    s.sendall(bytes('TS='+str(timestamp), encoding='utf8'))
    s.close()


def stop():
    global port
    global host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       
    s.connect((host, port)) 
    s.send(b'STOPSTOPSTOP')
    s.close()

host = socket.gethostname()
host = socket.gethostbyname(host)
print('my device info ',(host,))
host = input('Enter Host IP (or use default 192.168.43.188) : ') or '192.168.43.188'
port = 12345   


#FROM HERE
cam = cv2.VideoCapture(-1) # ERROR MAY OCCOUR
# cam.set(cv2.CAP_PROP_EXPOSURE, 20) 
count = 20000

ret_val, data = cam.read() # JUST TO INITIALISE CAMERA

start = time.time()
totsize = 0
activeThreads = []
comp_size = 0
input("continue?...")
print("streaming to ", (host, port))
while count>0:
    ret_val, data = cam.read()
    if ret_val:
        t1 = threading.Thread(target=sendimage, args=(data,))
        t1.start()
        activeThreads.append(t1)
    else:
        print('Failed To Open Camera. Change 0->-1')
        break
    count-=1
    totsize += data.nbytes
    time.sleep(.05)


for x in activeThreads:
    x.join()
end = time.time()
#TO HERE
print('status')
print(end-start, '(s)')
print(totsize/10**6, 'MB') 
print(comp_size/10**6, 'MB') 
print('start time : ' ,start)    
print('end time : ' ,end)
stop()
input('end?')  