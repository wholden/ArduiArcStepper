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

class arduinoMotor:

    def __init__(self, serial, waittime=0.02, readlength=16,verbose=False):
        self.serial = serial
        self.waittime = waittime
        self.readlength = readlength
        self.verbose = verbose

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
        if self.verbose:
            print(r)
        return r

def initialize_motors(**kwargs):
    for ad in serialaddresses:
        ser = serial.Serial(ad,57600,timeout=0.005)
        motorhandle = arduinoMotor(ser,**kwargs)
        i = 0
        k = ''
        while k == '' and i < 5:
            k = motorhandle.sendrecv('DN')
            if k in motordict:
                motordict[k]['handle'] = motorhandle
                print('Motor with name \''+k+'\' is initialized.')
            i += 1
            time.sleep(0.5)

def go_to_degree(degree,blockuntilcomplete = True):
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
    motordict['sample']['handle'].sendrecv(xstr)

    if blockuntilcomplete:
        while int(motordict['sample']['handle'].sendrecv('PX')) != int(steps):
            time.sleep(2)

def go_to_mm(distance,blockuntilcomplete = True):
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
    motordict['camera']['handle'].sendrecv(xstr)

    if blockuntilcomplete:
        while int(motordict['camera']['handle'].sendrecv('PX')) != int(steps):
            time.sleep(2)

def get_camera_position():
    steps = int(motordict['camera']['handle'].sendrecv('PX'))
    distance = steps*motordict['camera']['mmperstep']
    return str(round(distance,2))+'mm'

def get_sample_position():
    steps = int(motordict['sample']['handle'].sendrecv('PX'))
    theta = steps*motordict['sample']['degperstep']
    return str(round(theta,2))+'deg'

def set_camera_position(distance):
    xpos = int(distance/motordict['camera']['mmperstep'])
    motordict['camera']['handle'].sendrecv('PX='+str(xpos))
    return 'camera position set to: ' + str(xpos) + 'steps'

def set_sample_position(distance):
    xpos = int(distance/motordict['sample']['degperstep'])
    motordict['sample']['handle'].sendrecv('PX='+str(xpos))
    return 'sample position set to: ' + str(xpos) + 'steps'

def camera_limit_minus():
    return motordict['camera']['handle'].sendrecv('L-')

def stop():
    motordict['camera']['handle'].sendrecv('STOP')
    motordict['sample']['handle'].sendrecv('STOP')
    return 'STOP command sent to both motors'
# initialize_motors()

