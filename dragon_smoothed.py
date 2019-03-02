import numpy as np
import math
import sys


# settings
layers_number = 10 # number of layers (they are all identical)
iterations = 12
dimension = 4 # leght of the smallest segment in millimeters
filename = 'dragon'

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

print('Calculating the path...')
path = [1]
for i in range(iterations):
    path = path+[1]+reverse(path)

# turn the path into Gcode

header = []
body = []
footer = []
header.append(';Dragon curve smoothed Gcode\n')
header.append(';author: FedericoSold\n')

header.append('M140 S'+Tbed+' ; heat up bed\n') # inizia a scaldare il piano fino a Tbed
header.append('M104 T0 S'+Tex+'; het up extruder\n') # inizia a scaldare l'estrusore fino a Tex
header.append('G21 ; use millimeters\n') #unita' di misura in millimetri
header.append('G90\n') #usa coordinate assolute ripsetto all'origine della macchina
header.append('G92 E0\n') # resetta la posizione dell'estrusore
header.append('M82\n') #usa coordinate assolute anche per l'estusore
header.append('M190 S'+Tbed+' ; wait bed temperature\n') # aspetta che la temperatura del piano sia raggiunta
header.append('M109 T0 S'+Tex+' ; wait extruder temperature\n') # aspetta che la temperatura dell'estrusore sia raggiunta
header.append('M106 S15 ; start fan\n') #accendi la ventola (0 ferma 255 massima)

print('Creating Gcode...')
body.append('G92 E0     ; Reset the extruder\n')
E = 0
direction = 0
position = np.array(starting_point)
max_position = position.copy()
min_position = position.copy()
for step in path:
    direction += step
    direction %= 4
    old_position = position.copy()
    if direction == 0:
        position[0] += dimension
        if position[0]>max_position[0]:
            max_position[0] = position[0]
    elif direction == 1:
        position[1] += dimension
        if position[1]>max_position[1]:
            max_position[1] = position[1]
    elif direction == 2:
        position[0] += -dimension
        if position[0]<min_position[0]:
            min_position[0] = position[0]
    else:
        position[1] += -dimension
        if position[1]<min_position[1]:
            min_position[1] = position[1]
    # draw the lines
    E += kE/math.sqrt(2)
    body.append('G1 X%f Y%f E%f\n' % ((3*old_position[0]+position[0])/4, (3*old_position[1]+position[1])/4, E))
    E += kE*(1/2+1/math.sqrt(2))
    body.append('G1 X%f Y%f E%f\n' % ((old_position[0]+3*position[0])/4, (old_position[1]+3*position[1])/4, E))

# crate the skirt
header.append('G92 E0     ; Reset the extruder\n')
header.append('G0 X%f Y%f Z%f ; make skirt\n' % (min_position[0]-5, min_position[1]-5, dz0))
header.append('G1 X%f Y%f E%f \n' % (min_position[0]-5, max_position[1]+5, E))
header.append('G1 X%f Y%f E%f \n' % (max_position[0]+5, max_position[1]+5, E))
header.append('G1 X%f Y%f E%f \n' % (max_position[0]+5, min_position[1]-5, E))
header.append('G1 X%f Y%f E%f \n' % (min_position[0]-5, min_position[1]-5, E))
header.append('G0 X%f Y%f \n' % (min_position[0]-4, min_position[1]-4))
header.append('G1 X%f Y%f E%f \n' % (min_position[0]-4, max_position[1]+4, E))
header.append('G1 X%f Y%f E%f \n' % (max_position[0]+4, max_position[1]+4, E))
header.append('G1 X%f Y%f E%f \n' % (max_position[0]+4, min_position[1]-4, E))
header.append('G1 X%f Y%f E%f \n' % (min_position[0]-4, min_position[1]-4, E))

footer.append('M104 S0 ; turn off the extruder\n') #spegni l'estusore
footer.append('M140 S0 ; turn off bed heat\n') # spegni il piano
footer.append('G28 X Y ; go home\n') #home X axis
footer.append('M84 ; stop idle hold\n') #sblocca i motori

print('Writing file...')
# print Gcode
# open the file
file = open(filename+'.gcode', 'w')
for s in header:
    file.write(s)
for l in range(layers_number):
    file.write('; layer %d\n' %(l))
    file.write('G0 X%f  Y%f Z%f\n' % (starting_point[0], starting_point[1], dz0+l*dz))
    for s in body:
        file.write(s)
for s in footer:
    file.write(s)
