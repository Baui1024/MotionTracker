# import the necessary packages
from motion_detection.videogenerator2 import VideoGenerator
from flask import Flask, Response, render_template, request
import threading
import argparse
import sqlite3
import os


#need relative path for linux
#path = os.path.abspath(os.getcwd()) + "/MotionTracker/"
path = ""
conn = sqlite3.connect(path + "database.db", check_same_thread=False)
#video = VideoGenerator(usePiCamera=args["picamera"] > 0)


# cc = conn.cursor()


# cc.execute("""CREATE TABLE Shapes(
#           Bank text,
#          Zone text,
#         Shape text,
#        Data text
#       )""")


def insertShape(bank, zone, shape, data):
    c = conn.cursor()
    with conn:
        c.execute("INSERT INTO Shapes VALUES (:Bank, :Zone, :Shape, :Data)",
                  {"Bank": bank, "Zone": zone, "Shape": shape, "Data": data})
    c.close()
    print("inserted")


def updateShape(bank, zone, shape, data):
    c = conn.cursor()
    with conn:
        c.execute("UPDATE Shapes SET Shape=:shape, Data=:data WHERE Bank=:bank AND Zone=:zone ",
                  {"shape": shape, "data": data, "bank": bank, "zone": zone})
    c.close()


def getShape(bank, zone):
    c = conn.cursor()
    c.execute("SELECT * FROM Shapes WHERE bank=:bank AND zone=:zone", {"bank": bank, "zone": zone})
    result = c.fetchall()
    c.close()
    return result


def getAllShapes():
    c = conn.cursor()
    c.execute("SELECT * FROM Shapes")
    result = c.fetchall()
    c.close()
    if result:
        return result
    else:
        return []


# initialize a flask object
app = Flask(__name__, template_folder=path + "templates")
# initialize the dictionaries
Zones = {}
Shapes = {}
Shape = "rect"


# initialize the Dictionaries
def shapeInit():
    for Mics in range(1, 11):
        Zones["Bank" + str(Mics)] = {}
        Shapes["Bank" + str(Mics)] = {}
        for Zone in range(1, 21):
            Shapes["Bank" + str(Mics)]["Zone" + str(Zone)] = {}
            Zones["Bank" + str(Mics)]["Zone" + str(Zone)] = False


shapeInit()


def syncDatabaseWithDic():
    db = getAllShapes()
    for BankZones in db:
        data = {"shape": BankZones[2], "data": ' '.join([BankZones[3]]).replace("'", "\"")}
        Shapes[BankZones[0]][BankZones[1]] = data
    #print("synced shapes:", Shapes)
    return True


syncDatabaseWithDic()


@app.route("/", methods=["GET"])
def index():
    if request.method == "GET" and syncDatabaseWithDic():
        return render_template("index.html", Zones=Zones, Shapes=Shapes, Shape=Shape)


@app.route("/resetAllShapes", methods=["POST"])
def resetAllShapes():
    if request.method == "POST":
        c = conn.cursor()
        c.execute("DELETE FROM Shapes")
        c.close()
        print("got it")
        print("all shapes after reset", getAllShapes())
        shapeInit()
    return "200"


@app.route("/setShape", methods=["POST"])
def setShape():
    global Shape
    if request.method == "POST":
        shape = request.form
        for x in shape:
            Shape = x
    return "200"

@app.route("/resetShape", methods=["POST"])
def resetShape():
    global Shape
    if request.method == "POST":
        shapeDict = request.get_json()
        if getShape(shapeDict["bank"], shapeDict["data"]["zone"]) == []:
            pass
        else:
            updateShape(shapeDict["bank"], shapeDict["data"]["zone"],
                        "{}", "{}") #updating the database with empty values
        getShape(shapeDict["bank"], shapeDict["data"]["zone"])
        syncDatabaseWithDic()
        print("all shapes after post:", getShape(shapeDict["bank"], shapeDict["data"]["zone"]))
        # print(Shapes)
    return render_template("index.html", Zones=Zones, Shapes=Shapes)


@app.route("/submitShape", methods=["POST", "GET"])
def submitShape():
    if request.method == "POST":
        shapeDict = request.get_json()
        # Shapes[shapeDict["bank"]][shapeDict["data"]["zone"]] = shapeDict["data"]["data"]
        if getShape(shapeDict["bank"], shapeDict["data"]["zone"]) == []:
            insertShape(shapeDict["bank"], shapeDict["data"]["zone"],
                        shapeDict["data"]["data"]["shape"], str(shapeDict["data"]["data"]["data"]))
        else:
            updateShape(shapeDict["bank"], shapeDict["data"]["zone"],
                        shapeDict["data"]["data"]["shape"], str(shapeDict["data"]["data"]["data"]))

        getShape(shapeDict["bank"], shapeDict["data"]["zone"])
        syncDatabaseWithDic()
        print("all shapes after post:", getShape(shapeDict["bank"], shapeDict["data"]["zone"]))
        # print(Shapes)
    return render_template("index.html", Zones=Zones, Shapes=Shapes)


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(video.generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default="0.0.0.0",
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, default="8090",
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    ap.add_argument("-p", "--picamera", type=int, default=-1,
                         help="whether or not the Raspberry Pi camera should be used")
    args = vars(ap.parse_args())
    video = VideoGenerator(piCamera=args["picamera"] > 0)
    # start a thread that will perform motion detection
    t = threading.Thread(target=video.detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
    # release the video stream pointer
    video.vs.stop()

