import cv2
import numpy
import time
import threading
import os
import imutils
from imutils.video import VideoStream
import datetime

class VideoGenerator:
    def __init__(self, piCamera=False):
        self.width = 1280
        self.height = 720
        self.vs = VideoStream(usePiCamera=piCamera).start()
        if piCamera:
            #from picamera.array import PiRGBArray
            #from picamera import PiCamera
            #self.cam = PiCamera()
            #self.cam.resolution = (self.width, self.height)
            #self.cam.framerate = 32
            self.path = os.path.abspath(os.getcwd()) + "/MotionTracker/"
            #self.cap = PiRGBArray(self.cam, size=(self.width, self.height))

        else:
            print("webcam")
            #self.cam = VideoStream(src=0).start()  # use for webcam
            self.path = ""
        self.lock = threading.Lock()
        self.face = cv2.CascadeClassifier(self.path + 'data/haarcascade_frontalface_alt2.xml')
        # self.cap = cv2.VideoCapture(self.cam)
        time.sleep(0.1)
        self.outputFrame = None

    def detect_motion(self, frameCount):

        while True:
            frame = self.vs.read()
            frame = imutils.resize(frame, width=400)
            # draw the timestamp on the frame
            timestamp = datetime.datetime.now()
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            #cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
            #            0.35, (0, 0, 255), 1)
            # show the frame
            with self.lock:
                self.outputFrame = frame.copy()

    #       for frame in self.cam.capture_continuous(self.cap, format="bgr", use_video_port=True):
    #           #frame = self.cap.read()
    #            image = frame.array
    #            #frame = imutils.resize(frame, width=500)
    #            image = imutils.rotate(image, angle=180)
    #            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #            faces_1 = self.face.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=2)
    #            if type(faces_1) == numpy.ndarray:
    #
    #               for (fx, fy, fw, fh) in faces_1:
    #                    image[fy: fy + fh, fx: fx + fw]
    #                    color = (255, 0, 0)  # BGR
    #                    stroke = 2
    #                    end_cord_fx = fx + fw
    #                    end_cord_fy = fy + fh
    #                    cv2.rectangle(image, (fx, fy), (end_cord_fx, end_cord_fy), color, stroke)
    #
    #            with self.lock:
    #                self.outputFrame = image.copy()
    #           # clear the stream in preparation for the next frame
    #            self.cap.truncate(0)

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
            # self.cap.release()
            # cv2.destroyAllWindows()
