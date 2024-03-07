# -*- coding: mbcs -*-sinθ
import math
import os
import sys
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'
"""
参数获取，注意在abaqus cae中第八位及以后是附加参数
如os.system("abaqus cae noGUI=test.py -- 16 8 1.7 30 PATH 1"),h,L,t,theta,pathe,gpu
"""
h = float(sys.argv[8]);
L = float(sys.argv[9]);
t = float(sys.argv[10]);
theta = math.radians(float(sys.argv[11]));
file_path, file_extension = os.path.splitext(sys.argv[12])
jobpath = file_path
use_GPU = int(sys.argv[13])


s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, -h/2), point2=(0.0, 0.0))#此处-8.0=-h/2
s.VerticalConstraint(entity=g[2], addUndoState=False)
s.Line(point1=(0.0, 0.0), point2=(-t/2, 0.0))#此处-0.85＝-t/2
s.HorizontalConstraint(entity=g[3], addUndoState=False)
s.PerpendicularConstraint(entity1=g[2], entity2=g[3], addUndoState=False)
s.Line(point1=(-t/2, 0.0), point2=(-L * math.cos(theta) - t/2, -L*math.sin(theta)))#此处-0.85=-t/2,-7.7782=-L*cosθ-t/2，-4=-L*sinθ
s.Line(point1=(-L * math.cos(theta) - t/2, -L*math.sin(theta)), point2=(-L*math.cos(theta)-t, -L*math.sin(theta)))#此处-7.7782=-L*cosθ-t/2，-4=-L*sinθ，-8.6282=-L*cosθ-t
s.HorizontalConstraint(entity=g[5], addUndoState=False)
s.Line(point1=(-L*math.cos(theta)-t, -L*math.sin(theta)), point2=(-L*math.cos(theta)-t, h/2-L*math.sin(theta)))#此处-8.6282=-L*cosθ-t，-4=-L*sinθ，4.0=h/2-L*sinθ
s.VerticalConstraint(entity=g[6], addUndoState=False)
s.PerpendicularConstraint(entity1=g[5], entity2=g[6], addUndoState=False)
s.unsetPrimaryObject()
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0, transform=(1.0, 0.0, 0.0, 0.0, 0.0, 1.0, -0.0, -1.0, -0.0, 
    0.0, -100.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
s1.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
s1.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
s1.rectangle(point1=(-t/2, -t/2), point2=(t/2, t/2))#此处0.85均为t/2
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseSolidSweep(sketch=s1, path=s)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
del mdb.models['Model-1'].sketches['__sweep__']
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=OFF)


a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-1-1', ), axisPoint=(0.0, h/2-L*math.sin(theta), 0.0), #此处4.0=h/2-L*sinθ
    axisDirection=(1.0, 0.0, 0.0), angle=180.0)
#: The instance Part-1-1 was rotated by 180. degrees about the axis defined by the point 0., 4., 0. and the vector 1., 0., 0.
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-2', part=p, dependent=OFF)

a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-2', instances=(a.instances['Part-1-1'], 
    a.instances['Part-1-2'], ), originalInstances=SUPPRESS, domain=GEOMETRY)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-1-1', 'Part-1-2', 'Part-2-1'), axisPoint=(0.0, 
    0.0, 0.0), axisDirection=(0.0, 1.0, 0.0), angle=180.0)
#: The instances were rotated by 180. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-2']
a.Instance(name='Part-2-2', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-A', instances=(a.instances['Part-2-1'], 
    a.instances['Part-2-2'], ), originalInstances=SUPPRESS, domain=GEOMETRY)


a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-1-1', 'Part-1-2', 'Part-2-1', 'Part-2-2', 
    'Part-A-1'), vector=(0.0, 0.0, -L*math.cos(theta)-t))#此处-8.6282=-L*cosθ-t
#: The instances were translated by 0., 0., -L*math.cos(theta)-t with respect to the assembly coordinate system
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-A']
a.Instance(name='Part-A-2', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-A-2', ), vector=(0.0, 0.0, L*math.cos(theta)+t))#此处8.6282=L*cosθ+t
#: The instance Part-A-2 was translated by 0., 0., 8.6282 with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-A']
a.Instance(name='Part-A-3', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-A-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=180.0)
#: The instance Part-A-3 was rotated by 180. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.

a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-A-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=90.0)
#: The instance Part-A-3 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.

