import socket              
import numpy as np
import cv2
import pickle
import matplotlib.pyplot as plt
import os
import time
import threading

started = False

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
            return 'STOP', str(time.time())
        data += chunk
    # print('chunks = '+str(count))
    i = 1
    while chr(data[-i]) != "T" and  chr(data[-i+1]) != "S" and chr(data[-i+2]) != "=":
        i+=1
    # print(type(data[-i+3:]))
    return data[:-i], str(data[-i+3:], 'utf8')

def stream_to_ui(data, ui_host, ui_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       
    s.connect((ui_host, ui_port)) 
    if data == None:
        s.send(b'STOPSTOPSTOP')    
    else:
        s.send(data)
    s.close()

def helperThread(c,addr,count):
    global ui_host
    global ui_port
    global started
    

    data, timestamp = recvall(c) 
    if data == 'STOP':
        global s
        s.close()
        stream_to_ui(None, ui_host, ui_port)
        return

    
    stream_to_ui(data, ui_host, ui_port)

    if not started:
        return
    data = np.frombuffer(data, dtype='uint8')
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    data = np.reshape(data, (480,640,3))
    cv2.imwrite(os.path.join('C:\\Users\\Navaneeth\\Desktop\\dummy\\data', str(timestamp)+'.jpg'), data)
    # print(time.time())

def start_stop_recording():
    global started
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
    host = socket.gethostname()
    host = socket.gethostbyname(host)
    port = 11111
    s.bind((host, port))      
    s.listen(5)
    print("listening for start stop", (host, port))
    while True:
        try:
            c, addr = s.accept()
            started = not started
            print("started recording = ",started)
        except OSError:
            pass


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
host = socket.gethostname()
host = socket.gethostbyname(host)
port = 12345                     
print('my device info ',(host, port))  
ui_host = input('Enter IP of UI(or use default 192.168.43.188) : ') or '192.168.43.188'
ui_port = 4096
s.bind((host, port)) 
s.listen(5)    
input("continue?....")
t1 = threading.Thread(target=start_stop_recording, args=())
t1.start()
starttime = 0
count = 1
activeThreads = []
print('listening for stream from camera ',(host, port))  
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
end = time.time()
print('Time Taken ', end - starttime, '(s)')
print('start time : ' ,starttime)    
print('end time : ' ,end)
s.close()               

