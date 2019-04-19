import time
import math
import cv2
import mss
import numpy
import keyboard
import threading
from win10toast import ToastNotifier

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
    cap = 6

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
toaster = ToastNotifier()

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
            img = sct.grab(sct.monitors[1])
            fps = 1 / (time.time() - last_time)
            qlock.acquire()
            q.addFrame(Frame(img,fps))
            qlock.release()
            last_time = time.time()

def publishvideo():
    global thot
    global fhot
    global phot
    print('starting')
    qlock.acquire()
    keyboard.remove_hotkey(thot)
    keyboard.remove_hotkey(fhot)
    keyboard.remove_hotkey(phot)
    print(q.avg())
    print(len(q.frames))
    exampleframe = q.frames[0].pixels;
    exampleframe = numpy.array(exampleframe)
    exampleframe = numpy.flip(exampleframe[:, :, :3], 2)  # 1
    width = len(exampleframe[0])
    height = len(exampleframe)
    writer = cv2.VideoWriter('vid' + str(c.count()) +'.mp4',cv2.VideoWriter_fourcc(*'mp4v'), math.floor(q.avg()), (width,height))
    for plz in q.frames:
        nextframe = plz.pixels;
        nextframe = numpy.array(nextframe)
        nextframe = numpy.flip(nextframe[:, :, :3], 2)  # 1
        nextframe = cv2.cvtColor(nextframe, cv2.COLOR_BGR2RGB)
        writer.write(nextframe)
    qlock.release()
    thot = keyboard.add_hotkey('i', publishvideo)
    fhot = keyboard.add_hotkey('o', finish)
    phot = keyboard.add_hotkey('u', publishimage)
    toaster.show_toast("Clip Done", "Clip has been saved")

def publishimage():
    with mss.mss() as sct:
        frame = sct.grab(sct.monitors[1])
        frame = numpy.array(frame)
        frame = numpy.flip(frame[:,:,:3], 2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite('img' + str(c.count()) + '.jpg', frame)



thot = keyboard.add_hotkey('i', publishvideo)
fhot = keyboard.add_hotkey('o', finish)
phot = keyboard.add_hotkey('u', publishimage)

recordvideo()
keyboard.remove_hotkey(thot)
keyboard.remove_hotkey(fhot)
keyboard.remove_hotkey(phot)
