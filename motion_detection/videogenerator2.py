import cv2
import numpy
import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading
import os

class VideoGenerator:
    def __init__(self):
        self.lock = threading.Lock()
        self.path = os.path.abspath(os.getcwd()) + "/MotionTracker/"
        self.face = cv2.CascadeClassifier(self.path + 'data/haarcascade_frontalface_alt2.xml')
        self.cam = PiCamera()
        self.cam.resolution = (640, 480)
        self.cam.framerate = 32
        self.cap = PiRGBArray(self.cam, size=(640, 480))
        time.sleep(0.1)
        self.outputFrame = None

    def detect_motion(self, frameCount):

        while True:
            frame = self.cap.read()
            #frame = imutils.resize(frame, width=500)
            #frame = imutils.rotate(frame, angle=180)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces_1 = self.face.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=2)
            if type(faces_1) == numpy.ndarray:

                for (fx, fy, fw, fh) in faces_1:
                    frame[fy: fy + fh, fx: fx + fw]
                    color = (255, 0, 0)  # BGR
                    stroke = 2
                    end_cord_fx = fx + fw
                    end_cord_fy = fy + fh
                    cv2.rectangle(frame, (fx, fy), (end_cord_fx, end_cord_fy), color, stroke)

            with self.lock:
                self.outputFrame = frame.copy()


    def generate(self):
        while True:
            with self.lock:
                if self.outputFrame is None:
                    continue
                # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", self.outputFrame)
                if not flag:
                    continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                    bytearray(encodedImage) + b'\r\n')
                #self.cap.release()
                #cv2.destroyAllWindows()