a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-A-3', ), vector=(L*math.cos(theta)+t, 0.0, 0.0))#此处8.6282=L*cosθ+t
#: The instance Part-A-3 was translated by 8.6282, 0., 0. with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-A']
a.Instance(name='Part-A-4', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-A-4', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=90.0)
#: The instance Part-A-4 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-A-4', ), vector=(-L*math.cos(theta)-t, 0.0, 0.0))#此处-8.6282=-L*cosθ-t
#: The instance Part-A-4 was translated by -8.6282, 0., 0. with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-B', instances=(a.instances['Part-A-1'], 
    a.instances['Part-A-2'], a.instances['Part-A-3'], a.instances['Part-A-4'], 
    ), originalInstances=SUPPRESS, domain=GEOMETRY)

p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
a = mdb.models['Model-1'].rootAssembly

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-3', part=p, dependent=OFF)

a = mdb.models['Model-1'].rootAssembly
del a.features['Part-1-3']

p = mdb.models['Model-1'].parts['Part-1']

s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
#此处所有参数参考上方建模参数除了12.0=h-L*sinθ以及标记处8.0
s.Line(point1=(0.0, 0.0), point2=(-t/2, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
s.Line(point1=(-t/2, 0.0), point2=(-L * math.cos(theta) - t/2, -L*math.sin(theta)))
s.Line(point1=(-L * math.cos(theta) - t/2, -L*math.sin(theta)), point2=(-L*math.cos(theta)-t, -L*math.sin(theta)))
s.HorizontalConstraint(entity=g[4], addUndoState=False)
s.Line(point1=(-L*math.cos(theta)-t, -L*math.sin(theta)), point2=(-L*math.cos(theta)-t, h-L*math.sin(theta)))
s.VerticalConstraint(entity=g[5], addUndoState=False)
s.PerpendicularConstraint(entity1=g[4], entity2=g[5], addUndoState=False)
s.Line(point1=(-L*math.cos(theta)-t, h-L*math.sin(theta)), point2=(-L * math.cos(theta) - t/2, h-L*math.sin(theta)))
s.HorizontalConstraint(entity=g[6], addUndoState=False)
s.PerpendicularConstraint(entity1=g[5], entity2=g[6], addUndoState=False)
s.Line(point1=(-L * math.cos(theta) - t/2, h-L*math.sin(theta)), point2=(-t/2, h-2*L*math.sin(theta)))#此处8.0=h-2*L*sinθ
s.Line(point1=(-t/2, h-2*L*math.sin(theta)), point2=(0.0, h-2*L*math.sin(theta)))#此处8.0=h-2*L*sinθ
s.HorizontalConstraint(entity=g[8], addUndoState=False)
s.unsetPrimaryObject()
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0, transform=(0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 
    0.0, 0.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
s1.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
s1.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
s1.rectangle(point1=(-t/2, -t/2), point2=(t/2, t/2))
p = mdb.models['Model-1'].Part(name='Part-S', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-S']
p.BaseSolidSweep(sketch=s1, path=s)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-S']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
del mdb.models['Model-1'].sketches['__sweep__']

a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-S']
a1.Instance(name='Part-S-1', part=p, dependent=OFF)

a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('Part-S-1', ), vector=(L*math.cos(theta)+t, 0.0, 0.0))#此处8.6285=L*cosθ+t
#: The instance Part-S-1 was translated by 8.6285, 0., 0. with respect to the assembly coordinate system

a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-S']
a1.Instance(name='Part-S-2', part=p, dependent=OFF)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('Part-S-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=90.0)
#: The instance Part-S-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.

a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('Part-S-2', ), vector=(L*math.cos(theta)+t, 0.0, 0.0))#此处8.6285=L*cosθ+t
#: The instance Part-S-2 was translated by 8.6285, 0., 0. with respect to the assembly coordinate system

a1 = mdb.models['Model-1'].rootAssembly
a1.InstanceFromBooleanMerge(name='Part-S1', instances=(
    a1.instances['Part-S-1'], a1.instances['Part-S-2'], ), 
    originalInstances=SUPPRESS, domain=GEOMETRY)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('Part-S1-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=180.0)
#: The instance Part-S1-1 was rotated by 180. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-S1']
a1.Instance(name='Part-S1-2', part=p, dependent=ON)

a1 = mdb.models['Model-1'].rootAssembly
a1.InstanceFromBooleanMerge(name='Part-M', instances=(a1.instances['Part-B-1'], 
    a1.instances['Part-S1-1'], a1.instances['Part-S1-2'], ), 
    originalInstances=SUPPRESS, domain=GEOMETRY)

#阵列
a1 = mdb.models['Model-1'].rootAssembly
a1.LinearInstancePattern(instanceList=('Part-M-1', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1=6, number2=4, spacing1=2*l*math.cos(theta)+2*t, 
    spacing2=2*h-2*l*math.sin(theta))#此处17.26=2*L*cosθ+2*t，24.0=2*h-2*L*sinθ
a1 = mdb.models['Model-1'].rootAssembly
a1.LinearInstancePattern(instanceList=('Part-M-1', 'Part-M-1-lin-1-2', 
    'Part-M-1-lin-1-3', 'Part-M-1-lin-1-4', 
	'Part-M-1-lin-2-1', 'Part-M-1-lin-2-2', 
    'Part-M-1-lin-2-3', 'Part-M-1-lin-2-4',
	'Part-M-1-lin-3-1', 'Part-M-1-lin-3-2', 
    'Part-M-1-lin-3-3', 'Part-M-1-lin-3-4',
	'Part-M-1-lin-4-1', 'Part-M-1-lin-4-2', 
    'Part-M-1-lin-4-3', 'Part-M-1-lin-4-4',
	'Part-M-1-lin-5-1', 'Part-M-1-lin-5-2', 
    'Part-M-1-lin-5-3', 'Part-M-1-lin-5-4',
	'Part-M-1-lin-6-1', 'Part-M-1-lin-6-2', 
    'Part-M-1-lin-6-3', 'Part-M-1-lin-6-4',), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 
    0.0), number1=6, number2=1, spacing1=2*l*math.cos(theta)+2*t, spacing2=2*h-2*l*math.sin(theta))#此处参考上一条

#: (mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-2-1-1'], mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-1-2-lin-2-1'], mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-2-2-lin-2-1'], mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-2-1-lin-2-1'])
a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-MT', instances=(a.instances['Part-M-1'], 
    a.instances['Part-M-1-lin-1-2'], a.instances['Part-M-1-lin-1-3'], 
    a.instances['Part-M-1-lin-1-4'], a.instances['Part-M-1-lin-2-1'], 
    a.instances['Part-M-1-lin-2-2'], a.instances['Part-M-1-lin-2-3'], 
    a.instances['Part-M-1-lin-2-4'], a.instances['Part-M-1-lin-3-1'], 
    a.instances['Part-M-1-lin-3-2'], a.instances['Part-M-1-lin-3-3'], 
    a.instances['Part-M-1-lin-3-4'], a.instances['Part-M-1-lin-4-1'], 
    a.instances['Part-M-1-lin-4-2'], a.instances['Part-M-1-lin-4-3'], 
    a.instances['Part-M-1-lin-4-4'], a.instances['Part-M-1-lin-5-1'], 
    a.instances['Part-M-1-lin-5-2'], a.instances['Part-M-1-lin-5-3'], 
    a.instances['Part-M-1-lin-5-4'], a.instances['Part-M-1-lin-6-1'], 
    a.instances['Part-M-1-lin-6-2'], a.instances['Part-M-1-lin-6-3'], 
    a.instances['Part-M-1-lin-6-4'], a.instances['Part-M-1-lin-2-1-1'], 
    a.instances['Part-M-1-lin-3-1-1'], a.instances['Part-M-1-lin-4-1-1'], 
    a.instances['Part-M-1-lin-5-1-1'], a.instances['Part-M-1-lin-6-1-1'], 
    a.instances['Part-M-1-lin-1-2-lin-2-1'], 
    a.instances['Part-M-1-lin-1-2-lin-3-1'], 
    a.instances['Part-M-1-lin-1-2-lin-4-1'], 
    a.instances['Part-M-1-lin-1-2-lin-5-1'], 
    a.instances['Part-M-1-lin-1-2-lin-6-1'], 
    a.instances['Part-M-1-lin-1-4-lin-2-1'], 
    a.instances['Part-M-1-lin-1-4-lin-3-1'], 
    a.instances['Part-M-1-lin-1-4-lin-4-1'], 
    a.instances['Part-M-1-lin-1-4-lin-5-1'], 
    a.instances['Part-M-1-lin-1-4-lin-6-1'], 
    a.instances['Part-M-1-lin-2-2-lin-2-1'], 
    a.instances['Part-M-1-lin-2-2-lin-3-1'], 
    a.instances['Part-M-1-lin-2-2-lin-4-1'], 
    a.instances['Part-M-1-lin-2-2-lin-5-1'], 
    a.instances['Part-M-1-lin-2-2-lin-6-1'], 
    a.instances['Part-M-1-lin-2-4-lin-2-1'], 
    a.instances['Part-M-1-lin-2-4-lin-3-1'], 
    a.instances['Part-M-1-lin-2-4-lin-4-1'], 
    a.instances['Part-M-1-lin-2-4-lin-5-1'], 
    a.instances['Part-M-1-lin-2-4-lin-6-1'], 
    a.instances['Part-M-1-lin-3-2-lin-2-1'], 
    a.instances['Part-M-1-lin-3-2-lin-3-1'], 
    a.instances['Part-M-1-lin-3-2-lin-4-1'], 
    a.instances['Part-M-1-lin-3-2-lin-5-1'], 
    a.instances['Part-M-1-lin-3-2-lin-6-1'], 
    a.instances['Part-M-1-lin-4-2-lin-2-1'], 
    a.instances['Part-M-1-lin-4-2-lin-3-1'], 
    a.instances['Part-M-1-lin-4-2-lin-4-1'], 
    a.instances['Part-M-1-lin-4-2-lin-5-1'], 
    a.instances['Part-M-1-lin-4-2-lin-6-1'], 
    a.instances['Part-M-1-lin-4-4-lin-2-1'], 
    a.instances['Part-M-1-lin-4-4-lin-3-1'], 
    a.instances['Part-M-1-lin-4-4-lin-4-1'], 
    a.instances['Part-M-1-lin-4-4-lin-5-1'], 
    a.instances['Part-M-1-lin-4-4-lin-6-1'], 
    a.instances['Part-M-1-lin-6-2-lin-2-1'], 
    a.instances['Part-M-1-lin-6-2-lin-3-1'], 
    a.instances['Part-M-1-lin-6-2-lin-4-1'], 
    a.instances['Part-M-1-lin-6-2-lin-5-1'], 
    a.instances['Part-M-1-lin-6-2-lin-6-1'], 
    a.instances['Part-M-1-lin-6-4-lin-2-1'], 
    a.instances['Part-M-1-lin-6-4-lin-3-1'], 
    a.instances['Part-M-1-lin-6-4-lin-4-1'], 
    a.instances['Part-M-1-lin-6-4-lin-5-1'], 
    a.instances['Part-M-1-lin-6-4-lin-6-1'], 
    a.instances['Part-M-1-lin-3-4-lin-2-1'], 
    a.instances['Part-M-1-lin-3-4-lin-3-1'], 
    a.instances['Part-M-1-lin-3-4-lin-4-1'], 
    a.instances['Part-M-1-lin-3-4-lin-5-1'], 
    a.instances['Part-M-1-lin-3-4-lin-6-1'], 
    a.instances['Part-M-1-lin-5-2-lin-2-1'], 
    a.instances['Part-M-1-lin-5-2-lin-3-1'], 
    a.instances['Part-M-1-lin-5-2-lin-4-1'], 
    a.instances['Part-M-1-lin-5-2-lin-5-1'], 
    a.instances['Part-M-1-lin-5-2-lin-6-1'], 
    a.instances['Part-M-1-lin-5-4-lin-2-1'], 
    a.instances['Part-M-1-lin-5-4-lin-3-1'], 
    a.instances['Part-M-1-lin-5-4-lin-4-1'], 
    a.instances['Part-M-1-lin-5-4-lin-5-1'], 
    a.instances['Part-M-1-lin-5-4-lin-6-1'], 
    a.instances['Part-M-1-lin-1-3-lin-2-1'], 
    a.instances['Part-M-1-lin-1-3-lin-3-1'], 
    a.instances['Part-M-1-lin-1-3-lin-4-1'], 
    a.instances['Part-M-1-lin-1-3-lin-5-1'], 
    a.instances['Part-M-1-lin-1-3-lin-6-1'], 
    a.instances['Part-M-1-lin-2-1-lin-2-1'], 
    a.instances['Part-M-1-lin-2-1-lin-3-1'], 
    a.instances['Part-M-1-lin-2-1-lin-4-1'], 
    a.instances['Part-M-1-lin-2-1-lin-5-1'], 
    a.instances['Part-M-1-lin-2-1-lin-6-1'], 
    a.instances['Part-M-1-lin-2-3-lin-2-1'], 
    a.instances['Part-M-1-lin-2-3-lin-3-1'], 
    a.instances['Part-M-1-lin-2-3-lin-4-1'], 
    a.instances['Part-M-1-lin-2-3-lin-5-1'], 
    a.instances['Part-M-1-lin-2-3-lin-6-1'], 
    a.instances['Part-M-1-lin-3-1-lin-2-1'], 
    a.instances['Part-M-1-lin-3-1-lin-3-1'], 
    a.instances['Part-M-1-lin-3-1-lin-4-1'], 
    a.instances['Part-M-1-lin-3-1-lin-5-1'], 
    a.instances['Part-M-1-lin-3-1-lin-6-1'], 
    a.instances['Part-M-1-lin-4-1-lin-2-1'], 
    a.instances['Part-M-1-lin-4-1-lin-3-1'], 
    a.instances['Part-M-1-lin-4-1-lin-4-1'], 
    a.instances['Part-M-1-lin-4-1-lin-5-1'], 
    a.instances['Part-M-1-lin-4-1-lin-6-1'], 
    a.instances['Part-M-1-lin-4-3-lin-2-1'], 
    a.instances['Part-M-1-lin-4-3-lin-3-1'], 
    a.instances['Part-M-1-lin-4-3-lin-4-1'], 
    a.instances['Part-M-1-lin-4-3-lin-5-1'], 
    a.instances['Part-M-1-lin-4-3-lin-6-1'], 
    a.instances['Part-M-1-lin-6-1-lin-2-1'], 
    a.instances['Part-M-1-lin-6-1-lin-3-1'], 
    a.instances['Part-M-1-lin-6-1-lin-4-1'], 
    a.instances['Part-M-1-lin-6-1-lin-5-1'], 
    a.instances['Part-M-1-lin-6-1-lin-6-1'], 
    a.instances['Part-M-1-lin-6-3-lin-2-1'], 
    a.instances['Part-M-1-lin-6-3-lin-3-1'], 
    a.instances['Part-M-1-lin-6-3-lin-4-1'], 
    a.instances['Part-M-1-lin-6-3-lin-5-1'], 
    a.instances['Part-M-1-lin-6-3-lin-6-1'], 
    a.instances['Part-M-1-lin-3-3-lin-2-1'], 
    a.instances['Part-M-1-lin-3-3-lin-3-1'], 
    a.instances['Part-M-1-lin-3-3-lin-4-1'], 
    a.instances['Part-M-1-lin-3-3-lin-5-1'], 
    a.instances['Part-M-1-lin-3-3-lin-6-1'], 
    a.instances['Part-M-1-lin-5-1-lin-2-1'], 
    a.instances['Part-M-1-lin-5-1-lin-3-1'], 
    a.instances['Part-M-1-lin-5-1-lin-4-1'], 
    a.instances['Part-M-1-lin-5-1-lin-5-1'], 
    a.instances['Part-M-1-lin-5-1-lin-6-1'], 
    a.instances['Part-M-1-lin-5-3-lin-2-1'], 
    a.instances['Part-M-1-lin-5-3-lin-3-1'], 
    a.instances['Part-M-1-lin-5-3-lin-4-1'], 
    a.instances['Part-M-1-lin-5-3-lin-5-1'], 
    a.instances['Part-M-1-lin-5-3-lin-6-1'], ), originalInstances=SUPPRESS, 
    domain=GEOMETRY)
#加载面
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=(12*(l*math.cos(theta)+t)+t, 12*(l*math.cos(theta)+t)+t))#36.22=4*(L*cosθ+t)+t

p = mdb.models['Model-1'].Part(name='Part-P', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-P']
p.BaseSolidExtrude(sketch=s, depth=t)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-P']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-P']
a.Instance(name='Part-P-1', part=p, dependent=OFF)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-P-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
#: The instance Part-P-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 1., 0., 0.
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-P-1', ), vector=(-(l*math.cos(theta)+3.0/2*t), -h/2, -(l*math.cos(theta)+3.0/2*t)))#此处#9.48=L*cosθ+t+t/2，#-8.0=h/2
#: The instance Part-P-1 was translated by -9.48, -8., -9.48 with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-P']
a.Instance(name='Part-P-2', part=p, dependent=OFF)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-P-2', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
#: The instance Part-P-2 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 1., 0., 0.
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-P-2', ), vector=(-(l*math.cos(theta)+3.0/2*t), 8*h-8*l*math.sin(theta)-h/2, -(l*math.cos(theta)+3.0/2*t)))#此处#9.48=L*cosθ+t+t/2，#40.0=4*h-4*L*sinθ-h/2
#: The instance Part-P-2 was translated by -9.48, 40., -9.48 with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-ME', instances=(a.instances['Part-MT-1'], 
    a.instances['Part-P-1'], a.instances['Part-P-2'], ), 
    originalInstances=SUPPRESS, domain=GEOMETRY)


