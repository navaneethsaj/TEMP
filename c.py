import socket            
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import time
import threading
from sys import getsizeof

def sendimage(data): 
    global comp_size 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    host = '192.168.43.188'#socket.gethostname() 
    port = 12345               
    s.connect((host, port)) 
    is_success, im_buf_arr = cv2.imencode(".jpg", data)
    comp_size += getsizeof(im_buf_arr)
    s.sendall(im_buf_arr)
    s.close()



def stop():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    host = '192.168.43.188'#socket.gethostname() 
    port = 12345               
    s.connect((host, port)) 
    s.send(b'STOPSTOPSTOP')
    s.close()


#FROM HERE
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_EXPOSURE, 20) 
count = 50

ret_val, data = cam.read() # JUST TO INITIALISE CAMERA

start = time.time()
totsize = 0
activeThreads = []
comp_size = 0
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
    time.sleep(.1)


for x in activeThreads:
    x.join()

#TO HERE
print('status')
print(time.time()-start, '(s)')
print(totsize/10**6, 'MB') 
print(comp_size/10**6, 'MB')     
stop()
input('end?')  