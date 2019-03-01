import numpy as np
import math

# settings
layer_repetitions = 2
layer_distribution = 'exponential'
iterations = 5
print_antisnowflake = False

# useful constants
bhr = math.sqrt(3)/2
theta = math.pi*2/3
rot = np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta), math.cos(theta)]])


#variabili
starting_point = (10,10) # starting point in millimeters
dz0=0.2 # first layer height
dz=0.2 # layer height
k = 2
dx = 0.2

Tbed='15' # temperatura piano
Tex='210' # temperatura estrusore
v1='1200' # velocita' primo layer mm/min (20 mm/s)
v2='2400' # velocita' altri layer mm/min (40 mm/s)
vf='7800' # movimenti rapidi (130 mm/s)
kE = 2*dz*0.4/math.pi/1.75**2 # moltiplicatore per quantità da estrudere


dimension = 100
thickness = 1

header = []
header.append(';peano curve Gcode')
header.append(';author: Federico')

header.append('M140 S'+Tbed) # inizia a scaldare il piano fino a Tbed
header.append('M104 T0 S'+Tex) # inizia a scaldare l'estrusore fino a Tex
header.append('G21 ; use millimeters') #unita' di misura in millimetri
header.append('G90') #usa coordinate assolute ripsetto all'origine della macchina
header.append('G92 E0') # resetta la posizione dell'estrusore
header.append('M82') #usa coordinate assolute anche per l'estusore
header.append('M190 S'+Tbed+' ;bed temperature') # aspetta che la temperatura del piano sia raggiunta
header.append('M109 T0 S'+Tex+' ; extruder temperature') # aspetta che la temperatura dell'estrusore sia raggiunta
header.append('M106 S15 ; fan') #accendi la ventola (0 ferma 255 massima)

footer = []
footer.append('M104 S0') #spegni l'estusore
footer.append('M140 S0') # spegni il piano
footer.append('G28 X0') #home X axis
footer.append('M84') #sblocca i motori

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
    # the layer can be calculated from start and end
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
if print_antisnowflake:
    draw(np.array(starting_point), np.array([starting_point[0]+dimension,starting_point[1]+dimension]), 0)
    draw(np.array([starting_point[0]+dimension,starting_point[1]+dimension]), vertex, 0)
    draw(vertex, np.array([starting_point[0],starting_point[1]]), 0)
else:
    draw(np.array([starting_point[0]+dimension,starting_point[1]+dimension]), np.array(starting_point), 0)
    draw(vertex, np.array([starting_point[0]+dimension,starting_point[1]+dimension]), 0)
    draw(np.array([starting_point[0],starting_point[1]]), vertex, 0)


# print the Gcode
for w in header:
    print(w)
j = 1
l = 0
for e in reversed(body):
    if layer_distribution == 'linear':
        for i in range(layer_repetitions):
            print('G0 X%f  Y%f Z%f ; layer%d' % (starting_point[0], starting_point[1], l*dz+dz0, l))
            print(e)
            l += 1
    elif layer_distribution == 'exponential':
        for i in range(layer_repetitions**j):
            print('G0 X%f  Y%f Z%f ; layer%d' % (starting_point[0], starting_point[1], l*dz+dz0, l))
            print(e)
            l += 1
    else:
        print('G0 X%f  Y%f Z%f ; layer%d' % (starting_point[0], starting_point[1], l*dz+dz0, l))
        print(e)
        l += 1
    j += 1
for w in footer:
    print(w)
