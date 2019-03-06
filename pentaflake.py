import numpy as np
import math

# settings
layer_repetitions = 2
layer_distribution = 'linear'
iterations = 4
dimension = 2
filename = 'pentaflake'

# useful constants
phi1 = (math.sqrt(5)-1)/2+1
theta = 2/5*math.pi
rot = np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta), math.cos(theta)]])


#variabili
starting_point = (50,15) # starting point in millimeters
dz0=0.2 # altezza primo layer
dz=0.3 # layer height
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
header.append(';peano curve Gcode\n')
header.append(';author: FedericoSold\n')

header.append('M140 S'+Tbed+' ; set bed temperature\n') # inizia a scaldare il piano fino a Tbed
header.append('M104 T0 S'+Tex+' ; set extruder temperature\n') # inizia a scaldare l'estrusore fino a Tex
header.append('G21 ; use millimeters\n') #unita' di misura in millimetri
header.append('G90\n') #usa coordinate assolute ripsetto all'origine della macchina
header.append('G92 E0 ; reset the extruder\n') # resetta la posizione dell'estrusore
header.append('M82\n') #usa coordinate assolute anche per l'estusore
header.append('M190 S'+Tbed+' ; wait for bed heating\n') # aspetta che la temperatura del piano sia raggiunta
header.append('M109 T0 S'+Tex+' ; wait for extruder heating\n') # aspetta che la temperatura dell'estrusore sia raggiunta
header.append('M106 S15 ; fan\n') #accendi la ventola (0 ferma 255 massima)

footer = []
footer.append('M104 S0 ; turn off extruder heater\n') #spegni l'estusore
footer.append('M140 S0 ; turn off bed heater\n') # spegni il piano
footer.append('G28 X0 ; go home\n') #home X axis
footer.append('M84\n') #sblocca i motori

body = ["" for x in range(iterations)]
for l in range(iterations):
    body[l] += ';iteration '+str(l)+'\n'

def getNextVert(vert1,vert2):
    edge = vert2-vert1
    return vert2 + np.matmul(rot,edge)

def drawPentagon(v1, v2, layer):
    v3 = getNextVert(v1, v2)
    v4 = getNextVert(v2, v3)
    v5 = getNextVert(v3, v4)
    body[layer] += 'G92 E0     ; Reset the extruder \n'
    E = kE * math.sqrt(sum((v2-v1)**2))
    body[layer] += 'G1 X%f Y%f \n' % (v1[0], v1[1])
    body[layer] += 'G1 X%f Y%f E%f \n' % (v2[0], v2[1], E)
    body[layer] += 'G1 X%f Y%f E%f \n' % (v3[0], v3[1], 2*E)
    body[layer] += 'G1 X%f Y%f E%f \n' % (v4[0], v4[1], 3*E)
    body[layer] += 'G1 X%f Y%f E%f \n' % (v5[0], v5[1], 4*E)
    body[layer] += 'G1 X%f Y%f E%f \n' % (v1[0], v1[1], 5*E)


def draw(vert1, vert2, layer):
    # the layer can be calculated from start and end
    if (layer<iterations):
        # draw line
        drawPentagon(vert1, vert2, layer)

        # draw upper iterations
        verts =[vert1, vert2]
        verts.append(getNextVert(verts[0],verts[1]))
        verts.append(getNextVert(verts[1],verts[2]))
        verts.append(getNextVert(verts[2],verts[3]))
        verts.append(vert1)

        for j in range(5):
            draw(verts[j], verts[j+1]-(verts[j+1]-verts[j])/phi1, layer+1)


draw(np.array(starting_point), np.array([starting_point[0]+dimension,starting_point[1]]), 0)

# print the Gcode
file = open(filename+'.gcode', 'w')
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
