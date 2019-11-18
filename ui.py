import tkinter
from sys import getsizeof
from tkinter import messagebox

import numpy as np
from PIL import ImageTk, Image
import threading
import time
import socket
from pynput.keyboard import Key, Listener
import cv2
import os

count_speed = 0
count_turn = 0
started = False
terminate_var=False
cap = cv2.VideoCapture(0)


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()
        os._exit(1)


def recvall(c):
    data = b''
    count = 0
    BUFF_SIZE = 6553600  # 64KB
    while True:
        count += 1
        chunk = c.recv(BUFF_SIZE)
        # print(count, '\n', chunk)
        if chunk == b'':  # empty byte received due to socket.SHUTDOWN() in client
            # print('image received')
            break
        if chunk == b'STOPSTOPSTOP':
            return 'STOP'
        data += chunk
    # print('chunks = '+str(count))
    return data


def videoHandler():
    global window
    global cap
    vidLabel = tkinter.Label(window, anchor=tkinter.NW)
    vidLabel.place(x=0, y=0)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    host = socket.gethostbyname(host)
    port = 4096
    s.bind((host, port))
    print("Listening for video stream (portno:"+str(port)+")")
    s.listen(5)
    i = 0
    size = 0
    stime = 0
    b = False
    while True:
        c, addresss = s.accept()
        if not b:
            stime = time.time()
            b = True
        recived_data = recvall(c)
        size = size + getsizeof(recived_data)
        if recived_data == 'STOP':
            break
        recived_data = np.frombuffer(recived_data, dtype='uint8')
        recived_data = cv2.imdecode(recived_data, cv2.IMREAD_COLOR)
        recived_data = np.reshape(recived_data, (480, 640, 3))

        # cv2.imwrite(os.path.join('D:\\images1\\imageToSave'+str(i)+'.png'), recived_data)
        ###########################
        # ret, frame = cap.read()

        recived_data = cv2.cvtColor(recived_data, cv2.COLOR_BGR2RGB)

        frame = Image.fromarray(recived_data)
        frame = ImageTk.PhotoImage(frame)
        vidLabel.configure(image=frame)
        vidLabel.image = frame
    print(size / (1024 * 1024))
    end = time.time()
    print(" time ", end - stime)
    print(" END ", end, "     START ", stime)


def timstamprecorder_keystrock():
    global count_turn, terminate_var, started, count_speed
    f = open("C:\\Users\\Navaneeth\\Desktop\\\dummy\\dummytime_cardata.txt", 'a')
    while not terminate_var:
        if started:
            f.write(str(time.time()) + " " + str(count_speed) + " " + str(count_turn)+"\n")
        time.sleep(.02)
    f.close()


def start_stop():
    global started
    global hostaddress, start_stop_port
    started = not started
    print('Recoding started = ',started)
    sb = socket.socket()
    sb.connect((hostaddress, start_stop_port))
    sb.send(bytes(str(started), encoding='utf8'))
    sb.close()


def on_press(key):
    m = str(key)
    x = m[1:-1]
    if key == Key.up or x == 'w':
        w()
    if key == Key.down or x == 's':
        s()
    if key == Key.left or x == 'a':
        a()
    if key == Key.right or x == 'd':
        d()
    if x == 'r':
        start_stop()
    if key == Key.space:
        stop()


def on_release(key):
    m = str(key)
    x = m[1:-1]
    # if key == Key.up or x == 'w':
    # w()
    # if key == Key.down or x == 's':
    #     s()
    if key == Key.left or x == 'a':
        steer_straight()
    if key == Key.right or x == 'd':
        steer_straight()
    if key == Key.space:
        stop()


def send(message):
    global pi_address
    sb = socket.socket()
    port = 12347
    print("Sending to RPI (controls[Acceleration,Turn])"+message)
    sb.connect((pi_address, port))
    sb.send(message.encode())
    sb.close()
    pass


def key_pressHandler():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def w():
    global count_speed, label1
    if count_speed < 3:
        count_speed = count_speed + 1
        send(str(count_speed) + " " + str(count_turn))
        label1.configure(text=count_speed)


def s():
    global count_speed, label1
    if count_speed > -3:
        count_speed = count_speed - 1
        send(str(count_speed) + " " + str(count_turn))
        label1.configure(text=count_speed)


def a():
    global count_turn, label2
    if count_turn > -1:
        count_turn = count_turn - 1
        send(str(count_speed) + " " + str(count_turn))
        label2.configure(text=count_turn)


def d():
    global count_turn, label2
    if count_turn < 1:
        count_turn = count_turn + 1
        send(str(count_speed) + " " + str(count_turn))
        label2.configure(text=count_turn)


def steer_straight():
    global count_turn
    count_turn = 0
    send(str(count_speed) + " " + str(0))
    label2.configure(text=count_turn)


def stop():
    global count_speed, label1, count_turn
    count_speed = 0
    count_turn = 0
    send(str(count_speed) + " " + str(count_turn))
    label1.configure(text=count_speed)
    label2.configure(text=count_turn)

def quit():
    global terminate_var
    terminate_var = True

window = tkinter.Tk()
window.title("Car")
window.geometry("900x480")
print("IP_address : 192.168.43.113")
hostaddress = input("Enter the host address (default : '192.168.43.188')") or '192.168.43.188'
start_stop_port = 11111

pi_address = input("Enter address of pi or use default '192.168.43.163'") or '192.168.43.163'
# canvas = tkinter.Canvas(window, width=1200, height=450).pack()
img = Image.open("C:\\Users\\Navaneeth\\Desktop\\dummy\\place.jpg")
img = ImageTk.PhotoImage(img.resize((640, 480), Image.ANTIALIAS))
tkinter.Label(window, image=img).place(x=0, y=0)

tkinter.Label(window, text="Acceleration").place(x=700, y=100)
tkinter.Label(window, text="Turn").place(x=700, y=200)

label1 = tkinter.Label(window)
label1.place(x=800, y=100)

label2 = tkinter.Label(window)
label2.place(x=800, y=200)

t1 = threading.Thread(target=videoHandler)
t2 = threading.Thread(target=key_pressHandler)
t3 = threading.Thread(target=timstamprecorder_keystrock)
# n=input("Do u want to continue for video streaming?")
t1.start()
t2.start()
# n1=input("Dou want to enable video recording?")
t3.start()

w1 = tkinter.Button(window, text='W', command=w, height=1, width=3, bg="black", fg="white")
w1.place(x=750, y=300)
s1 = tkinter.Button(window, text='S', command=s, height=1, width=3, bg="black", fg="white")
s1.place(x=750, y=350)
a1 = tkinter.Button(window, text='A', command=a, height=1, width=3, bg="black", fg="white")
a1.place(x=700, y=350)
d1 = tkinter.Button(window, text='D', command=d, height=1, width=3, bg="black", fg="white")
d1.place(x=800, y=350)
space1 = tkinter.Button(window, text='Space', command=stop, height=1, width=12, bg="black", fg="white")
space1.place(x=750, y=400)

terminate = tkinter.Button(window, text='Exit', command=quit, height=3, width=3, bg="black", fg="white")
terminate.place(x=750, y=150)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
