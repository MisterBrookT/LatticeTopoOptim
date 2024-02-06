# -*- coding: utf-8 -*-
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os
import sys

"""
参数获取，注意在abaqus cae中第八位及以后是附加参数
如os.system("abaqus cae noGUI=test.py -- 0.8 0.3"),此时0.8和0.3分别在8、9位
"""
inner = float(sys.argv[8])
outer = float(sys.argv[9])
file_path, file_extension = os.path.splitext(sys.argv[10])
jobpath = file_path
#建模过程
#一号杆
s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints

s.Line(point1=(-6.0,6.0 ), point2=(6.0, -6.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0, transform=(-0.707106781186548, -0.707106781186548, 0.0, 
    0.0, 0.0, 1.0, -0.707106781186548, 0.707106781186548, 0.0, -6.0, 6.0, 0.0))

g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
s1.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(outer, 0.0))
s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(inner, 0.0))

p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)

p.BaseSolidSweep(sketch=s1, path=s)
p = mdb.models['Model-1'].parts['Part-1']

del mdb.models['Model-1'].sketches['__profile__']
del mdb.models['Model-1'].sketches['__sweep__']

#二号杆
s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.Line(point1=(6.0, 6.0), point2=(-6.0, -6.0))

s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0, transform=(-0.707106781186548, 0.707106781186548, 0.0, 
    0.0, -0.0, 1.0, 0.707106781186548, 0.707106781186548, 0.0, 6.0, 6.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
s1.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(outer, 0.0))
s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(inner, 0.0))

p = mdb.models['Model-1'].Part(name='Part-2', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-2']
p.BaseSolidSweep(sketch=s1, path=s)
p = mdb.models['Model-1'].parts['Part-2']

session.viewports['Viewport: 1'].setValues(displayedObject=p)

del mdb.models['Model-1'].sketches['__profile__']
del mdb.models['Model-1'].sketches['__sweep__']

#两杆合一形成face-1
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=OFF)
p = mdb.models['Model-1'].parts['Part-2']
a.Instance(name='Part-2-1', part=p, dependent=OFF)

#两根杆instance凑成一个face基本面
a.InstanceFromBooleanMerge(name='face-1', instances=(a.instances['Part-1-1'], 
    a.instances['Part-2-1'], ), originalInstances=SUPPRESS, domain=GEOMETRY)
#rotate是杆旋转，translate是杆移动，旋转移动十字基本面
a.rotate(instanceList=('Part-1-1', 'Part-2-1', 'face-1-1'), axisPoint=(0.0, 
    0.0, 0.0), axisDirection=(0.0, 1.0, 0.0), angle=90.0)
a.translate(instanceList=('Part-1-1', 'Part-2-1', 'face-1-1'), vector=(6.0, 
    0.0, 0.0))

#face-2
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-2', part=p, dependent=OFF)
p = mdb.models['Model-1'].parts['Part-2']
a.Instance(name='Part-2-2', part=p, dependent=OFF)
a.InstanceFromBooleanMerge(name='face-2', instances=(a.instances['Part-1-2'], 
    a.instances['Part-2-2'], ), originalInstances=SUPPRESS, domain=GEOMETRY)
