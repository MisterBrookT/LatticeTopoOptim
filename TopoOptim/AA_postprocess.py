from abaqus import *
from odbAccess import *
from abaqusConstants import *
import math

h = float(sys.argv[8]);
L = float(sys.argv[9]);
t = float(sys.argv[10]);
theta = math.radians(float(sys.argv[11]));
path = sys.argv[12]

o1 = session.openOdb(name=path)
odb = o1
mdb = odb.rootAssembly
step = odb.steps['Step-1']
frame=odb.steps['Step-1'].frames
element_nummber=frame[1].fieldOutputs['S'].values
stress =0.0
strain=0.0
evol=0.0
evolfcc=0.0
val_e=0.0
val_s=0.0
strian_stress=[]

volumefcc = frame[1].fieldOutputs['IVOL'].values

for k in range(len(volumefcc)):
	val_vfcc = volumefcc[k]
	evolfcc = evolfcc + val_vfcc.data

for i in range(len(frame)):
	stress = frame[i].fieldOutputs['RF'].values[0].data[1]
	strain = frame[i].frameValue
	ave_e=abs(strain*27.77/(8*h-8*l*math.sin(theta)))
	ave_s=abs(stress/((12*(l*math.cos(theta)+t)+t)*(12*(l*math.cos(theta)+t)+t)))
	strian_stress.append((ave_e,ave_s))

strian_stress=tuple(strian_stress)
energy=0

for i in range(len(strian_stress)-1):
	yy=(strian_stress[i+1])[1]+(strian_stress[i])[1]
	xx=(strian_stress[i+1])[0]-(strian_stress[i])[0]
	AA=yy*xx/2
	energy=energy+AA

SEA=energy/evolfcc*(12*(l*math.cos(theta)+t)+t)*(12*(l*math.cos(theta)+t)+t)*(8*h-8*l*math.sin(theta))/0.0237

with open('output.txt', 'a') as f:
    f.write('SEA:{}\n'.format(SEA))

