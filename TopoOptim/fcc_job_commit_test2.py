# -*- coding: utf-8 -*-
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os
import sys

os.environ['CUDA_VISIBLE_DEVICES'] = '1,2'
"""
参数获取，注意在abaqus cae中第八位及以后是附加参数
如os.system("abaqus cae noGUI=test.py -- 0.3 0.8"),此时0.8和0.3分别在8、9位
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
    direction2=(0.0, 1.0, 0.0), number1=2, number2=2, spacing1=12.0, 
    spacing2=12.0)

#第二次阵列
a.LinearInstancePattern(instanceList=('FCC-1', 'FCC-1-lin-1-2', 'FCC-1-lin-2-1', 
    'FCC-1-lin-2-2'), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2=2, spacing1=61.2, 
    spacing2=12.0)

#通过布尔运算形成整体FCClattice
a.InstanceFromBooleanMerge(name='FCClattice', instances=(a.instances['FCC-1'], 
    a.instances['FCC-1-lin-1-2'], a.instances['FCC-1-lin-2-1'], 
    a.instances['FCC-1-lin-2-2'], a.instances['FCC-1-lin-1-2-1'], 
    a.instances['FCC-1-lin-1-2-lin-1-2'], a.instances['FCC-1-lin-2-2-lin-1-2'], 
    a.instances['FCC-1-lin-2-1-lin-1-2'], ), originalInstances=SUPPRESS, 
    domain=GEOMETRY)

#加载平板
#: mdb.models['Model-1'].rootAssembly.instances['FCClattice-1']
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-2']
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.rectangle(point1=(-8.0, -8.0), point2=(20.0, 20.0))
p = mdb.models['Model-1'].Part(name='Part-uo', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p.BaseSolidExtrude(sketch=s, depth=2.0)
del mdb.models['Model-1'].sketches['__profile__']

a.Instance(name='Part-uo-1', part=p, dependent=OFF)
a.Instance(name='Part-uo-2', part=p, dependent=OFF)
a.translate(instanceList=('Part-uo-2', ), vector=(0.0, 0.0, 17.5))
a.translate(instanceList=('Part-uo-1', ), vector=(0.0, 0.0, -7.5))

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
p.seedPart(size=1.0, deviationFactor=0.1, minSizeFactor=0.1)
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
    'S','E','U','RF','IVOL'))

"""
设置边界条件：
1. 对'Part-3-1'实例中的一组面进行了位移边界条件的设置，固定在xyz方向上的位移为0。
2. 对另一组面进行了位移边界条件的设置，其中u3（z方向上的位移）被设定为-10.0。
"""
a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-3-1'].faces
faces1 = f1.getSequenceFromMask(mask=('[#20 ]', ), )
region = regionToolset.Region(faces=faces1)
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
    region=region, u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0,
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='',
    localCsys=None)

a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-3-1'].faces
faces1 = f1.getSequenceFromMask(mask=('[#0:13 #400000 ]', ), )
region = regionToolset.Region(faces=faces1)
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
    region=region, u1=UNSET, u2=UNSET, u3=-10.0, ur1=UNSET, ur2=UNSET,
    ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM,
    fieldName='', localCsys=None)

#创建集合
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-3-1'].elements
elements1 = e1.getSequenceFromMask(mask=(
    '[#0:6 #22 #0:13 #80000000 #0:18 #1 #0:25',
    ' #400000 #0:18 #200000 #0:2 #80000000 #0:9 #8000',
    ' #0:13 #400000 #0:2 #2000000 #0:16 #41 #0',
    ' #20000000 #400000 #0:15 #8000000 #4000 #0:11 #80',
    ' #0:21 #200 #0:20 #2 #0:5 #2000000 #0:8',
    ' #800 #0 #40000 #0:14 #800 #0:18 #4000000',
    ' #0 #400 #10000000 #0:15 #80000 #0:11 #2000',
    ' #0:4 #4 #0:15 #80 #0:12 #10000 #0:2',
    ' #80 #0:21 #80000 #0:2 #100000 #0:32 #20',
    ' #0 #80000 #0:4 #2000 #2 #4000 #0:3',
    ' #8000 #0 #8000000 #0 #2000 #1200000 #0',
    ' #c0004000 #24 #0:7 #24 #20 #0:7 #100',
    ' #120800 #108 #0 #20000 #802900 #8e201000 #4000000:2',
    ' #8000800 #0 #40 #80000400 #4000080 #10000 #80',
    ' #0:10 #1000000 #4400000 #c0000000 #40 #0:2 #8',
    ' #0 #81000000 #800400 #8840402 #44024 #20180000 #401200',
    ' #8a00 #4810080 #0 #40008c04 #10000000 #24000000 #253000',
    ' #0:5 #10020404 #0:2 #a001 #0:3 #1 #0:6',
    ' #180000 #0:2 #180 #0 #48000000 #0:3 #400',
    ' #0:2 #6408 #0:10 #10 #0:21 #2000000 #0:4',
    ' #80000 #0:88 #20000000 #1 #80 #2000000 #20000000',
    ' #38 #800000 #0:5 #20 #0 #800000 #10000',
    ' #0:24 #10000 #0:3 #10000 #0:27 #20000 #0:18',
    ' #2400 #40000 #0:5 #40000000 #400000c #0:8 #20000000',
    ' #2000000 #0:2 #100000 #0:11 #100000 #0:69 #8000000',
    ' #2080000 #8208120 #400030b0 #12 #30001 #81 #20',
    ' #80140 #8400000 #8060c00 #1001082 #2800001 #4080 #8200a20',
    ' #44008500 #11110a08 #10040802 #304e0070 #a410000 #1000030 #40112200',
    ' #820240 #4009260 #222182c2 #2003 #48400909 #202c0 #4800140',
    ' #17046248 #11000000 #a10cc188 #a0100115 #92218414 #340a0200 #40000004',
    ' #44124444 #40002001 #8008008 #85085580 #20001205 #14814780 #2040202',
    ' #40010001 #18004041 #910088e4 #1d901001 #90041004 #2bb0002 #2c0c8e48',
    ' #4248000 #6202080 #a80c1408 #200188 #4b00004c #2d006080 #188',
    ' #8008840 #8a803182 #2400023 #81880 #800a8004 #11108300 #1892002b',
    ' #4400a00 #1002319 #a000001 #2410800 #a0410a40 #80010800 #40001412',
    ' #110c240 #46c01010 #c000e000 #480608 #802288a0 #14098808 #e000000',
    ' #5040620 #20000204 #2811180 #1088c402 #81020040 #a18040 #e4b200',
    ' #58012 #100206c #2000 #b000400 #2015000 #30060 #1006410',
    ' #404402 #18200004 #1402110 #60021 #2885001 #10c018 #102800',
    ' #82000500 #1500000a #4050 #26820008 #80110690 #10800608 #8020000d',
    ' #40e02801 #6868006 #41 #1e000020 #10088069 #44020000 #802080a0',
    ' #810894a0 #d9a00024 #2082284 #e0002301 #1228806 #12082818 #14205080',
    ' #8950120 #10002018 #404102 #40204c02 #9080010 #881c00 #42002400',
    ' #2181581 #281 #1001080 #1004801 #20020c02 #8238 #21001188',
    ' #4400 #100002 #4601a080 #861780 #4001800 #c030010 #20000018',
    ' #20120000 #200002 #83000820 #6091000 #c0005010 #40810 #80002404',
    ' #10800c00 #2010 #81214084 #2180004 #14080101 #8020 #2000000',
    ' #200200 #40004040 #8000 #0:41 #220000 #9006000 #21100040',
    ' #8020000 #40081848 #4400001 #0:5 #40021400 #82400 #20860000',
    ' #2000 #210c022 #2000 #0:2 #400000 #0 #80000000',
    ' #0 #4400140 #140044 #10104 #1 #0:2 #40000000',
    ' #20 #0 #4502000 #900800 #800 #e160004 #c001',
    ' #2 #8000 #0 #200000 #0 #10000 #8000',
    ' #0:6 #80000 #0 #800000 #9000200 #0:5 #100',
    ' #20000 #0:4 #80008 #0:20 #10000000 #0 #1',
    ' #0:2 #40 #80000 #0:2 #1000040 #0:2 #10000',
    ' #0:3 #10000840 #0:2 #8000 #240 #0:8 #80',
    ' #0:18 #400000 #0:5 #2000 #12008 #0:6 #101000',
    ' #8400 #0 #400100 #0:3 #40020 #0 #2',
    ' #0:3 #20000000 #0:3 #8000000 #0:3 #1000 #800',
    ' #0:2 #4 #0:5 #180 #0:10 #20 #20000000',
    ' #0:18 #20000 #0:11 #10000 #0 #400 #0:88',
    ' #100000 #0:130 #c0000 #0:10 #100 #0:2 #1000000',
    ' #0:4 #8000 #0:6 #2000000 #0 #8 #0:28',
    ' #10000 #0:45 #4000 #0:63 #80000000 #0:10 #400000',
    ' #0:5 #8000000 #1000 #0:2 #8520 #4 #8000',
    ' #80000000 #0:3 #8000 #2 #0 #10000 #0:18',
    ' #10 #0 #100000 #0:5 #2000000 #0:3 #1000100',
    ' #40000000 #0:3 #800 #200000 #0:2 #142000 #400',
    ' #2 #0:4 #4000000 #4 #0:15 #8000 #0:7',
    ' #80 #0:21 #2000001 #8000 #0:14 #10008000 #0:22',
    ' #40000 #0:2 #80000000 #0:8 #10 #0:8 #8000000',
    ' #0:101 #40000 #0:47 #441900 #4 #400 #4000102',
    ' #1880 #0 #40080100 #0:4 #80 #40 #241c00',
    ' #c0 #104 #8000000 #0 #1001000 #0 #20000000',
    ' #600 #b8004020 #92200002 #0:2 #200000 #20080 #1001010',
    ' #100 #0 #80000000 #0 #8 #2000000 #0',
    ' #2 #0:2 #400000 #0:2 #20 #400000 #80000000',
    ' #1d000000 #4000000 #30820514 #22000002 #0 #500003 #80000000',
    ' #10 #30100000 #1400 #14000000 #0 #20800 #0',
    ' #202 #2020100 #1000000 #0:2 #3000004 #400a40 #0:2',
    ' #4000 #0 #41001480 #0 #10401000 #84c #0',
    ' #1000020 #4342001 #1008008 #100 #0 #104 #10000',
    ' #0:2 #20 #0 #1 #8000000 #40000 #0', ' #4 #20 #9800000 #100 #0 #43 #0:2',
    ' #24000000 #85000204 #2020000 #1000040 #0 #104000 #2400010',
    ' #80000 #2000 #a0410821 #2 #0 #3400002 #830000',
    ' #80000 #10508000 #5800 #2 #2000000 #0 #20000000',
    ' #0 #4600080 #6000000 #0 #800000 #400400 #0',
    ' #40000020 #4000000 #0:2 #40040100 #0 #940000 #0:3',
    ' #88000 #22020000 #20000000 #0 #400000 #1000 #0:2',
    ' #1 #0:3 #1000 #0 #20000000 #4008000 #0:10',
    ' #100000 #0 #800 #0:2 #1400000 #110004 #2400230',
    ' #40 #0:2 #2 #0:3 #82800020 #8000 #0:2',
    ' #2000024 #40180 #100000 #400000 #10008001 #62 #0:3',
    ' #4000 #0 #40000000 #0 #21000 #10000 #1000',
    ' #0 #200 #40000000 #100000 #0 #400000 #400',
    ' #0:2 #80000100 #8000400 #0:2 #200 #20100000 #8000',
    ' #0:4 #800000 #0 #200000 #80000 #10000 #800000',
    ' #0 #20 #0 #800 #100 #0:9 #800000',
    ' #200000 #0 #8000 #0 #1000 #0:3 #200',
    ' #0:3 #80001000 #0:2 #20 #800000 #40 #4',
    ' #0 #100000 #0 #2 #20140 #0 #80000004',
    ' #80000 #0:9 #2000200 #400000 #0:5 #80000000 #4000',
    ' #0:2 #400000 #10002000 #0 #20000 #0 #2',
    ' #0:2 #8000 #0:4 #80000 #0:2 #8 #0:3',
    ' #80800000 #0:5 #200 #0:3 #800 #0:2 #20000000',
    ' #0:21 #8000000 #0 #2:2 #0 #40 #0', ' #4000 #8 #0:4 #800 #0:9 #4 #0:4',
    ' #80 #0 #400000 #0:10 #400 #0:4 #40000',
    ' #0:2 #4 #0:7 #1000000 #10000000 #0:2 #10',
    ' #20000 #800 #0:8 #80000000 #0 #4000 #0:37',
    ' #20000000 #0 #8000000 #0:3 #200000 #0:61 #20000000',
    ' #0:5 #100 #0:46 #100000 #0:16 #80000000 #0:20',
    ' #10000000 #0:75 #400000 #0:51 #8 #0:4 #400000',
    ' #0:29 #80000000 #0:17 #8000 #0:11 #80 #0:62',
    ' #1000000 #0:49 #2 #0:6 #10000000 #0:7 #4000000',
    ' #0:16 #80 #0:13 #800 #0:28 #40000000 #0:2',
    ' #40000 #0:6 #80000000 #0:61 #200 #0:28 #2',
    ' #0:3 #2 #0:29 #80000000 #0:110 #8 #0:13',
    ' #800 #0:5 #20 #0:17 #40000 #0:25 #1200000',
    ' #0 #800 #0:5 #100000 #0:3 #80000 #0:51',
    ' #1000000 #0:65 #400 #0:19 #40000 #0:3 #100000',
    ' #0:19 #200000 #0:28 #400 #0:65 #80000000 #0:3',
    ' #20 #0:10 #2 #0:43 #2000000 #0:3 #24000',
    ' #0:2 #800 #0:10 #80000 #0:32 #80000000 #0:6',
    ' #40 #0:12 #10000 #0:23 #20 #0:7 #3000000',
    ' #0:10 #1 #0:12 #4000 #0:35 #40000 #0:3',
    ' #2 #0:5 #10000 #0:8 #400000 #0:24 #400000',
    ' #100 #0:27 #20000000 #0:42 #80 #0:11 #10000',
    ' #0:3 #10000000 #0:40 #1000000 #0:9 #10000 #0:8',
    ' #4000000 #0:4 #10000 #0:6 #4000 #0:20 #40000000',
    ' #0:9 #800 #0:6 #8000 #0:4 #200000 #0:12',
    ' #1 #0:4 #10000000 #0:10 #4 #0:3 #1001000',
    ' #0:3 #100 #0 #4000 #0:51 #4000000 #0:10',
    ' #40000000 #0:3 #10000000 #1000000 #0:9 #8000 #0:10',
    ' #400 #0:11 #8000000 #80 #0:135 #4000 ]', ), )
a.Set(elements=elements1, name='Set-FCC')


#设置job任务
mdb.Job(name=jobpath, model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=40, 
    numDomains=40, numGPUs=2)
#保存以及提交任务
mdb.jobs[jobpath].submit(consistencyChecking=OFF)

# mdb.saveAs('fcclattice')
# 打开文本文件，若不存在则创建
# file = open("output.txt", "w")
# file.write("succeed")
# file.close()