a.rotate(instanceList=('face-2-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=90.0)
a.translate(instanceList=('face-2-1', ), vector=(-6.0, 0.0, 0.0))

#结合初始两杆引入face-3并旋转平移（参考face-2操作步骤）
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-3', part=p, dependent=OFF)
p = mdb.models['Model-1'].parts['Part-2']
a.Instance(name='Part-2-3', part=p, dependent=OFF)
a.InstanceFromBooleanMerge(name='face-3', instances=(a.instances['Part-1-3'], 
    a.instances['Part-2-3'], ), originalInstances=SUPPRESS, domain=GEOMETRY)
a.rotate(instanceList=('face-3-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
a.translate(instanceList=('face-3-1', ), vector=(0.0, 6.0, 0.0))

#结合初始两杆引入face-4并旋转平移（参考face-2操作步骤）
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-4', part=p, dependent=OFF)
p = mdb.models['Model-1'].parts['Part-2']
a.Instance(name='Part-2-4', part=p, dependent=OFF)
a.InstanceFromBooleanMerge(name='face-4', instances=(a.instances['Part-1-4'], 
    a.instances['Part-2-4'], ), originalInstances=SUPPRESS, domain=GEOMETRY)
a.rotate(instanceList=('face-4-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
a.translate(instanceList=('face-4-1', ), vector=(0.0, -6.0, 0.0))

#结合初始两杆引入face-5并平移（不需要旋转）
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-5', part=p, dependent=OFF)
p = mdb.models['Model-1'].parts['Part-2']
a.Instance(name='Part-2-5', part=p, dependent=OFF)
a.InstanceFromBooleanMerge(name='face-5', instances=(a.instances['Part-1-5'], 
    a.instances['Part-2-5'], ), originalInstances=SUPPRESS, domain=GEOMETRY)
a.translate(instanceList=('face-5-1', ), vector=(0.0, 0.0, -6.0))

#结合初始两杆引入face-6并平移（不需要旋转参考face-5）
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-6', part=p, dependent=OFF)
p = mdb.models['Model-1'].parts['Part-2']
a.Instance(name='Part-2-6', part=p, dependent=OFF)
a.InstanceFromBooleanMerge(name='face-6', instances=(a.instances['Part-1-6'], 
    a.instances['Part-2-6'], ), originalInstances=SUPPRESS, domain=GEOMETRY)
a.translate(instanceList=('face-6-1', ), vector=(0.0, 0.0, 6.0))

#通过布尔运算形成单个FCC
a.InstanceFromBooleanMerge(name='FCC', instances=(a.instances['face-1-1'], 
    a.instances['face-2-1'], a.instances['face-3-1'], a.instances['face-4-1'], 
    a.instances['face-5-1'], a.instances['face-6-1'], ), 
    originalInstances=SUPPRESS, domain=GEOMETRY)

#通过阵列形成FCClattice（两次阵列）
#第一次阵列
a.LinearInstancePattern(instanceList=('FCC-1', ), direction1=(1.0, 0.0, 0.0), 
    direction2=(0.0, 1.0, 0.0), number1=5, number2=5, spacing1=12.0, 
    spacing2=12.0)

#第二次阵列
a.LinearInstancePattern(instanceList=('FCC-1', 'FCC-1-lin-1-2', 
    'FCC-1-lin-1-3', 'FCC-1-lin-1-4', 'FCC-1-lin-1-5', 'FCC-1-lin-2-1', 
    'FCC-1-lin-2-2', 'FCC-1-lin-2-3', 'FCC-1-lin-2-4', 'FCC-1-lin-2-5', 
    'FCC-1-lin-3-1', 'FCC-1-lin-3-2', 'FCC-1-lin-3-3', 'FCC-1-lin-3-4', 
    'FCC-1-lin-3-5', 'FCC-1-lin-4-1', 'FCC-1-lin-4-2', 'FCC-1-lin-4-3', 
    'FCC-1-lin-4-4', 'FCC-1-lin-4-5', 'FCC-1-lin-5-1', 'FCC-1-lin-5-2', 
    'FCC-1-lin-5-3', 'FCC-1-lin-5-4', 'FCC-1-lin-5-5'), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2=5, spacing1=61.2, 
    spacing2=12.0)

#通过布尔运算形成整体FCClattice
a.InstanceFromBooleanMerge(name='FCClattice', instances=(a.instances['FCC-1'], 
    a.instances['FCC-1-lin-1-2'], a.instances['FCC-1-lin-1-3'], 
    a.instances['FCC-1-lin-1-4'], a.instances['FCC-1-lin-1-5'], 
    a.instances['FCC-1-lin-2-1'], a.instances['FCC-1-lin-2-2'], 
    a.instances['FCC-1-lin-2-3'], a.instances['FCC-1-lin-2-4'], 
    a.instances['FCC-1-lin-2-5'], a.instances['FCC-1-lin-3-1'], 
    a.instances['FCC-1-lin-3-2'], a.instances['FCC-1-lin-3-3'], 
    a.instances['FCC-1-lin-3-4'], a.instances['FCC-1-lin-3-5'], 
    a.instances['FCC-1-lin-4-1'], a.instances['FCC-1-lin-4-2'], 
    a.instances['FCC-1-lin-4-3'], a.instances['FCC-1-lin-4-4'], 
    a.instances['FCC-1-lin-4-5'], a.instances['FCC-1-lin-5-1'], 
    a.instances['FCC-1-lin-5-2'], a.instances['FCC-1-lin-5-3'], 
    a.instances['FCC-1-lin-5-4'], a.instances['FCC-1-lin-5-5'], 
    a.instances['FCC-1-lin-1-2-1'], a.instances['FCC-1-lin-1-3-1'], 
    a.instances['FCC-1-lin-1-4-1'], a.instances['FCC-1-lin-1-5-1'], 
    a.instances['FCC-1-lin-1-2-lin-1-2'], a.instances['FCC-1-lin-1-2-lin-1-3'], 
    a.instances['FCC-1-lin-1-2-lin-1-4'], a.instances['FCC-1-lin-1-2-lin-1-5'], 
    a.instances['FCC-1-lin-1-4-lin-1-2'], a.instances['FCC-1-lin-1-4-lin-1-3'], 
    a.instances['FCC-1-lin-1-4-lin-1-4'], a.instances['FCC-1-lin-1-4-lin-1-5'], 
    a.instances['FCC-1-lin-2-2-lin-1-2'], a.instances['FCC-1-lin-2-2-lin-1-3'], 
    a.instances['FCC-1-lin-2-2-lin-1-4'], a.instances['FCC-1-lin-2-2-lin-1-5'], 
    a.instances['FCC-1-lin-2-4-lin-1-2'], a.instances['FCC-1-lin-2-4-lin-1-3'], 
    a.instances['FCC-1-lin-2-4-lin-1-4'], a.instances['FCC-1-lin-2-4-lin-1-5'], 
    a.instances['FCC-1-lin-3-2-lin-1-2'], a.instances['FCC-1-lin-3-2-lin-1-3'], 
    a.instances['FCC-1-lin-3-2-lin-1-4'], a.instances['FCC-1-lin-3-2-lin-1-5'], 
    a.instances['FCC-1-lin-4-2-lin-1-2'], a.instances['FCC-1-lin-4-2-lin-1-3'], 
    a.instances['FCC-1-lin-4-2-lin-1-4'], a.instances['FCC-1-lin-4-2-lin-1-5'], 
    a.instances['FCC-1-lin-4-4-lin-1-2'], a.instances['FCC-1-lin-4-4-lin-1-3'], 
    a.instances['FCC-1-lin-4-4-lin-1-4'], a.instances['FCC-1-lin-4-4-lin-1-5'], 
    a.instances['FCC-1-lin-3-4-lin-1-2'], a.instances['FCC-1-lin-3-4-lin-1-3'], 
    a.instances['FCC-1-lin-3-4-lin-1-4'], a.instances['FCC-1-lin-3-4-lin-1-5'], 
    a.instances['FCC-1-lin-5-2-lin-1-2'], a.instances['FCC-1-lin-5-2-lin-1-3'], 
    a.instances['FCC-1-lin-5-2-lin-1-4'], a.instances['FCC-1-lin-5-2-lin-1-5'], 
    a.instances['FCC-1-lin-5-4-lin-1-2'], a.instances['FCC-1-lin-5-4-lin-1-3'], 
    a.instances['FCC-1-lin-5-4-lin-1-4'], a.instances['FCC-1-lin-5-4-lin-1-5'], 
    a.instances['FCC-1-lin-1-3-lin-1-2'], a.instances['FCC-1-lin-1-3-lin-1-3'], 
    a.instances['FCC-1-lin-1-3-lin-1-4'], a.instances['FCC-1-lin-1-3-lin-1-5'], 
    a.instances['FCC-1-lin-1-5-lin-1-2'], a.instances['FCC-1-lin-1-5-lin-1-3'], 
    a.instances['FCC-1-lin-1-5-lin-1-4'], a.instances['FCC-1-lin-1-5-lin-1-5'], 
    a.instances['FCC-1-lin-2-1-lin-1-2'], a.instances['FCC-1-lin-2-1-lin-1-3'], 
    a.instances['FCC-1-lin-2-1-lin-1-4'], a.instances['FCC-1-lin-2-1-lin-1-5'], 
    a.instances['FCC-1-lin-2-3-lin-1-2'], a.instances['FCC-1-lin-2-3-lin-1-3'], 
    a.instances['FCC-1-lin-2-3-lin-1-4'], a.instances['FCC-1-lin-2-3-lin-1-5'], 
    a.instances['FCC-1-lin-2-5-lin-1-2'], a.instances['FCC-1-lin-2-5-lin-1-3'], 
    a.instances['FCC-1-lin-2-5-lin-1-4'], a.instances['FCC-1-lin-2-5-lin-1-5'], 
    a.instances['FCC-1-lin-4-1-lin-1-2'], a.instances['FCC-1-lin-4-1-lin-1-3'], 
    a.instances['FCC-1-lin-4-1-lin-1-4'], a.instances['FCC-1-lin-4-1-lin-1-5'], 
    a.instances['FCC-1-lin-4-3-lin-1-2'], a.instances['FCC-1-lin-4-3-lin-1-3'], 
    a.instances['FCC-1-lin-4-3-lin-1-4'], a.instances['FCC-1-lin-4-3-lin-1-5'], 
    a.instances['FCC-1-lin-4-5-lin-1-2'], a.instances['FCC-1-lin-4-5-lin-1-3'], 
    a.instances['FCC-1-lin-4-5-lin-1-4'], a.instances['FCC-1-lin-4-5-lin-1-5'], 
    a.instances['FCC-1-lin-3-1-lin-1-2'], a.instances['FCC-1-lin-3-1-lin-1-3'], 
    a.instances['FCC-1-lin-3-1-lin-1-4'], a.instances['FCC-1-lin-3-1-lin-1-5'], 
    a.instances['FCC-1-lin-3-3-lin-1-2'], a.instances['FCC-1-lin-3-3-lin-1-3'], 
    a.instances['FCC-1-lin-3-3-lin-1-4'], a.instances['FCC-1-lin-3-3-lin-1-5'], 
    a.instances['FCC-1-lin-3-5-lin-1-2'], a.instances['FCC-1-lin-3-5-lin-1-3'], 
    a.instances['FCC-1-lin-3-5-lin-1-4'], a.instances['FCC-1-lin-3-5-lin-1-5'], 
    a.instances['FCC-1-lin-5-1-lin-1-2'], a.instances['FCC-1-lin-5-1-lin-1-3'], 
    a.instances['FCC-1-lin-5-1-lin-1-4'], a.instances['FCC-1-lin-5-1-lin-1-5'], 
    a.instances['FCC-1-lin-5-3-lin-1-2'], a.instances['FCC-1-lin-5-3-lin-1-3'], 
    a.instances['FCC-1-lin-5-3-lin-1-4'], a.instances['FCC-1-lin-5-3-lin-1-5'], 
    a.instances['FCC-1-lin-5-5-lin-1-2'], a.instances['FCC-1-lin-5-5-lin-1-3'], 
    a.instances['FCC-1-lin-5-5-lin-1-4'], a.instances['FCC-1-lin-5-5-lin-1-5'], 
    ), originalInstances=SUPPRESS, domain=GEOMETRY)

#加载平板
#: mdb.models['Model-1'].rootAssembly.instances['FCClattice-1']
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-2']
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.rectangle(point1=(-6.0, -6.0), point2=(54.0, 54.0))
p = mdb.models['Model-1'].Part(name='Part-uo', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p.BaseSolidExtrude(sketch=s, depth=2.0)
del mdb.models['Model-1'].sketches['__profile__']

a.Instance(name='Part-uo-1', part=p, dependent=OFF)
a.Instance(name='Part-uo-2', part=p, dependent=OFF)
a.translate(instanceList=('Part-uo-2', ), vector=(0.0, 0.0, 54.5))
a.translate(instanceList=('Part-uo-1', ), vector=(0.0, 0.0, -6.5))

#布尔运算形成part-3，带两个平面的模型整体
a.InstanceFromBooleanMerge(name='Part-3', instances=(
    a.instances['FCClattice-1'], a.instances['Part-uo-1'], 
    a.instances['Part-uo-2'], ), originalInstances=SUPPRESS, domain=GEOMETRY)

#划分并生成网格，setMeshControls用于设置网格划分的方法
p = mdb.models['Model-1'].parts['Part-3']
c = p.cells
pickedRegions = c.getSequenceFromMask(mask=('[#3 ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
cells = c.getSequenceFromMask(mask=('[#3 ]', ), )
pickedRegions =(cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
    elemType3))
p.seedPart(size=0.4, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

#使用我们收集的材料应力应变曲线数据来材料属性校准
#修改
mdb.models['Model-1'].Calibration(name='Calibration-1')
mdb.models['Model-1'].calibrations['Calibration-1'].DataSet(name='DataSet-1')
mdb.models['Model-1'].calibrations['Calibration-1'].dataSets['DataSet-1'].setValues(
    data=((0.0, 2.3), (0.01135, 108.6), (0.02246, 214.9), (0.03454, 329.67356), 
    (0.04704, 442.25685), (0.04954, 462.55637), (0.05204, 480.89028), (0.05454, 
    498.22184), (0.05704, 513.74487), (0.05954, 527.69042), (0.06204, 
    539.42115), (0.06454, 548.72434), (0.06704, 557.70886), (0.06954, 
    566.01667), (0.07204, 572.27807), (0.07454, 577.41943), (0.07704, 
    581.97403), (0.07954, 585.10125), (0.08204, 587.76885), (0.08454, 
    590.65369), (0.08704, 592.34888), (0.08954, 594.36752), (0.09204, 
    595.4992), (0.09454, 596.46464), (0.09704, 597.47628), (0.09954, 
    598.54112), (0.10204, 599.33785), (0.10454, 600.09085), (0.10704, 
    600.25708), (0.10954, 600.29864), (0.11204, 600.38176), (0.11454, 
    600.54116), (0.11704, 600.66816)), type='Stress/Strain', form='NOMINAL')

#创建材料和校准曲线
mdb.models['Model-1'].calibrations['Calibration-1'].Behavior(name='Behavior-1', 
    typeName='ElasPlasIsoBehavior')
mdb.models['Model-1'].Material(name='Material-1')

#校准曲线Behavior-1
mdb.models['Model-1'].calibrations['Calibration-1'].behaviors['Behavior-1'].setValues(
    ds1Name='DataSet-1', ultimatePoint=(0.10461, 600.07), yieldPoint=(0.04508, 
    425.496), plasticPoints=((0.04508, 425.4958), (0.04704, 442.25685), (
    0.0488038084388, 456.630225808), (0.0494082791213, 461.617207314), (
    0.0494756345736, 462.156160684), (0.0496249703757, 463.160801483), (
    0.0501984807037, 467.361953195), (0.0510479891517, 473.624709314), (
    0.0519750765895, 480.418085727), (0.0528165853342, 486.474416416), (
    0.0535848019753, 491.836181548), (0.0543464733266, 496.952548012), (
    0.0551621688248, 502.23047206), (0.0560393697123, 507.714061296), (
    0.0569585681013, 513.26295728), (0.0579045879652, 518.759024942), (
    0.0588858904793, 524.207280916), (0.0599190513072, 529.652181919), (
    0.0610433378876, 535.114696231), (0.0623304463972, 540.581874009), (
    0.0637931886748, 546.044329314), (0.0653151904696, 551.505902423), (
    0.0668340845406, 556.96859698), (0.0683893990183, 562.431154918), (
    0.0702173419946, 567.893556761), (0.0725425524938, 573.356035058), (
    0.0752373457279, 578.818498149), (0.0787986247469, 584.280963583), (
    0.0835429031086, 589.743427737), (0.0913144713181, 595.20588647), (0.11704, 
    600.66816)), plasticPointsRange=(100, 71, 100), ds2Name='DataSet-1', 
    elasticModulus=9438.68, PoissonsRatio=0.3)

#绘制应力应变曲线
calibPlot = session.XYPlot('DataSet-1')
calibPlot.title.setValues(useDefault=True)
ch = calibPlot.charts.values()[0]
ds = mdb.models['Model-1'].calibrations['Calibration-1'].dataSets['DataSet-1']
cxy = session.XYData(name='DataSet-1', data=ds.data, sourceDescription='Data')
cu = session.Curve(cxy)
ch.setValues(curvesToPlot=(cu, ), appendMode=False)
cu.lineStyle.setValues(show=True)
cu.symbolStyle.setValues(show=False)
xTitle = "Strain"
yTitle = "Stress"
ch.axes1[0].axisData.setValues(useSystemTitle=False, title=xTitle)
ch.axes2[0].axisData.setValues(useSystemTitle=False, title=yTitle)
session.viewports[session.currentViewportName].setValues(
    displayedObject=calibPlot)

#曲线上ultimate
calibPlot = session.xyPlots['DataSet-1']
calibPlot.title.setValues(useDefault=True)
ch = calibPlot.charts.values()[0]
cxy = session.XYData(name='DataSet-1-UltimatePt', data=((0.10461, 600.07), ), 
    sourceDescription='Data')
cu = session.Curve(cxy)
ch.setValues(curvesToPlot=(cu, ), appendMode=True)
cu.lineStyle.setValues(show=False)
cu.symbolStyle.setValues(show=True, marker=FILLED_TRI, color="Red")
cu.symbolStyle.setValues(size=3.0)
session.viewports[session.currentViewportName].setValues(
    displayedObject=calibPlot)

#yieldpt曲线
calibPlot = session.xyPlots['DataSet-1']
calibPlot.title.setValues(useDefault=True)
ch = calibPlot.charts.values()[0]
cxy = session.XYData(name='DataSet-1-YieldPt', data=((0.04508, 425.496), ), 
    sourceDescription='Data')
cu = session.Curve(cxy)
ch.setValues(curvesToPlot=(cu, ), appendMode=True)
cu.lineStyle.setValues(show=False)
cu.symbolStyle.setValues(show=True, marker=FILLED_CIRCLE, color="Blue")
cu.symbolStyle.setValues(size=3.0)
session.viewports[session.currentViewportName].setValues(
    displayedObject=calibPlot)

#elasticmodulus 曲线
calibPlot = session.xyPlots['DataSet-1']
calibPlot.title.setValues(useDefault=True)
ch = calibPlot.charts.values()[0]
cxy = session.XYData(name='DataSet-1-ElasticModulus', data=((0.0, 0.0), (
    0.04508, 425.496)), sourceDescription='Data')
cu = session.Curve(cxy)
ch.setValues(curvesToPlot=(cu, ), appendMode=True)
cu.lineStyle.setValues(show=True)
cu.symbolStyle.setValues(show=False)
session.viewports[session.currentViewportName].setValues(
    displayedObject=calibPlot)

#plasticpt 曲线
calibPlot = session.xyPlots['DataSet-1']
calibPlot.title.setValues(useDefault=True)
ch = calibPlot.charts.values()[0]
cxy = session.XYData(name='DataSet-1-PlasticPts', data=((0.04508, 425.4958), (
    0.04704, 442.25685), (0.0488038084388, 456.630225808), (0.0494082791213, 
    461.617207314), (0.0494756345736, 462.156160684), (0.0496249703757, 
    463.160801483), (0.0501984807037, 467.361953195), (0.0510479891517, 
    473.624709314), (0.0519750765895, 480.418085727), (0.0528165853342, 
    486.474416416), (0.0535848019753, 491.836181548), (0.0543464733266, 
    496.952548012), (0.0551621688248, 502.23047206), (0.0560393697123, 
    507.714061296), (0.0569585681013, 513.26295728), (0.0579045879652, 
    518.759024942), (0.0588858904793, 524.207280916), (0.0599190513072, 
    529.652181919), (0.0610433378876, 535.114696231), (0.0623304463972, 
    540.581874009), (0.0637931886748, 546.044329314), (0.0653151904696, 
    551.505902423), (0.0668340845406, 556.96859698), (0.0683893990183, 
    562.431154918), (0.0702173419946, 567.893556761), (0.0725425524938, 
    573.356035058), (0.0752373457279, 578.818498149), (0.0787986247469, 
    584.280963583), (0.0835429031086, 589.743427737), (0.0913144713181, 
    595.20588647), (0.11704, 600.66816)), sourceDescription='Data')
cu = session.Curve(cxy)
ch.setValues(curvesToPlot=(cu, ), appendMode=True)
cu.lineStyle.setValues(show=False)
cu.symbolStyle.setValues(show=True, marker=HOLLOW_CIRCLE, color="Brown")
cu.symbolStyle.setValues(size=2.0)
session.viewports[session.currentViewportName].setValues(
    displayedObject=calibPlot)

"""
1. 将名为'Behavior-1'的材料校准映射到名为'Material-1'的材料上。
2. 创建了一个名为'Section-1'的均质实体截面，采用'Material-1'材料，无需定义厚度。
3. 对'Part-3'部件中的指定单元进行了截面分配，使用了之前定义的'Section-1'截面。
4. 重定义这个装配体的材料属性
"""
mdb.models['Model-1'].calibrations['Calibration-1'].behaviors['Behavior-1'].mapToMaterial(
    'Material-1')
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-1', thickness=None)
p = mdb.models['Model-1'].parts['Part-3']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#3 ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
a = mdb.models['Model-1'].rootAssembly
a.regenerate()

"""
静力学分析设置：
1. 创建了一个名为'Step-1'的静力学分析步骤，设置了最大增量次数、初始增量、最大增量等参数。
2. 设置了场输出请求的变量为应力和应变。
"""
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial', 
    maxNumInc=10000, initialInc=0.1, maxInc=0.1)
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
    'S', 'E', 'U', 'RF', 'IVOL'))

"""
设置边界条件：
1. 对'Part-3-1'实例中的一组面进行了位移边界条件的设置，固定在xyz方向上的位移为0。
2. 对另一组面进行了位移边界条件的设置，其中u3（z方向上的位移）被设定为-10.0。
"""
a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-3-1'].faces
faces1 = f1.getSequenceFromMask(mask=('[#0:6 #400000 ]', ), )
region = regionToolset.Region(faces=faces1)
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', 
    region=region, u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0, 
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-3-1'].faces
faces1 = f1.getSequenceFromMask(mask=('[#0 #80000000 ]', ), )
region = regionToolset.Region(faces=faces1)
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', 
    region=region, u1=UNSET, u2=UNSET, u3=-10.0, ur1=UNSET, ur2=UNSET, 
    ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, 
    fieldName='', localCsys=None)
#创建集合
a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-3-1'].faces
faces1 = f1.getSequenceFromMask(mask=('[#0 #80000000 ]', ), )
a.Set(faces=faces1, name='Set-FCC')


#设置job任务
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=20, 
    numDomains=20, numGPUs=0)
#保存以及提交任务
mdb.jobs[jobpath].submit(consistencyChecking=OFF)
