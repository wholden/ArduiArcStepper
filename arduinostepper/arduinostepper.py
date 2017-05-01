import serial
import time
import re

motordict = {'camera':{'devname':'camera','stepsperrev':200,'leadscrewpitch':0.635,'microstep':16},
            'sample':{'devname':'sample','stepsperrev':200,'pulleyratio':16/60,'microstep':16}}
motordict['camera']['mmperstep'] = motordict['camera']['leadscrewpitch']/motordict['camera']['stepsperrev']/motordict['camera']['microstep']
motordict['sample']['degperstep'] = 360*motordict['sample']['pulleyratio']/motordict['sample']['stepsperrev']/motordict['sample']['microstep']

serialaddresses = ['/dev/ttyACM0','/dev/ttyACM1']

# serial0 = serial.Serial('/dev/ttyACM0',57600,timeout=0.001)
# serial1 = serial.Serial('/dev/ttyACM1',57600,timeout=0.001)
initialize_motors()

class arduinoMotor:

    def __init__(self, serial, waittime=0.01, readlength=16):
        self.serial = serial
        self.waittime = waittime
        self.readlength = readlength

    def sendrecv(self, string):
        self.serial.write(string.encode('ascii'))
        time.sleep(self.waittime)
        return self.readAndParse()

    def readAndParse(self):
        response = self.serial.read(self.readlength)
        try:
            r = re.match(r'(.*)\r', response.decode('utf-8')).group(1)
        except AttributeError:
            r = ''
        return r

def initialize_motors():
    for ad in serialaddresses:
        ser = serial.Serial(ad,57600,timeout=0.001)
        motorhandle = arduinoMotor(ser)
        k = motorhandle.sendrecv('DN')
        if k is in motordict:
            motordict[k]['handle'] = motorhandle
        print('Motor with name '+k+' is initialized'.)

def go_to_degree(degree):
    """Move sample motor to angular position indicated by degree.
    
    This moves the sample rotator to the indicated position.
    Current implementation sets degree=0 to location at 
    powerup of the controller. Zero location can be reset
    by sending 'PX=0' string to the controller.

    Angular position is calculated based on configuration
    in motordict dictionary.  Calculation makes use of
    'pulleyratio', 'stepsperrev', and 'microstep'.

    Args:
        degree: Degree of position to rotate to.
    """
    steps = degree/motordict['sample']['degperstep']
    xstr='X'+str(int(steps))
    SendRecv(motordict['sample']['handle'],xstr)

def go_to_mm(distance):
    """Move camera motor to position indicated by distance(mm).
    
    This moves the camera stage to the indicated position.
    Make sure to zero the controller out by using the 'L-'
    command string, so that distance=0 is properly calibrated.

    Distance (mm) is calculated based on configuration
    in motordict dictionary.  Calculation makes use of
    'leadscrewpitch', 'stepsperrev', and 'microstep'.

    Args:
        distance: Distance in mm to move the camera to.
    """
    steps = distance/motordict['camera']['mmperstep']
    xstr="X"+str(int(steps))
    print(xstr)
    SendRecv(motordict['camera']['handle'],xstr)

def get_camera_position():
    steps = int(SendRecv(motordict['camera']['handle'],'PX')[1])
    distance = steps*motordict['camera']['mmperstep']
    return str(round(distance,2))+'mm'

def get_sample_position():
    steps = int(SendRecv(motordict['sample']['handle'],'PX')[1])
    theta = steps*motordict['sample']['degperstep']
    return str(round(theta,2))+'deg'