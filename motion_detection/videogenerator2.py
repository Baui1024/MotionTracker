import cv2
import numpy
from picamera import PiCamera

class VideoGenerator:

    def __init__(self):

        self.face = cv2.CascadeClassifier('cv2/data/haarcascade_frontalface_alt2.xml')
        self.cam = PiCamera()
        self.cap = cv2.VideoCapture(self.cam)

    def generate(self):

        while True:
            with self.lock:
                ret, frame = self.cap.read()
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

                    print("something")
                    #cv2.imshow('frame', frame)
                    (flag, encodedImage) = cv2.imencode(".jpg", self.outputFrame)
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                           bytearray(encodedImage) + b'\r\n')
                    #if cv2.waitKey(20) & 0xFF == ord('q'):
                    #    break

        #self.cap.release()
        #cv2.destroyAllWindows()
