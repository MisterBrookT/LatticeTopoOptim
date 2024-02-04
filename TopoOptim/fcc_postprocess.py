from abaqus import *
from odbAccess import *
from abaqusConstants import *
import visualization
import xyPlot
import numpy as np
from matplotlib import pyplot as plt
import sys
path = sys.argv[8]
o1 = session.openOdb(name=path)
odb = o1
mdb = odb.rootAssembly
step = odb.steps['Step-1']
frame=odb.steps['Step-1'].frames
element_nummber=frame[1].fieldOutputs['S'].values
STRESS=0
STRAIN=0
sum_sv=0
sum_ev=0
evol=0
evolfcc=0
val_e=0.0
val_ss=0
strian_stress=[]
for i in range(len(frame)):
        volumefcc=frame[i].fieldOutputs['IVOL'].values
        stress = frame[i].fieldOutputs['S'].getSubset(region = mdb.elementSets['SET-FCC']).values
        strain = frame[i].fieldOutputs['U'].values
        volume = frame[i].fieldOutputs['IVOL'].getSubset(region = mdb.elementSets['SET-FCC']).values
        for k in range(len(volumefcc)):
            val_vfcc = volumefcc[k]
            evolfcc = evolfcc + val_vfcc.data
        for j in range(len(stress)):
            val_s=stress[j].data[2]
            val_e=strain[0].data[2]
            val_v=volume[j]
            sv=val_s*val_v.data
            ev=val_e
 
            evol=evol+val_v.data
            sum_sv=sum_sv+sv

        ave_s= sum_sv/evol/evolfcc
        ave_e= ev
       
        strian_stress.append((ave_e,ave_s))
strian_stress=tuple(strian_stress)
x_test = max(strian_stress, key=lambda x: x[1])[0]
max_ave_s = max(strian_stress, key=lambda x: x[1])[1]

with open('output.txt', 'w') as f:
    f.write('Max Ave E: {}\n'.format(x_test))
    f.write('Max Ave S: {}\n'.format(max_ave_s))