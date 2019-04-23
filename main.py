
import sys
#Ensure main has access to required folders
sys.path.insert(0, 'home/pi/PanTiltFiles/servoHatFiles/')
import zmq
from msgpack import loads
import Adafruit_PCA9685
import RPi.GPIO as GPIO
import time
import geometry
import gazemapping
import PTCalib
from collections import deque



#Servo PWM HAT set freq
Pwm = Adafruit_PCA9685.PCA9685()
Pwm.set_pwm_freq(400)


yDir = True
xDir = False
switch = False

#Set Pulse lengths corresponsing to 0 and 1 gaze coordinates
xLen = 492 
xminPulse = 2490 - xLen
#midPulse = 2490     #1820us in bits ~0°
xmaxPulse = 2490 + xLen

yLen = 385

yminPulse = 2490 - yLen #~920us in bits ~-60°
#midPulse = 2490     #1820us in bits ~0°
ymaxPulse = 2490 + yLen #2120us in bits ~60°


#Turn on Laser
laserPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(laserPIN, GPIO.OUT)

#Calibrate PTPlatform
xOff, yOff, context = PTCalib.PTCalibrate()


#Open req port to talk to pupil
addr = '192.168.137.1'  # remote ip or localhost
req_port = "50020"  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))

# ask for the sub port
req.send_string('SUB_PORT')
sub_port = req.recv_string()

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))

#Subscribe to gaze coordinates
sub.setsockopt_string(zmq.SUBSCRIBE, 'gaze')

#For more info on above go to https://github.com/pupil-labs/pupil-helpers/blob/master/python/filter_messages.py

blinkTime = 0
initTime = 0
check = 0
xPosPrev = 2490
yPosPrev = 2490

#X and Y averaging stacks
yList = deque([2490, 2490, 2490, 2490, 2490, 2490, 2490, 2490, 2490, 2490])
xList = deque([2490, 2490, 2490, 2490, 2490, 2490, 2490, 2490, 2490, 2490])

while True:
    try:
        topic = sub.recv_string()
        msg = sub.recv()
        msg = loads(msg, encoding='utf-8')
        xNorm, yNorm = msg['norm_pos']
        confidence = msg['confidence']
        
		#Map the y coordinate depending on distance - will be useful with vergeance measurement
        yNorm = geometry.mapCoordinates(yNorm)
		
		#Convert gaze coordinate to PWM signal
        xPos, yPos, check, initTime, switch = gazemapping.gazeToPos(xNorm, yNorm, check, initTime, switch, confidence)
        
        #If gaze confidence is low, keep same coordinates as last iteration
        if confidence < 0.6:
            xPos = xPosPrev
            yPos = yPosPrev
        

            
        xPosPrev = xPos
        yPosPrev = yPos

		#Add calibrated offsets
        xPos = xPos + xOff
        yPos = yPos + yOff

		#Update averaging stacks
        xList.pop()
        xList.appendleft(xPos)
        
        yList.pop()
        yList.appendleft(yPos)
        
		#Blink sequence switch
        if switch == False:
            GPIO.output(laserPIN, 1)
            Pwm.set_pwm(xDir, 0, int(sum(xList)/len(xList)))
            Pwm.set_pwm(yDir, 0, int(sum(yList)/len(yList)))
        else:
            GPIO.output(laserPIN, 0)
            Pwm.set_pwm(xDir, 0, 2490)
            Pwm.set_pwm(yDir, 0, 2490)
            
            
    except KeyboardInterrupt:
        GPIO.cleanup()
        print('POWER OFF')
        break
