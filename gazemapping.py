import time


def gazeToPos(xNorm, yNorm, check, initTime, switch, confidence):

    xLen = 492*2 #492

    xminPulse = 2490 - xLen
    #midPulse = 2490     #1820us in bits ~0°
    xmaxPulse = 2490 + xLen

    yLen = 450 #385

    yminPulse = 2490 - yLen #~920us in bits ~-60°
    #midPulse = 2490     #1820us in bits ~0°
    ymaxPulse = 2490 + yLen #2120us in bits ~60°
    
	
	#Blink threshold - future iterations this could be adapted depending on brightness
    if confidence < 0.32:
        check += 1
        xPos = 2490
        yPos = 2490
        if check == 1:
            initTime = time.time()
            blinkTime = 0
        elif check > 1:
			#If an elongated blink is seen
            blinkTime = time.time() - initTime
            if blinkTime > 0.5:
                switch = not switch
                blinkTime = 0
                initTime = 0
                check = 0
                print('blink')
            else:
                switch = switch
    else:
        blinkTime = 0
        check = 0
        
		#Otherwise, map coordinates accordingly
        xPos = int(((xmaxPulse-xminPulse)*xNorm)+xminPulse)
        yPos = int(((ymaxPulse-yminPulse)*yNorm)+yminPulse)
        
    return xPos, yPos, check, initTime, switch
