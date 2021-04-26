import socket, pickle,struct
from cv2 import cv2
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.releat()

    def get_frame(self):
        ret, frame = self.video.read()
        frame = cv2.flip(frame, 1)

        ret,jpeg = cv2.imencode('.jpg',frame)
        return jpeg.tobytes()
