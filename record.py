import time
import math
import cv2
import mss
import numpy
import keyboard
import threading

class Count:
    c = 0
    def count(self):
        self.c = self.c + 1
        return self.c

class Frame:
    pixels = []
    fps = 0

    def __init__(self, pixels, fps):
        self.pixels = pixels
        self.fps = fps

class FrameQueue:
    frames = []
    cap = 5

    def avg(self):
        sum = 0
        for frame in self.frames:
            sum = sum + frame.fps
        return sum / len(self.frames)

    def addFrame(self, frame):
        self.frames.append(frame)
        self.manageframecount()

    def manageframecount(self):
        while len(self.frames) / self.avg() > self.cap:
            self.frames.pop(1)

done = False
qlock = threading.Lock()

def finish():
    global done
    done = True


q = FrameQueue()
c = Count()

def recordvideo():
    with mss.mss() as sct:
        # Part of the screen to capture
        last_time = time.time()
        while not done:
            img = numpy.array(sct.grab(sct.monitors[1]))
            img = numpy.flip(img[:, :, :3], 2)  # 1
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  #
            fps = 1 / (time.time() - last_time)
            qlock.acquire()
            q.addFrame(Frame(img,fps))
            qlock.release()
            last_time = time.time()

def publishvideo():
    global thot
    global fhot
    print('starting')
    qlock.acquire()
    keyboard.remove_hotkey(thot)
    keyboard.remove_hotkey(fhot)
    print(q.avg())
    print(len(q.frames))
    exampleframe = q.frames[0].pixels;
    width = len(exampleframe[0])
    height = len(exampleframe)
    writer = cv2.VideoWriter('vid' + str(c.count()) +'.mp4',cv2.VideoWriter_fourcc(*'mp4v'), math.floor(q.avg()), (width,height))
    for plz in q.frames:
        writer.write(plz.pixels)
    qlock.release()
    thot = keyboard.add_hotkey('i', publishvideo)
    fhot = keyboard.add_hotkey('o', finish)

def publishimage():
    global thot
    global fhot
    qlock.acquire()
    keyboard.remove_hotkey(thot)
    keyboard.remove_hotkey(fhot)



thot = keyboard.add_hotkey('i', publishvideo)
fhot = keyboard.add_hotkey('o', finish)
recordvideo()
keyboard.remove_hotkey(thot)
keyboard.remove_hotkey(fhot)
