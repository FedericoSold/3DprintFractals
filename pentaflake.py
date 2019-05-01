import numpy as np
import math

# settings
layer_repetitions = 30
layer_distribution = 'quadratic'
iterations = 4
dimension = 80
thickness = 1.2
filename = 'pentaflake'

skirt_rounds = 3
skirt_spacing = 2
skirt_distance = 2

enable_optimized_path = True #i.e. avoid crossing perimeters
enable_retraction = False
retraction = 2
zlift = 0.2

# useful constants
phi1 = (math.sqrt(5)-1)/2+1
theta = 2/5*math.pi
rot = np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta), math.cos(theta)]])


#variabili
starting_point = (50,25) # starting point in millimeters
dz0=0.3 # first layer height
dz=0.2 # layer height
k = 2
dx = 0.2

Tbed='25' # bed temperature
Tex='210' # extruder temperature

#speeds [mm/min]
vel1=1200
vel2=2400
velf=7800

#extruded material = kE*lenght
kE = thickness*dz/(math.pi*3**2/4)


header = []
header.append(';pentaflake curve Gcode\n')
header.append(';author: FedericoSold\n')

header.append('M107 \n')
header.append('M140 S'+Tbed+' ; set bed temperature\n') # inizia a scaldare il piano fino a Tbed
header.append('M104 T0 S'+Tex+' ; set extruder temperature\n') # inizia a scaldare l'estrusore fino a Tex
if enable_retraction:
    header.append('M207 S%f F%f Z%f ; set retraction \n' % (retraction,velf,zlift))
    header.append('M209 \n')
#
header.append('G28 ; home all axes\n')
header.append('G1 Z5 F5000 ; lift nozzle \n')
#
header.append('G21 ; use millimeters\n')
header.append('G90\n') #use absolute coordinates
header.append('M82\n') #use absolute coordinates for the extruder
header.append('M190 S'+Tbed+' ; wait for bed heating\n')
header.append('M109 T0 S'+Tex+' ; wait for extruder heating\n')
header.append('M106 S15 ; fan\n')
header.append('G1 Z%f F%f \n' % (dz0, velf))

footer = []
footer.append('G92 Z0 E0 \n')
footer.append('G0 Z0.3 E-4 F1200 \n')
footer.append('G0 Z10 F1200 \n')
footer.append('G28 X0 ; go home\n') #home X axis
footer.append('G1 Y170 ; present the product \n')
footer.append('M104 S0 ; turn off extruder heater\n')
footer.append('M140 S0 ; turn off bed heater\n')
footer.append('M84 \n') #unlock motors

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

    '''
    if enable_retraction:
        body[layer] += 'G10 \n'
    body[layer] += 'G1 X%f Y%f \n' % (v1[0], v1[1])
    if enable_retraction:
        body[layer] += 'G92 E0 \n'
    '''
    if enable_retraction:
        body[layer] += 'G0 E%f \n' % (-retraction)
        body[layer] += 'G0 X%f Y%f F%f \n' % (v1[0], v1[1], velf)
        body[layer] += 'G0 E0 \n'
    else:
        body[layer] += 'G1 X%f Y%f F%f \n' % (v1[0], v1[1], vel1)

    body[layer] += 'G1 X%f Y%f E%f F%f \n' % (v2[0], v2[1], E, vel1)
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

        if enable_optimized_path:
            for k in range(1,iterations - layer):
                body[layer + k] += 'G0 X%f Y%f \n \n ' % (vert1[0],vert1[1])

        '''
        if(layer + 1 < iterations):
            body[layer + 1] += 'G0 X%f Y%f \n \n ' % (vert1[0],vert1[1])

        if(layer + 2 < iterations):
            body[layer + 2] += 'G0 X%f Y%f \n \n ' % (vert1[0],vert1[1])
        '''

draw(np.array(starting_point), np.array([starting_point[0]+dimension,starting_point[1]]), 0)

# create the skirt
sp_0 = np.array(np.array(starting_point))
sp_1 = sp_0 + np.array([dimension,0])
sp_2 = getNextVert(sp_0, sp_1)
sp_3 = getNextVert(sp_1, sp_2)
sp_4 = getNextVert(sp_2, sp_3)
center = (sp_0+sp_1+sp_2+sp_3+sp_4)/5
header.append('; skirt\n')

x0 = np.array([starting_point[0] - skirt_distance, starting_point[1] - skirt_distance])
header.append('G0 X%f Y%f Z%f \n' % (x0[0],x0[1],dz0))

for i in range(0,skirt_rounds):
    header.append('G92 E0 ; reset the extruder\n')
    versor = (x0 - center)
    norm = math.sqrt(sum(versor**2))#radius of the circle
    x_diam = 2*center - x0
    ex_quantity = kE*2*math.pi*norm
    header.append('G2 X%f Y%f I%f J%f E%f F%d \n' % (x_diam[0],x_diam[1],center[0] - x0[0],center[1] - x0[1],ex_quantity/2,vel1))
    x0 = x0 + versor*(skirt_spacing/norm)
    header.append('G2 X%f Y%f I%f J%f E%f F%d \n' % (x0[0],x0[1],center[0] - x_diam[0],center[1] - x_diam[1],ex_quantity,vel1))


# print the Gcode
file = open(filename+'.gcode', 'w')
for w in header:
    file.write(w)
j = 1
l = 0

for e in reversed(body):
    if layer_distribution == 'linear':
        for i in range(layer_repetitions):
            if enable_retraction:
                file.write('G92 E0 \n')
                file.write('G0 E%f \n' % (-retraction))
            file.write('\n G0 X%f  Y%f Z%f F%f ; layer%d\n' % (starting_point[0], starting_point[1], l*dz+dz0, velf, l))
            if enable_retraction:
                file.write('G0 E0 \n')
            file.write(e)
            l += 1
    elif layer_distribution == 'exponential':
        for i in range(layer_repetitions**j):
            if enable_retraction:
                file.write('G92 E0 \n')
                file.write('G0 E%f \n' % (-retraction))
            file.write('G0 X%f  Y%f Z%f F%f ; layer%d\n' % (starting_point[0], starting_point[1], l*dz+dz0, velf, l))
            if enable_retraction:
                file.write('G0 E0 \n')
            file.write(e)
            l += 1
    elif layer_distribution == 'quadratic':
        for i in range(layer_repetitions*j):
            if enable_retraction:
                file.write('G92 E0 \n')
                file.write('G0 E%f \n' % (-retraction))
            file.write('G0 X%f  Y%f Z%f F%f ; layer%d\n' % (starting_point[0], starting_point[1], l*dz+dz0, velf, l))
            if enable_retraction:
                file.write('G0 E0 \n')
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
