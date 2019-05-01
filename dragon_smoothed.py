import numpy as np
import math



# settings
layers_number = 10 # number of layers (they are all identical)
iterations = 10
dimension = 1.9 # leght of the smallest segment in millimeters
thickness = 1.2
filename = 'dragon'

#skirt
skirt_rounds = 3
skirt_distance = 3
skirt_spacing = 1

#retraction
enable_optimized_path = True #i.e avoid crossing perimeters
enable_retraction = True
retraction = 2
recovery = 0.1

# plotting variables
starting_point = (150.0,60.0)
dz0=0.26 # first layer's height
dz=0.2 # other layer's height

Tbed='25' # bed temperature
Tex='210' # extruder temperature

#speeds [mm/min]
vel1=1200
vel2=2400
velf=7800

#extruded material = kE*lenght
kE =kE = thickness*dz/(math.pi*3**2/4)



# create the path

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
reversed_body = []
footer = []
header.append(';Dragon curve smoothed Gcode\n')
header.append(';author: FedericoSold\n')

header.append('M107 \n')
header.append('M140 S'+Tbed+' ; heat up bed\n')
header.append('M104 T0 S'+Tex+'; het up extruder\n')

header.append('G28 ; home all axes\n')
header.append('G1 Z5 F5000 ; lift nozzle \n')

header.append('G21 ; use millimeters\n')
header.append('G90\n') #use absolute coordinates for the XYZ axis
header.append('G92 E0\n') # reset extruder
header.append('M82\n') #use absolute coordinates for the extruder
header.append('M190 S'+Tbed+' ; wait bed temperature\n')
header.append('M109 T0 S'+Tex+' ; wait extruder temperature\n')
header.append('M106 S15 ; start fan\n')
header.append('G1 Z%f F%f \n' % (dz0, velf))

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

maxE = E


E = maxE
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
    E -= kE/math.sqrt(2)
    reversed_body.append('G1 X%f Y%f E%f\n' % ((3*old_position[0]+position[0])/4, (3*old_position[1]+position[1])/4, E))
    E -= kE*(1/2+1/math.sqrt(2))
    reversed_body.append('G1 X%f Y%f E%f\n' % ((old_position[0]+3*position[0])/4, (old_position[1]+3*position[1])/4, E))
reversed_body.append('G92 E0     ; Reset the extruder\n')

# create the skirt
header.append('; skirt \n')
for i in range(0,skirt_rounds):
    l = skirt_distance + i*skirt_spacing
    header.append('G92 E0     ; Reset the extruder\n')
    header.append('G0 X%f Y%f Z%f F%d \n' % (min_position[0]-l, min_position[1]-l, dz0, velf))
    E = max_position[1] - min_position[1] + 2*l
    header.append('G1 X%f Y%f E%f F%d \n' % (min_position[0]-l, max_position[1]+l, E*kE, vel1))
    E += max_position[0] - min_position[0] + 2*l
    header.append('G1 X%f Y%f E%f \n' % (max_position[0]+l, max_position[1]+l, E*kE))
    E += max_position[1] - min_position[1] + 2*l
    header.append('G1 X%f Y%f E%f \n' % (max_position[0]+l, min_position[1]-l, E*kE))
    E += max_position[0] - min_position[0] + 2*l
    header.append('G1 X%f Y%f E%f \n' % (min_position[0]-l, min_position[1]-l, E*kE))


footer.append('G92 Z0 E0 \n')
footer.append('G0 Z0.3 E-4 F1200 \n')
footer.append('G0 Z10 F1200 \n')
footer.append('G28 X0 ; go home\n') #home X axis
footer.append('G1 Y170 ; present the product \n')
footer.append('M104 S0 ; turn off extruder heater\n')
footer.append('M140 S0 ; turn off bed heater\n')
footer.append('M84 \n') #unlock motors

print('Writing file...')
# print Gcode
# open the file
file = open(filename+'.gcode', 'w')
for s in header:
    file.write(s)

for l in range(layers_number):
    file.write('; layer %d\n' %(l))

    if enable_optimized_path:
        if l == 0:
            if enable_retraction:
                file.write('G92 E0 \n')
                file.write('G0 E%f \n' % (-retraction))
            file.write('G0 Z%f \n' % (dz0+l*dz))
            file.write('G0 X%f  Y%f F%d \n' % (starting_point[0], starting_point[1], velf))
            if enable_retraction:
                file.write('G0 E%f \n' % (recovery))
                file.write('G92 E0 \n')
        else:
            file.write('G0 Z%f \n' % (dz0+l*dz))

        if l%2 == 1:
            for s in reversed(reversed_body):
                file.write(s)
        else:
            for s in body:
                file.write(s)
    else:
        if enable_retraction:
            file.write('G92 E0 \n')
            file.write('G0 E%f \n' % (-retraction))
        file.write('G0 Z%f \n' % (dz0+l*dz))
        file.write('G0 X%f  Y%f F%d \n' % (starting_point[0], starting_point[1], velf))
        if enable_retraction:
            file.write('G0 E%f \n' % (recovery))
            file.write('G92 E0 \n')
        for s in body:
            file.write(s)

for s in footer:
    file.write(s)
file.close()
