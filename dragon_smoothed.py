import numpy as np
import math

# settings
layers_number = 10 # number of layers (they are all identical)
iterations = 12
dimension = 4 # leght of the smallest segment in millimeters

# plotting variables
starting_point = (100,100) # Use the center of the printing space
dz0=0.2 # first layer's height
dz=0.2 # other layer's height

Tbed='15' # temperatura piano
Tex='210' # temperatura estrusore
v1='1200' # velocita' primo layer mm/min (20 mm/s)
v2='2400' # velocita' altri layer mm/min (40 mm/s)
vf='7800' # movimenti rapidi (130 mm/s)
kE = 2*dz*0.4/math.pi/1.75**2 # moltiplicatore per quantità da estrudere

# usefull costants

# crate the path

def reverse(p):
    q = reversed(p)
    return [(-1)*x for x in q]

path = [1]
for i in range(iterations):
    path = path+[1]+reverse(path)

# turn the path into Gcode

header = []
body = []
footer = []
header.append(';Dragon curve smoothed Gcode')
header.append(';author: FedericoSold')

header.append('M140 S'+Tbed) # inizia a scaldare il piano fino a Tbed
header.append('M104 T0 S'+Tex) # inizia a scaldare l'estrusore fino a Tex
header.append('G21 ; use millimeters') #unita' di misura in millimetri
header.append('G90') #usa coordinate assolute ripsetto all'origine della macchina
header.append('G92 E0') # resetta la posizione dell'estrusore
header.append('M82') #usa coordinate assolute anche per l'estusore
header.append('M190 S'+Tbed+' ;bed temperature') # aspetta che la temperatura del piano sia raggiunta
header.append('M109 T0 S'+Tex+' ; extruder temperature') # aspetta che la temperatura dell'estrusore sia raggiunta
header.append('M106 S15 ; fan') #accendi la ventola (0 ferma 255 massima)

body.append('G92 E0     ; Reset the extruder')
E = 0

direction = 0
position = np.array(starting_point)
for step in path:
    direction += step
    direction %= 4
    old_position = position.copy()
    if direction == 0:
        position[0] += dimension
    elif direction == 1:
        position[1] += dimension
    elif direction == 2:
        position[0] += -dimension
    else:
        position[1] += -dimension
    # draw the lines
    E += kE/math.sqrt(2)
    body.append('G1 X%f Y%f E%f' % ((3*old_position[0]+position[0])/4, (3*old_position[1]+position[1])/4, E))
    E += kE*(1/2+1/math.sqrt(2))
    body.append('G1 X%f Y%f E%f' % ((old_position[0]+3*position[0])/4, (old_position[1]+3*position[1])/4, E))

footer.append('M104 S0') #spegni l'estusore
footer.append('M140 S0') # spegni il piano
footer.append('G28 X0') #home X axis
footer.append('M84') #sblocca i motori

# print Gcode
for s in header:
    print(s)
for l in range(layers_number):
    print('; layer %d' %(l))
    print('G0 X%f  Y%f Z%f' % (starting_point[0], starting_point[1], dz0+l*dz))
    for s in body:
        print(s)
for s in footer:
    print(s)