#材料属性
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((31.4891, 0.48), ))
mdb.models['Model-1'].materials['Material-1'].Plastic(table=((0.64773, 0.0), (
    0.713450292, 0.00122763932041564), (0.74435241042, 0.00160222579439244), (
    0.769668732566, 0.00190130243577563), (0.792799660682, 
    0.00220893481767079), (0.816953393855, 0.00260329737531577), (
    0.842902507842, 0.00308791127921607), (0.869747041863, 
    0.00361503348687634), (0.896566056284, 0.00413664520770165), (
    0.922905057481, 0.0046335228437098), (0.948919625346, 0.00512410457115265), 
    (0.974806531513, 0.00562937146317935), (1.00075421697, 0.0061692289289364), 
    (1.02682237457, 0.00674695826245644), (1.0529694486, 0.00735276741167671), 
    (1.0791511523, 0.00797651169295054), (1.10532331238, 0.00860808028796209), 
    (1.13145944295, 0.00924264168156793), (1.15756977634, 0.0098863239531526), 
    (1.18366911381, 0.0105466189009961), (1.2097717154, 0.0112316763541133), (
    1.23588104128, 0.0119627778485139), (1.26199059454, 0.0127733117525031), (
    1.28809350605, 0.0136971190634845), (1.31418427999, 0.0147599382315273), (
    1.34026386009, 0.0159495151869786), (1.3663350759, 0.0172424694356604), (
    1.39240149703, 0.0186023430185942), (1.41846938072, 0.0199451770389797), (
    1.44454559064, 0.021176281017207), (1.47063375188, 0.0222464304102178), (
    1.49672830499, 0.0232353412116808), (1.52282207353, 0.0242454302432496), (
    1.54890787753, 0.0253757718206798), (1.57497850672, 0.0266967346495651), (
    1.60102673542, 0.0282640693752746), (1.62704682646, 0.0301191685938348), (
    1.65305424529, 0.03210057840073), (1.67908024771, 0.0338957778717732), (
    1.70515123723, 0.0352393502264512), (1.73123787469, 0.036406444110175), (
    1.75727711637, 0.0379990588584645), (1.78322717296, 0.0404205775171019), (
    1.80913347653, 0.0432586615929003), (1.8350573731, 0.0459505205423338), (
    1.8610069997, 0.0484165615646725), (1.88696259162, 0.0508305782562205), (
    1.91291173442, 0.0533026475006058), (1.93886148205, 0.0557738199643922), (
    1.9648169355, 0.0581990743863349), (1.99076369141, 0.0606909799512353), (
    2.01668266765, 0.0633991232066904), (2.04255653864, 0.0664313819055027), (
    2.06837015513, 0.0698439766697178), (2.09412332613, 0.073610192595609), (
    2.11986792954, 0.077423260019633), (2.14565462351, 0.0809897602928726), (
    2.17148338644, 0.0843160674252793), (2.19732610787, 0.0875656593603128), (
    2.22310517854, 0.0911657129768481), (2.2487739093, 0.0953753636711875), (
    2.27443297955, 0.0996566723675428), (2.30014247006, 0.103671995678658), (
    2.32575114318, 0.108173609150713), (2.35128687657, 0.113040788668283), (
    2.37696883844, 0.117206624394988), (2.40272242286, 0.121005004222892), (
    2.42828679742, 0.125659634693233), (2.45362365759, 0.131368960339763), (
    2.47898179852, 0.137006860458758), (2.50441583242, 0.142306171760135), (
    2.52973443334, 0.148088222771045), (2.55485766547, 0.15458904194066), (
    2.57985893428, 0.161374117291951), (2.60500560338, 0.168067464718225), (
    2.63013337538, 0.175061293719095), (2.6542568009, 0.183862443743903), (
    2.6773323174, 0.195246137312133), (2.70071706689, 0.207948801643905), (
    2.719298246, 0.224755449357587)))
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-1', thickness=None)
p = mdb.models['Model-1'].parts['Part-ME']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(cells=cells)
p = mdb.models['Model-1'].parts['Part-ME']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
a1 = mdb.models['Model-1'].rootAssembly
a1.regenerate()

