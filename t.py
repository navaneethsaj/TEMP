import cv2

cam = cv2.VideoCapture(0)
ret_val, data = cam.read() # JUST TO INITIALISE CAMERA
print(data.nbytes)