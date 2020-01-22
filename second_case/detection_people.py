""" a python script ables to detect people in a video-stream.
USAGE: python3 detection_people.py --input videos/example.mp4 --output output/example_out.avi --yolo yolo-coco
"""
import argparse
import json
import logging
import time
from datetime import datetime

import cv2
import imutils
import numpy as np
from imutils.video import FPS
from imutils.video import VideoStream

from common.bot import bot
from common.publisher import Publisher_people

pub = Publisher_people(clientID='pub_vid', topic='AulaMagna')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                    datefmt='%d/%m/%Y %H:%M ',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", default="MobileNetSSD_deploy.prototxt.txt",
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", default="MobileNetSSD_deploy.caffemodel", help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2, help="minimum probability to filter weak detections")
ap.add_argument("-i", "--input", type=str, help="path to optional input video file")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# if a video path was not supplied, grab a reference to the webcam
if not args.get("input", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

# otherwise, grab a reference to the video file
else:
    print("[INFO] opening video file...")
    vs = cv2.VideoCapture(args["input"])

fps = FPS().start()

# payload pub
dict_ = {'Time': None, 'Payload': ''}
pub.start()

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = frame[1] if args.get("input", False) else frame

    # if we are viewing a video and we did not grab a frame then we
    # have reached the end of the video
    if args["input"] is not None and frame is None:
        break

    frame = imutils.resize(frame, width=400)
    # grab the frame dimensions and convert it to a blob

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)

    # pass the blob through the network and obtain the detections and
    # predictions
    start = time.time()
    net.setInput(blob)
    detections = net.forward()
    end = time.time()
    ls = [int(detections[0, 0, i, 1]) for i in range(detections.shape[2]) if int(detections[0, 0, i, 1]) == 15.0]
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > args["confidence"]:
            # extract the index of the class label from the
            # `detections`, then compute the (x, y)-coordinates of
            # the bounding box for the object
            # print("detection")
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx],
                                         confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    if len(ls) <= 11:
        end = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
        dict_['Time'] = end
        dict_['Payload'] = 'GREEN'
        payload = json.dumps(dict_)
        time.sleep(1)
        pub.publish(msg=payload)
        try:
            bot('Level', 'AulaMagna', 'GREEN')
        except:
            pass

    elif 11 < len(ls) <= 15:
        end = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
        dict_['Time'] = end
        dict_['Payload'] = 'BLUE'
        payload = json.dumps(dict_)
        time.sleep(1)
        pub.publish(msg=payload)
        try:
            bot('Level', 'AulaMagna', 'BLUE')
        except:
            pass
    elif 15 < len(ls) <= 25:
        end = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
        dict_['Time'] = end
        dict_['Payload'] = 'YELLOW'
        payload = json.dumps(dict_)
        time.sleep(1)
        pub.publish(msg=payload)
        try:
            bot('Level', 'AulaMagna', 'YELLOW')
        except:
            pass
    elif len(ls) > 25:
        end = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
        dict_['Time'] = end
        dict_['Payload'] = 'RED'
        payload = json.dumps(dict_)
        time.sleep(1)
        pub.publish(msg=payload)
        try:
            bot('Level', 'AulaMagna', 'RED')
        except:
            pass

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        dict_['Payload'] = 'STOP'
        dict_['Time'] = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
        payload = json.dumps(dict_)
        pub.publish(msg=payload)
        pub.stop()
        end_ = time.time()
        elap = round(end_ - start, 3)
        logger.info(f"single frame took {elap} seconds")
        break

    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
# if we are not using a video file, stop the camera video stream
if not args.get("input", False):
    vs.stop()

# otherwise, release the video file pointer
else:
    vs.release()
