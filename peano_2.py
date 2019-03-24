import numpy as np
import math

# settings
dimension = 100 # length of the top line
lines_number = 2
layer_distribution = 'linear'
layer_repetitions = 8
filename = 'peano_curve'

# useful constants
mat1 =np.array([[0, -1],[1, 0]])

# ploting settings
starting_point = (10,10)
dz0=0.2 # altezza primo layer
dz=0.2 # altezza layer
layer_repetitions = 2
layers = 4
dx = 0.2 # space between two parallel lines

Tbed='15' # temperatura piano
Tex='210' # temperatura estrusore
v1='1200' # velocita' primo layer mm/min (20 mm/s)
v2='2400' # velocita' altri layer mm/min (40 mm/s)
vf='7800' # movimenti rapidi (130 mm/s)
kE = 2*dz*0.4/math.pi/1.75**2 # moltiplicatore per quantità da estrudere


header = []
body = []
footer = []
header.append(';peano curve Gcode\n')
header.append(';author: FedericoSold\n')


header.append('M140 S'+Tbed+' ; heat up bed\n') # inizia a scaldare il piano fino a Tbed
header.append('M104 T0 S'+Tex+'; het up extruder\n') # inizia a scaldare l'estrusore fino a Tex
header.append('G28 X0 Z0\n') #home X and Z axis
header.append('G21 ; use millimeters\n') #unita' di misura in millimetri
header.append('G90\n') #usa coordinate assolute ripsetto all'origine della macchina
header.append('G92 E0\n') # resetta la posizione dell'estrusore
header.append('M82\n') #usa coordinate assolute anche per l'estusore
header.append('M190 S'+Tbed+' ; wait bed temperature\n') # aspetta che la temperatura del piano sia raggiunta
header.append('M109 T0 S'+Tex+' ; wait extruder temperature\n') # aspetta che la temperatura dell'estrusore sia raggiunta
header.append('M106 S15 ; start fan\n') #accendi la ventola (0 ferma 255 massima)
# add the skirt
header.append('G0 X%f  Y%f Z%f ; skirt' % (starting_point[0]-5, starting_point[1]-5, dz0))
header.append('G2 X%F Y%f I%F J%f E%f'% (starting_point[0]-5, starting_point[1]-5, starting_point[0]+dimension/2, starting_point[1]+dimension/2, kE*math.pi*(dimension+10)*math.sqrt(2)))
header.append('G2 X%F Y%f I%F J%f E%f'% (starting_point[0]-4, starting_point[1]-4, starting_point[0]+dimension/2, starting_point[1]+dimension/2, kE*math.pi*(dimension+18)*math.sqrt(2)))

footer = []

footer.append('M104 S0 ; turn off the extruder\n') #spegni l'estusore
footer.append('M140 S0 ; turn off bed heat\n') # spegni il piano
footer.append('G28 X Y ; go home\n') #home X axis
footer.append('M84 ; stop idle hold\n') #sblocca i motori


body = ["" for x in range(layers)]#[';level '+str(l)+'\n' for l in range(layers) ]#np.empty((layers,),object)
for l in range(layers):
    body[l] += ';level '+str(l)+'\n'

def draw(start, end, layer):
    # the layer can be calculated from start and end
    if (layer<layers):
        # draw line
        body[layer] += 'G92 E0     ; Reset the extruder \n'
        body[layer] += 'G1 X%f Y%f \n' % (start[0], start[1])
        body[layer] += 'G1 X%f Y%f E%f \n' % (end[0], end[1], kE*dimension/3*(layers-1-layer))

        deltaP = (end-start)/3
        deltaO = np.matmul(deltaP,mat1)
        delP = dx*deltaP/math.sqrt(sum(deltaP**2))
        delO = dx*deltaO/math.sqrt(sum(deltaP**2))
        for j in range(lines_number):
            body[layer] += 'G92 E0     ; Reset the extruder \n'
            body[layer] += 'G1 X%f Y%f \n' % (start[0]+delP[0]+delO[0], start[1]+delP[1]+delO[1])
            body[layer] += 'G1 X%f Y%f E%f \n' % (end[0]-delP[0]+delO[0], end[1]-delP[1]+delO[1], kE*(dimension/3*(layers-1-layer)-math.sqrt(2)*dx))

            body[layer] += 'G92 E0     ; Reset the extruder \n'
            body[layer] += 'G1 X%f Y%f \n' % (start[0]+delP[0]-delO[0], start[1]+delP[1]-delO[1])
            body[layer] += 'G1 X%f Y%f E%f \n' % (end[0]-delP[0]-delO[0], end[1]-delP[1]-delO[1], kE*(dimension/3*(layers-1-layer)-math.sqrt(2)*dx))
        # make above lines
        draw(start,start+deltaP, layer+1)
        draw(start+deltaP, start+deltaP+deltaO, layer+1)
        draw(start+deltaP+deltaO, start+2*deltaP+deltaO, layer+1)
        draw(start+2*deltaP+deltaO, start+2*deltaP, layer+1)
        draw(start+2*deltaP, start+deltaP, layer+1)
        draw(start+deltaP, start+deltaP-deltaO, layer+1)
        draw(start+deltaP-deltaO, start+2*deltaP-deltaO, layer+1)
        draw(start+2*deltaP-deltaO, start+2*deltaP, layer+1)
        draw(start+2*deltaP, end, layer+1)
draw(np.array(starting_point), np.array([starting_point[0]+dimension,starting_point[1]+dimension]),0)
# print the Gcode
file = open(filename+'.gcode','w')
for w in header:
    file.write(w)
j = 1
l = 0
for e in reversed(body):
    if layer_distribution == 'linear':
        for i in range(layer_repetitions):
            file.write('G0 X%f  Y%f Z%f ; layer%d' % (starting_point[0], starting_point[1], l*dz+dz0, l))
            file.write(e)
            l += 1
    elif layer_distribution == 'exponential':
        for i in range(layer_repetitions**j):
            file.write('G0 X%f  Y%f Z%f ; layer%d' % (starting_point[0], starting_point[1], l*dz+dz0, l))
            file.write(e)
            l += 1
    else:
        file.write('G0 X%f  Y%f Z%f ; layer%d' % (starting_point[0], starting_point[1], l*dz+dz0, l))
        file.write(e)
        l += 1
    j += 1
for w in footer:
    file.write(w)
