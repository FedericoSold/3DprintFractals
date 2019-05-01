import numpy as np
import math

# settings
layer_repetitions = 20 # number of layers (they are all identical)
layer_distribution = 'linear'
iterations = 5
print_antisnowflake = True
filename = 'koch_snowflake'

# useful constants
bhr = math.sqrt(3)/2
theta = math.pi*2/3
rot = np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta), math.cos(theta)]])


# variables
starting_point = (10,10) # starting point in millimeters
dz0=0.2 # first layer height
dz=0.2 # layer height
k = 2
dx = 0.2

Tbed='65' # bed temperature
Tex='200' # extruder temperature
kE = 2*dz*0.4/math.pi/1.75**2 #extruded material = kE*lenght


dimension = 100
thickness = 1

header = []
header.append(';peano curve Gcode\n')
header.append(';author: Federico\n')

header.append('M140 S'+Tbed+'\n') # heat up the bed
header.append('M104 T0 S'+Tex+'\n') # iheat up the extruder
header.append('G21 ; use millimeters\n') # use millimeters
header.append('G90\n') # use absolute coordinates
header.append('G92 E0\n') # reset extruder position
header.append('M82\n') # use absolute coordinates
header.append('M190 S'+Tbed+' ;bed temperature\n') # wait for bet temperature
header.append('M109 T0 S'+Tex+' ; extruder temperature\n') # wait for extruder temperature
header.append('M106 S15 ; fan\n') # turn on the fan

footer = []
footer.append('M104 S0\n') # turn off extruder
footer.append('M140 S0\n') # turn off bed
footer.append('G28 X0\n') # go home X axis
footer.append('M84\n') # free the motors

body = ["" for x in range(iterations)]
for l in range(iterations):
    body[l] += ';iteration '+str(l)+'\n'

def getNextVert(vert1,vert2):
    edge = vert2-vert1
    return vert2 + np.matmul(rot,edge)

def drawTriangle(v1, v2, layer):
    v3 = getNextVert(v1, v2)
    body[layer] += 'G92 E0     ; Reset the extruder \n'
    E = kE * math.sqrt(sum((v2-v1)**2))
    body[layer] += 'G1 X%f Y%f \n' % (v1[0], v1[1])
    body[layer] += 'G1 X%f Y%f E%f \n' % (v2[0], v2[1], E)
    body[layer] += 'G1 X%f Y%f E%f \n' % (v3[0], v3[1], 2*E)
    body[layer] += 'G1 X%f Y%f E%f \n' % (v1[0], v1[1], 3*E)


def draw(vert1, vert2, layer):
    if (layer<iterations):
        length = math.sqrt(sum((vert2-vert1)**2))
        point1 = vert1 + (vert2-vert1)/3
        point2 =vert1 + (vert2-vert1)*2/3
        point3 = getNextVert(point1, point2)

        # draw border lines
        body[layer] += 'G92 E0    ; Reset the extruder \n'
        E = kE * length/3
        body[layer] += 'G1 X%f Y%f \n' % (vert1[0], vert1[1])
        body[layer] += 'G1 X%f Y%f E%f \n' % (point1[0], point1[1], E)
        body[layer] += 'G1 X%f Y%f E%f \n' % (point3[0], point3[1], 2*E)
        body[layer] += 'G1 X%f Y%f E%f \n' % (point2[0], point2[1], 3*E)
        body[layer] += 'G1 X%f Y%f E%f \n' % (vert2[0], vert2[1], 4*E)
        # draw inner triangle
        for l in range(layer,iterations):
            # commet the next line if you don't want support trinagles
            drawTriangle(point1+(vert2-vert1)*dx/length, point2-(vert2-vert1)*dx/length, l)
            pass

        # draw under iterations
        draw(vert1, point1, layer+1)
        draw(point1, point3, layer+1)
        draw(point3, point2, layer+1)
        draw(point2, vert2, layer+1)

vertex = getNextVert(np.array(starting_point), np.array([starting_point[0]+dimension,starting_point[1]+dimension]))
# add the skirt
header.append('G0 X%f  Y%f Z%f ; skirt\n' % (starting_point[0]-5, starting_point[1]-5, dz0))
center = (vertex+2*np.array(starting_point)+np.array([dimension,dimension]))/3
header.append('G92 E0    ; Reset the extruder\n')
header.append('G2 X%F Y%f I%F J%f E%f\n'% (starting_point[0]-5, starting_point[1]-5, center[0], center[1], kE*math.pi*(dimension+10)/math.sqrt(3)))
header.append('G2 X%F Y%f I%F J%f E%f\n'% (starting_point[0]-4, starting_point[1]-4, center[0], center[1], kE*math.pi*(dimension+18)/math.sqrt(3)))

if print_antisnowflake:
    draw(np.array(starting_point), np.array([starting_point[0]+dimension,starting_point[1]+dimension]), 0)
    draw(np.array([starting_point[0]+dimension,starting_point[1]+dimension]), vertex, 0)
    draw(vertex, np.array([starting_point[0],starting_point[1]]), 0)
else:
    draw(np.array([starting_point[0]+dimension,starting_point[1]+dimension]), np.array(starting_point), 0)
    draw(vertex, np.array([starting_point[0]+dimension,starting_point[1]+dimension]), 0)
    draw(np.array([starting_point[0],starting_point[1]]), vertex, 0)


# print the Gcode on file
file = open(filename+'.gcode','w')
for w in header:
    file.write(w)
j = 1
l = 0
for e in reversed(body):
    if layer_distribution == 'linear':
        for i in range(layer_repetitions):
            file.write('G0 X%f  Y%f Z%f ; layer%d\n' % (starting_point[0], starting_point[1], l*dz+dz0, l))
            file.write(e)
            l += 1
    elif layer_distribution == 'exponential':
        for i in range(layer_repetitions**j):
            file.write('G0 X%f  Y%f Z%f ; layer%d\n' % (starting_point[0], starting_point[1], l*dz+dz0, l))
            file.write(e)
            l += 1
    else:
        file.write('G0 X%f  Y%f Z%f ; layer%d\n' % (starting_point[0], starting_point[1], l*dz+dz0, l))
        file.write(e)
        l += 1
    j += 1
for w in footer:
    file.write(w)
file.close()
