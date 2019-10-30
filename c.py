import socket            
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import time
from sys import getsizeof

def sendimage(data):  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    host = '192.168.43.188'#socket.gethostname() 
    port = 12345               
    s.connect((host, port)) 
    # data = data.flatten()
    # print(data.shape)
    # print(data)
    s.send(data.tobytes())
    # print(time.time())    
    s.close()
    #TODO : (IF NEEDED IN FUTURE) USE APPROPRIATE METHOD TO MARK END OF FILE
    # fundamental truth of sockets: 
    # messages must either be fixed length (yuck), 
    # or be delimited (shrug), 
    # or indicate how long they are (much better), 
    # or end by shutting down the connection. 
    # The choice is entirely yours, (but some ways are righter than others).
    # s.send(b'EOFEOFEOF') #TO MARK END OF IMAGE **IMPORTANT



def stop():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    host = '192.168.43.188'#socket.gethostname() 
    port = 12345               
    s.connect((host, port)) 
    s.send(b'STOPSTOPSTOP')
    s.close()


#FROM HERE
cam = cv2.VideoCapture(0)
count = 50

ret_val, data = cam.read() # JUST TO INITIALISE CAMERA

start = time.time()
totsize = 0
while count>0:
    ret_val, data = cam.read()
    sendimage(data)
    count-=1
    totsize += data.nbytes

#TO HERE
print('status')
print(time.time()-start, '(s)')
print(totsize/10**6, 'MB')      
stop()
input('end?')  