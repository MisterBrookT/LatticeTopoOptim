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
    0.0), direction2=(0.0, 1.0, 0.0), number1=6, number2=4, spacing1=2*L*math.cos(theta)+2*t, 
    spacing2=2*h-2*L*math.sin(theta))#此处17.26=2*L*cosθ+2*t，24.0=2*h-2*L*sinθ
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
    0.0), number1=6, number2=1, spacing1=2*L*math.cos(theta)+2*t, spacing2=2*h-2*L*math.sin(theta))#此处参考上一条

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
s.rectangle(point1=(0.0, 0.0), point2=(12*(L*math.cos(theta)+t)+t, 12*(L*math.cos(theta)+t)+t))#36.22=4*(L*cosθ+t)+t

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
a.translate(instanceList=('Part-P-1', ), vector=(-(L*math.cos(theta)+3.0/2*t), -h/2, -(L*math.cos(theta)+3.0/2*t)))#此处#9.48=L*cosθ+t+t/2，#-8.0=h/2
#: The instance Part-P-1 was translated by -9.48, -8., -9.48 with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-P']
a.Instance(name='Part-P-2', part=p, dependent=OFF)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-P-2', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
#: The instance Part-P-2 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 1., 0., 0.
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-P-2', ), vector=(-(L*math.cos(theta)+3.0/2*t), 8*h-8*L*math.sin(theta)-h/2, -(L*math.cos(theta)+3.0/2*t)))#此处#9.48=L*cosθ+t+t/2，#40.0=4*h-4*L*sinθ-h/2
#: The instance Part-P-2 was translated by -9.48, 40., -9.48 with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-ME', instances=(a.instances['Part-MT-1'], 
    a.instances['Part-P-1'], a.instances['Part-P-2'], ), 
    originalInstances=SUPPRESS, domain=GEOMETRY)


#材料属性
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((1000, 0.48), ))
mdb.models['Model-1'].materials['Material-1'].Plastic(table=((
    30.84428571, 0.0), (33.97382343, 0.001227639), (35.44535288, 0.001602226),
    (36.65089203, 0.001901302), (37.75236479, 0.002208935), (38.90254256,
    0.002603297), (40.13821466, 0.003087911), (41.4165258, 0.003615033), (
    42.69362173, 0.004136645), (43.94785988, 0.004633523), (45.18664883,
    0.005124105), (46.41935864, 0.005629371), (47.65496271, 0.006169229), (
    48.89630355, 0.006746958), (50.14140231, 0.007352767), (51.38815011,
    0.007976512), (52.63444345, 0.00860808), (53.87902109, 0.009242642), (
    55.1223703, 0.009886324), (56.3651959, 0.010546619), (57.60817692,
    0.011231676), (58.85147816, 0.011962778), (60.09479022, 0.012773312), (
    61.337786, 0.013697119), (69.16759368, 0.014759938), (70.54020316,
    0.015949515), (71.91237242, 0.017242469), (73.28428932, 0.018602343), (
    74.6562832, 0.019945177), (76.0287153, 0.021176281), (77.40177641,
    0.02224643), (78.77517395, 0.023235341), (80.14853019, 0.02424543), (
    81.52146724, 0.025375772), (82.89360562, 0.026696735), (84.26456502,
    0.028264069), (85.6340435, 0.030119169), (87.00285502, 0.032100578), (
    88.37264462, 0.033895778), (89.74480196, 0.03523935), (91.11778288,
    0.036406444), (92.48826928, 0.037999059), (93.85406173, 0.040420578), (
    95.2175514, 0.043258662), (96.58196701, 0.045950521), (97.94773683,
    0.048416562), (99.31382061, 0.050830578), (100.679565, 0.053302648), (
    102.0453412, 0.05577382), (103.4114177, 0.058199074), (104.7770364,
    0.06069098), (106.141193, 0.063399123), (107.5029757, 0.066431382), (
    108.8615871, 0.069843977), (110.2170172, 0.073610193), (111.5719963,
    0.07742326), (112.9291907, 0.08098976), (114.2885993, 0.084316067), (
    115.6487425, 0.087565659), (117.0055357, 0.091165713), (118.3565215,
    0.095375364), (119.7069989, 0.099656672), (121.06013, 0.103671996), (
    122.4079549, 0.108173609), (123.7519409, 0.113040789), (125.1036231,
    0.117206624), (126.4590749, 0.121005004), (127.8045683, 0.125659635), (
    129.1380872, 0.13136896), (130.4727262, 0.13700686), (131.8113596,
    0.142306172), (133.1439175, 0.148088223), (134.4661929, 0.154589042), (
    135.7820492, 0.161374117), (137.1055581, 0.168067465), (138.4280724,
    0.175061294), (139.6977264, 0.183862444), (140.9122272, 0.195246137), (
    142.1430035, 0.207948802), (143.1209603, 0.224755449), (160.0,
    0.241555449), (180.0, 0.258355449), (200.0, 0.275155449)))
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

#创建点间耦合
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(5*L*math.cos(theta)+5*t, 8*h-8*L*math.sin(theta)-h/2, 5*L*math.cos(theta)+5*t))
RF_ID = a.features['RP-1'].id
r1 = a.referencePoints
refPoints1=(r1[RF_ID], )
region1=a.Set(referencePoints=refPoints1, name='Set-node')
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['Part-ME-1'].faces
side1Faces1 = s1.findAt(((5*L*math.cos(theta)+5*t, 8*h-8*L*math.sin(theta)-h/2, 5*L*math.cos(theta)+5*t),))
region2=a.Surface(side1Faces=side1Faces1, name='Surf-up')

#分析步设置
a = mdb.models['Model-1'].rootAssembly
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial',
    maxNumInc=1000, initialInc=0.1, maxInc=0.2, nlgeom=ON)
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
    'S', 'E', 'IVOL'))
regionDef=mdb.models['Model-1'].rootAssembly.sets['Set-node']
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
    createStepName='Step-1', variables=('U', 'RF'), region=regionDef,
    sectionPoints=DEFAULT, rebar=EXCLUDE)




#加入必要集合
a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-ME-1'].faces
faces1 = f1.findAt(((0,8*h-8*L*math.sin(theta)-h/2,0),))
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
mdb.models['Model-1'].Coupling(name='Constraint-1', controlPoint=region1,
    surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
    localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
a = mdb.models['Model-1'].rootAssembly
region = a.sets['Set-node']
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
    region=region, u1=0.0, u2=27.77, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET,
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='',
    localCsys=None)


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



