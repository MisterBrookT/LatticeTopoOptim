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
    0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=2, spacing1=2*L*math.cos(theta)+2*t, 
    spacing2=2*h-2*L*math.sin(theta))#此处17.26=2*L*cosθ+2*t，24.0=2*h-2*L*sinθ
a1 = mdb.models['Model-1'].rootAssembly
a1.LinearInstancePattern(instanceList=('Part-M-1', 'Part-M-1-lin-1-2', 
    'Part-M-1-lin-2-1', 'Part-M-1-lin-2-2'), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 
    0.0), number1=2, number2=1, spacing1=2*L*math.cos(theta)+2*t, spacing2=2*h-2*L*math.sin(theta))#此处参考上一条

#: (mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-2-1-1'], mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-1-2-lin-2-1'], mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-2-2-lin-2-1'], mdb.models['Model-1'].rootAssembly.instances['Part-M-1-lin-2-1-lin-2-1'])
a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-MT', instances=(a.instances['Part-M-1'], 
    a.instances['Part-M-1-lin-1-2'], a.instances['Part-M-1-lin-2-1'], 
    a.instances['Part-M-1-lin-2-2'], a.instances['Part-M-1-lin-2-1-1'], 
    a.instances['Part-M-1-lin-1-2-lin-2-1'], 
    a.instances['Part-M-1-lin-2-2-lin-2-1'], 
    a.instances['Part-M-1-lin-2-1-lin-2-1'], ), originalInstances=SUPPRESS, 
    domain=GEOMETRY)
#加载面
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=(4*(L*math.cos(theta)+t)+t, 4*(L*math.cos(theta)+t)+t))#36.22=4*(L*cosθ+t)+t

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
a.translate(instanceList=('Part-P-1', ), vector=(-(L*math.cos(theta)+3.0/2.0*t), -h/2, -(L*math.cos(theta)+3.0/2.0*t)))#此处#9.48=L*cosθ+t+t/2，#-8.0=h/2
#: The instance Part-P-1 was translated by -9.48, -8., -9.48 with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-P']
a.Instance(name='Part-P-2', part=p, dependent=OFF)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('Part-P-2', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
#: The instance Part-P-2 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 1., 0., 0.
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('Part-P-2', ), vector=(-(L*math.cos(theta)+3.0/2.0*t), 4*h-4*L*math.sin(theta)-h/2, -(L*math.cos(theta)+3.0/2.0*t)))#此处#9.48=L*cosθ+t+t/2，#40.0=4*h-4*L*sinθ-h/2
#: The instance Part-P-2 was translated by -9.48, 40., -9.48 with respect to the assembly coordinate system

a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanMerge(name='Part-ME', instances=(a.instances['Part-MT-1'], 
    a.instances['Part-P-1'], a.instances['Part-P-2'], ), 
    originalInstances=SUPPRESS, domain=GEOMETRY)


#材料属性
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((160000.0, 0.27), ))
mdb.models['Model-1'].materials['Material-1'].Plastic(table=((350.0, 0.0), (
    400.0, 0.07), (500.0, 0.12), (600.0, 0.2), (700.0, 0.3), (800.0, 0.45), (
    900.0, 0.68), (1000.0, 0.9)))
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
p.seedPart(size=2.0, deviationFactor=0.1, minSizeFactor=0.1)
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
faces1 = f1.findAt(((0,4*h-4*L*math.sin(theta)-h/2,0),))
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
    region=region, u1=UNSET, u2=-20.0, u3=UNSET, ur1=UNSET, ur2=UNSET, 
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



