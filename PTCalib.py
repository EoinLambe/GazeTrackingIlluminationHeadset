
import sys
#Ensure calib has access to required folders
sys.path.insert(0, 'home/pi/PanTiltFiles/servoHatFiles/')
from gpiozero import Button
import RPi.GPIO as GPIO
import zmq
from msgpack import loads
import Adafruit_PCA9685
import RPi.GPIO as GPIO
import time
import geometry
import gazemapping




def PTCalibrate():
	#View main for explanation 
    Pwm = Adafruit_PCA9685.PCA9685()
    Pwm.set_pwm_freq(400)
    
    yDir = True
    xDir = False
    switch = False

    xLen = 492 #492 

    xminPulse = 2490 - xLen
    #midPulse = 2490     #1820us in bits ~0°
    xmaxPulse = 2490 + xLen

    yLen = 385

    yminPulse = 2490 - yLen #~920us in bits ~-60°
    #midPulse = 2490     #1820us in bits ~0°
    ymaxPulse = 2490 + yLen #2120us in bits ~60°


	#Calibration Joystick
    up = Button(12)
    down = Button(6)
    left = Button(5)
    right = Button(13)
    middle = Button(16)


    
    laserPIN = 17
    GPIO.setup(laserPIN, GPIO.OUT)
    

    context = zmq.Context()
    # open a req port to talk to pupil
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


    sub.setsockopt_string(zmq.SUBSCRIBE, 'gaze')
    blinkTime = 0
    initTime = 0
    check = 0
    
    xOff = 0
    yOff = 0

	#Begin in the middle
    xPosPrev = 2490
    yPosPrev = 2490
    
    while True:
        try:
            topic = sub.recv_string()
            msg = sub.recv()
            msg = loads(msg, encoding='utf-8')
            xNorm, yNorm = msg['norm_pos']
            confidence = msg['confidence']

            yNorm = geometry.mapCoordinates(yNorm)

            xPos, yPos, check, initTime, switch = gazemapping.gazeToPos(xNorm, yNorm, check, initTime, switch, confidence
			
			#No averaging stack for calibration phase
            xPos = xPos + xOff
            yPos = yPos + yOff 
			
			#Blink sequence
            if switch == False:
                GPIO.output(laserPIN, 1)
                Pwm.set_pwm(xDir, 0, xPos)
                Pwm.set_pwm(yDir, 0, yPos)
            else:
                GPIO.output(laserPIN, 0)
                Pwm.set_pwm(xDir, 0, int(((xmaxPulse-xminPulse)*0.5)+xminPulse))
                Pwm.set_pwm(yDir, 0, int(((ymaxPulse-yminPulse)*0.5)+yminPulse))

            if up.is_pressed:
                yOff = yOff + 4
    
            elif down.is_pressed:
                yOff = yOff - 4
    
            elif left.is_pressed:
                xOff = xOff - 4
    
            elif right.is_pressed:
                xOff = xOff + 4
    
            elif middle.is_pressed:
                print('Calibration Complete.')
                break
            
            
            
        except KeyboardInterrupt:
            break
    
    return xOff, yOff, context
