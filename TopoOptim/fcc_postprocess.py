# -*- coding: utf-8 -*-

from abaqus import *
from odbAccess import *
from abaqusConstants import *
from multiprocessing import Pool
# import visualization
# import xyPlot
import numpy as np
# from matplotlib import pyplot as plt
import sys
path = sys.argv[8]

# with Pool() as pool:
    # pass

# try:
o1 = session.openOdb(name=path)

print('Successfully open the odb file\n')

odb = o1
mdb = odb.rootAssembly
step = odb.steps['Step-1']
frame=odb.steps['Step-1'].frames



sum_sv=0
evol=0
evolfcc=0
val_e=0.0


print('len of frame: {}\n'.format(len(frame)))

total = len(frame)
evolfcc_total = 0
evol_total = 0
sum_sv_total = 0
strian_stress=[]

volumefcc_all = [f.fieldOutputs['IVOL'].values for f in frame]
stress_all = [f.fieldOutputs['S'].getSubset(region=mdb.elementSets['SET-FCC']).values for f in frame]
strain_all = [f.fieldOutputs['U'].values for f in frame]
volume_all = [f.fieldOutputs['IVOL'].getSubset(region=mdb.elementSets['SET-FCC']).values for f in frame]

print('Finish reading data. Start for-loop\n')

def process_frame(i):
    # pass
# for i in range(len(frame)): 
    print('Start: {}/{}\n'.format(i+1,total))

    volumefcc= volumefcc_all[i]
    stress =  stress_all[i]
    # strain = frame[i].fieldOutputs['U'].values
    strain = strain_all[i][0].data[2]
    volume = volume_all[i]
    print(type(volumefcc))
    

    evolfcc = sum([val.data for val in volumefcc])
    evol = sum([val.data for val in volume])
    sum_sv = sum([s.data[2] * v.data for s, v in zip(stress, volume)])

    # for j in range(len(stress)):
    #     val_s=stress[j].data[2]
    #     val_e=strain[0].data[2]
    #     val_v=volume[j]
    #     sv=val_s*val_v.data
    #     ev=val_e

    #     evol=evol+val_v.data
    #     sum_sv=sum_sv+sv
    ave_s= sum_sv/evol/evolfcc
    ave_e= strain

    return ave_e, ave_s
    # strian_stress.append((ave_e,ave_s))

pool = Pool()  # 直接创建 Pool 对象
results = pool.map(process_frame, range(total))
pool.close() 
pool.join() 

strian_stress=list(results)
print(strian_stress)
x_test = max(strian_stress, key=lambda x: x[1])[0]
max_ave_s = max(strian_stress, key=lambda x: x[1])[1]

with open('output.txt', 'a') as f:
    f.write('Max Ave E: {}\n'.format(x_test))
    f.write('Max Ave S: {}\n'.format(max_ave_s))