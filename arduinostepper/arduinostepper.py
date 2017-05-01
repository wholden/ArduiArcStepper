import serial
import time
import re

sampleserial = serial.Serial('/dev/ttyACM1',57600,timeout=0.001)
cameraserial = serial.Serial('/dev/ttyACM2',57600,timeout=0.001)

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

samplemotor = arduinoMotor(sampleserial)
assert samplemotor.sendrecv('DN')=='sample', 'sample motor error: name is not \'sample\''
cameramotor = arduinoMotor(cameraserial)
assert cameramotor.sendrecv('DN')=='camera', 'camera motor error: name is not \'camera\''