#网格划分
p = mdb.models['Model-1'].parts['Part-ME']
p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-ME']
c = p.cells
pickedRegions = c.getSequenceFromMask(mask=('[#1 ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
p = mdb.models['Model-1'].parts['Part-ME']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
pickedRegions =(cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
    elemType3))
p = mdb.models['Model-1'].parts['Part-ME']
p.generateMesh()

#分析步设置
a = mdb.models['Model-1'].rootAssembly
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial', 
    maxNumInc=1000, initialInc=0.1, maxInc=0.2, nlgeom=ON)
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
    'S', 'MISES', 'E', 'U', 'RF', 'ENER', 'ELEN', 'ELEDEN', 'DAMAGEC', 'IVOL'))

#加入必要集合
a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-ME-1'].faces
faces1 = f1.findAt(((0,8*h-8*l*math.sin(theta)-h/2,0),))
a.Set(faces=faces1, name='Set-up')

a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-ME-1'].faces
faces1 = f1.findAt(((0,-h/2-t,0),))
a.Set(faces=faces1, name='Set-down')

#边界条件设置
a = mdb.models['Model-1'].rootAssembly
region = a.sets['Set-down']
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', 
    region=region, u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)
a = mdb.models['Model-1'].rootAssembly
region = a.sets['Set-up']
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', 
    region=region, u1=UNSET, u2=-40.0, u3=UNSET, ur1=UNSET, ur2=UNSET, 
    ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, 
    fieldName='', localCsys=None)


#设置job任务
if use_GPU:
    mdb.Job(name=jobpath, model='Model-1', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=40, 
        numDomains=40, numGPUs=3)
else:
    mdb.Job(name=jobpath, model='Model-1', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=40, 
        numDomains=40, numGPUs=0)
#保存以及提交任务
mdb.jobs[jobpath].submit(consistencyChecking=OFF)



