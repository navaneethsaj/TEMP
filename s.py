import socket              
import numpy as np
import cv2
import pickle
import matplotlib.pyplot as plt
import os
import time
import threading

def recvall(c):
    data = b''
    count = 0
    BUFF_SIZE  = 6553600  #64KB
    while True:
        count += 1
        chunk = c.recv(BUFF_SIZE)
        # print(count, '\n', chunk)
        if chunk==b'': #empty byte received due to socket.SHUTDOWN() in client
            # print('image received')
            break
        if chunk == b'STOPSTOPSTOP':
            return 'STOP'
        data += chunk
    # print('chunks = '+str(count))
    return data


def helperThread(c,addr,count):
    data = recvall(c) 
    if data == 'STOP':
        global s
        s.close()
        return
    data = np.frombuffer(data, dtype='uint8')
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    data = np.reshape(data, (480,640,3))
    cv2.imwrite(os.path.join('C:\\Users\\Navaneeth\\Desktop\\dummy\\data',str(count)+'.jpg'), data)
    # print(time.time())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
host = socket.gethostname()
host = socket.gethostbyname(host)
port = 12345                
s.bind((host, port))      
print((host, port))  
s.listen(5)          

starttime = 0
count = 1
activeThreads = []
while True:
    try:
        c, addr = s.accept()
        if starttime==0:
            starttime = time.time()
    except OSError:
        #helperThread closes socket S when STOP
        break
    # print ('Got connection from', addr)
    t1 = threading.Thread(target=helperThread, args=(c,addr,count))
    t1.start()
    activeThreads.append(t1)
    count += 1
    
for x in activeThreads:
    x.join()

print('Time Taken ', time.time() - starttime, '(s)')
s.close()               

