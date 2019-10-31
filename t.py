import cv2
from sys import getsizeof

cam = cv2.VideoCapture(0)
ret_val, data = cam.read() # JUST TO INITIALISE CAMERA
print(getsizeof(data))
is_success, im_buf_arr = cv2.imencode(".jpg", data)
print(getsizeof(im_buf_arr), type(im_buf_arr))

data = cv2.imdecode(im_buf_arr, cv2.IMREAD_COLOR)
print(getsizeof(data))
