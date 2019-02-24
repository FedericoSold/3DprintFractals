import numpy as np
import math

# settings
dimension = 100 # lenght of the top line
lines_number = 2

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


body = ["" for x in range(layers)]#[';level '+str(l)+'\n' for l in range(layers) ]#np.empty((layers,),object)
for l in range(layers):
    body[l] += ';level '+str(l)+'\n'
    body[l] += 'G0 X%f  Y%f Z%f \n' % (starting_point[0], starting_point[1], l*dz+dz0)

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
draw(np.array(starting_point), np.array([starting_point[0]+10,starting_point[1]+10]),0)
for w in header:
    print(w)
for e in reversed(body):
    for i in range(layer_repetitions):
        print(e)
for w in footer:
    print(w)
