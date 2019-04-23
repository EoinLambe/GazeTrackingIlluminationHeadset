import math

def mapCoordinates(yNorm):

	#For use when vergence distance is known
    normdist = 80.0
	#Some helmet measurements
    offset = 10.3
    alpha_zero = 39.0
    if yNorm >= 0.5:
        alpha = alpha_zero - (60.0 * (yNorm - 0.5))
    else:
        alpha = alpha_zero + (60.0 * (0.5 - yNorm))
        
    gamma = 180.0 - 51.0 - alpha
    b = math.sin(math.radians(90)) * normdist / math.sin(math.radians(gamma))
    c = math.sqrt(offset**2 + b**2 - (2 * offset * b * math.cos(math.radians(alpha))))
    beta = math.degrees(math.acos((offset**2 + c**2 - b**2)/(2*offset*c)))
    result = 180.0 - alpha - beta
    yNorm = yNorm - (result / 60.0)

    return yNorm
    
    
    
