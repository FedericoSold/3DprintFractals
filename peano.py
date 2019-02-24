import numpy as np
import math


mat1 =np.array([[0, -1],[1, 0]])

#variabili
starting_point = (10,10)
z0=0.2 # altezza primo layer
dz=0.2 # altezza layer
nl=6 # numero di layer
layer_repetitions = 2
layers = 5


Tbed='15' # temperatura piano
Tex='210' # temperatura estrusore
v1='1200' # velocita' primo layer mm/min (20 mm/s)
v2='2400' # velocita' altri layer mm/min (40 mm/s)
vf='7800' # movimenti rapidi (130 mm/s)
kE = 2*dz*0.4/math.pi/1.75**2 # moltiplicatore per quantità da estrudere


dimension = 100
thickness = 1

start = []
start.append(';peano curve Gcode')
start.append(';author: Federico')


start.append('M140 S'+Tbed) # inizia a scaldare il piano fino a Tbed
start.append('M104 T0 S'+Tex) # inizia a scaldare l'estrusore fino a Tex
start.append('G21 ; use millimeters') #unita' di misura in millimetri
start.append('G90') #usa coordinate assolute ripsetto all'origine della macchina
start.append('G92 E0') # resetta la posizione dell'estrusore
start.append('M82') #usa coordinate assolute anche per l'estusore
start.append('M190 S'+Tbed+' ;bed temperature') # aspetta che la temperatura del piano sia raggiunta
start.append('M109 T0 S'+Tex+' ; extruder temperature') # aspetta che la temperatura dell'estrusore sia raggiunta
start.append('M106 S15 ; fan') #accendi la ventola (0 ferma 255 massima)

end = []

end.append('M104 S0') #spegni l'estusore
end.append('M140 S0') # spegni il piano
end.append('G28 X0') #home X axis
end.append('M84') #sblocca i motori


gcode = ["" for x in range(layers)]
for l in range(layers):
    gcode[l] += ';level '+str(l)+'\n'
    gcode[l] += 'G0 X%f  Y%f Z%f \n' % (starting_point[0], starting_point[1], (layers-l)*dz+z0)

def draw(start, end, layer):
    # the layer can be calculated from start and end
    if (layer<layers):
        # draw line
        gcode[layer] += 'G92 E0     ; Reset the extruder \n'
        gcode[layer] += 'G1 X%f Y%f E%f \n' % (end[0], end[1], kE*dimension/3*(layers-1-layer))
        # make above lines
        delta = (end-start)/3
        draw(start,start+delta, layer+1)
        draw(start+delta, start+delta+np.matmul(delta,mat1), layer+1)
        draw(start+delta+np.matmul(delta,mat1), start+2*delta+np.matmul(delta,mat1), layer+1)
        draw(start+2*delta+np.matmul(delta,mat1), start+2*delta, layer+1)
        draw(start+2*delta, start+delta, layer+1)
        draw(start+delta, start+delta-np.matmul(delta,mat1), layer+1)
        draw(start+delta-np.matmul(delta,mat1), start+2*delta-np.matmul(delta,mat1), layer+1)
        draw(start+2*delta-np.matmul(delta,mat1), start+2*delta, layer+1)
        draw(start+2*delta, end, layer+1)
draw(np.array(starting_point), np.array([starting_point[0]+10,starting_point[1]+10]),0)
for w in start:
    print(w)
for e in reversed(gcode):
    for i in range(layer_repetitions):
        print(e)
for w in end:
    print(w)
