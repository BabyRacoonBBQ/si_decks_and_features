"""Manually transcribed source rows; screenshots remain the primary originals."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
case_rows = '''1|Backend_FlipChip|Flip-Chip Package Reliability Optimization With Copper Pillar Stress and Crack Modelling|Backend|mode mechanics|Applications_Library/Backend/CopperPillar_FlipChip_Crack|未开始
2|Backend_CopperReliability|Reliability and Optimization of Copper Pillar Bumps in High-Performance Flip-Chip Packages|Backend|mode mechanics|Applications_Library/Backend/CopperPillar_Reliability|未开始
3|Backend_Thermomech|Coupled Thermomechanical Reliability Analysis of Power Semiconductor Packages|Backend|mode mechanics|Applications_Library/Backend/Package_ThermomechanicalReliability|未开始
4|Backend_Stress|Modeling Mechanical Stress Evolution During BEOL Fabrication and Package Assembly Process|Backend|mode mechanics|Applications_Library/Backend/PackageAssembly_Stress|未开始
5|Backend_SolderReliability|Mechanical Reliability Analysis of Advanced Bumping Schemes Under Chip-Package Integration|Backend|mode mechanics|Applications_Library/Backend/SolderBump_Reliability|未开始
6|Backend_SRAM|Processing and Modeling of 6T SRAM Backend Structure Using Sentaurus Interconnect Based on Rectangular Geometries|Backend|mode mechanics; mode current thermal mechanics|Applications_Library/Backend/SRAM_Backend|未开始
7|Backend_SRAMRounding|Processing and Modeling of 6T SRAM Backend Structure Using Sentaurus Interconnect|Backend|mode mechanics; mode current thermal mechanics|Applications_Library/Backend/SRAM_Backend_Rounding|未开始
8|Backend_Fatigue|Prediction of Flip-Chip Bump Thermal Fatigue Life From Full-Package Board-Level Simulations Using Nonlinear Material Models|Backend|TODO|Applications_Library/Backend/FlipChip_BumpFatigue|未开始
9|Damascene|Example-Three-Dimensional Damascene Structure|Training manual|mode mechanics; mode mechanics current thermal|Applications_Library/GettingStarted/sinterconnect/DualDamascene|全流程跑通，输出一致
10|Cantilever|Example: Cantilever With End Load (3D)|Training manual|mode mechanics|Applications_Library/GettingStarted/sinterconnect/3D_Cantilever|全流程跑通，输出一致
11|3D_Interconnect|Example: Thermoelectromechanical Analysis of an Interconnect (3D)|Training manual|mode mechanics current thermal|Applications_Library/GettingStarted/sinterconnect/3D_Interconnect|全流程跑通，输出一致
12|3D_Matrix_Calculation|Example: Electrostatic, Electrical, and Thermal Analyses (3D)|Training manual|mode capacitance; mode resistance; mode thermal.resistance|Applications_Library/GettingStarted/sinterconnect/3D_Matrix_Calculation|未开始
13|Inverter|Example: Inverter|Training manual|mode electrostatic|Applications_Library/GettingStarted/sinterconnect/Inverter|全流程跑通，输出一致
14|User_Fluid|Fluid Stress|客户|mode mechanics|/global/ae/tcad/eamon/STDB/work/CXMT/AA_Structure_demo_for_stress_simulation && /global/ae/tcad/eamon/STDB/work/CXMT/Fluid_Stress/Fluid_Stress_Kangkang_20231109|未开始
15|User_Cap|*Cap Layer Bending|客户|mode mechanics|/global/ae/tcad/eamon/STDB/work/CXMT/AA_Structure_demo_for_stress_simulation|未开始
16|User_Warpage|*Wafer Warpage|客户|mode mechanics|/global/ae/tcad/eamon/STDB/work/CXMT/Wafer_warpage|未开始
17|User_Line|Line Bending|客户|mode mechanics; mode buckling|/global/ae/tcad/eamon/STDB/work/CXMT/deformation20231208|未开始
18|User_TSV|*TSV Stress|客户|mode mechanics|/global/ae/tcad/eamon/STDB/work/CXMT/TSV_copper_20240222|全流程跑通，输出一致'''

# Columns: original row, category, feature, commands, reference, case aliases,
# development difficulty/time, mode, source completion, destination category.
feature_rows = r'''2|边界条件/载荷|力：点载荷 (pfx, pfy, pfz)|stressdata bc.location=pointend point.coord={0 0 0} bc.value={pfx=0 pfy=0 \\ pfz=@p@<dyn>}|p.112 Point-Force Boundary Condition|Cantilever|低|力|done|Boundary conditions & constraints
3|边界条件/载荷|力：指定点的迪利克雷边界条件 (pdx, pdy, pdz)|stressdata bc.location=<c> bc.value={pdx=<n> pdy=<n> pdz=<n>} point.coord={<n> <n> <n>}|p.113 Point-Displacement Rate Boundary Condition|Backend_CopperReliability,Backend_Thermomech,Backend_SolderReliability,User_Warpage|低|力|done|Boundary conditions & constraints
4|边界条件/载荷|力：指定面的迪利克雷边界条件 (dx, dy, dz)|stressdata bc.location=Bottom bc.value={dx=0 dy=0 dz=0}|p.107 Boundary Conditions|Cantilever,3D_Matrix_Calculation,Backend_CopperReliability,Backend_FlipChip,Backend_Thermomech,Backend_Stress,Backend_SolderReliability,User_Fluid,User_Cap,User_Line,User_TSV|低|力|done|Boundary conditions & constraints
5|边界条件/载荷|力：压力 (pressure)|stressdata bc.location=cont2 bc.value={pressure=50.0<MPa>}|p.111 Pressure Boundary Condition; p.694 stressdata|3D_Interconnect|低|力|done|Boundary conditions & constraints
6|边界条件/载荷|力：面载荷 (sx, sy, sz)|stressdata bc.location=Back bc.value={sx=0 sy=0 sz=0}|p.107 Boundary Conditions|Cantilever|低|力|ongoing|Boundary conditions & constraints
7|边界条件/载荷|力：迪利克雷边界条件支持消行消列|pdbSet Mechanics Boundary.Method.Type MatrixReduction|p.108 Boundary Conditions|Backend_FlipChip,Backend_CopperReliability|中|力|ongoing|Boundary conditions & constraints
8|边界条件/载荷|热：Bottom Boundary Condition|pdbSet <material> AttachThermalResistor 1\npdbSet WaferThickness <n>\npdbSet Env.Temp <n>|p.176 Bottom Boundary Condition|3D_Interconnect,Backend_SRAM,Backend_SRAMRounding|低|力|not started|Boundary & interface conditions
9|边界条件/载荷|热：温度边界条件|supply contact.name=tm0 temperature=100<C>|p.709 supply — Specifies a constant temperature supply.|Damascene,3D_Interconnect,Backend_SRAM,Backend_SRAMRounding|低|力|not started|Boundary & interface conditions
10|边界条件/载荷|电：voltage|supply contact.name=upper voltage=0.1<V>|p.709 supply — Specifies a constant voltage supply.|Damascene,3D_Interconnect,Inverter,Backend_SRAM,Backend_SRAMRounding|低|电|not started|Analysis modes
11|边界条件/载荷|边界条件/载荷支持 bc.location=<contact name>|stressdata bc.location=<c>|p.694 stressdata|3D_Interconnect,Cantilever,3D_Matrix_Calculation,Backend_CopperReliability,Backend_Thermomech,Backend_Stress,Backend_SolderReliability|低|通用|ongoing|Boundary conditions & constraints
12|边界条件/载荷|力：支反力输出|pdbSetBoolean Mechanics Save.Reaction.Force 1|p.107 Boundary Conditions||低|通用|ongoing|Boundary conditions & constraints
13|材料|力：塑性（各向同性、随动硬化）|pdbSetBoolean BumpMat Mechanics IsPlastic 1|p.82 Plastic Materials|Backend_CopperReliability,User_Warpage|中|力|done|Material models
14|材料|力：粘塑性|pdbSetBoolean BumpMat Mechanics IsViscoPlastic 1|p.86 Viscoplastic Materials|Backend_CopperReliability|高|力|not started|Material models
15|材料|力：绝对热膨胀系数与相对热膨胀系数切换|pdbSetDouble Mechanics RefThExpCoeff 0\nor\npdbSetDouble Mechanics RefThExpCoeff <n>|p.118 Thermal Mismatch|Backend_FlipChip,Backend_Thermomech,Backend_Stress|低|力|not started|Stress-causing mechanisms
16|材料|热：比热容、热导率、密度|pdbSet <material> MassDensity <n>\npdbSet <material> SpecificHeatCapacity <expression>\npdbSet <material> Temperature Conductivity <expression>|p.173 Thermal Analysis|Damascene,3D_Interconnect,Backend_SRAM,Backend_SRAMRounding|低|热|not started|Heat transfer & materials
17|材料|力：粘弹性|pdbSetDouble Pass Mechanics Viscosity0 1e40\npdbSetDouble Pass Mechanics ViscosityW 0.0|p.73 Viscoelastic Materials|Backend_FlipChip,Backend_CopperReliability,Backend_Stress,Backend_SolderReliability,User_Line,User_TSV|中|力|done|Material models
18|材料|电：电导率|pdbSetString Copper Potential Conductivity 5.9e5|p.17? Thermal Analysis（页码被指针遮挡）|Backend_SRAM,Backend_SRAMRounding|低|电|not started|Analysis modes
19|材料|基于 new.like 继承并创建新材料|mater add name=mat1 new.like=Silicon|p.47 Materials: Material Parameter Inheritance|Backend_FlipChip,Backend_CopperReliability,Backend_Thermomech,Backend_Stress,Backend_SolderReliability,Backend_SRAM,Backend_SRAMRounding,User_Fluid,User_Cap,User_Warpage,User_Line,User_TSV|中|通用|done|Material models
20|单元|力：二阶单元|pdbSetDouble Mechanics FiniteElementOrder 2|p.98 Second-Order Finite Element Analysis|Cantilever,Backend_FlipChip,Backend_CopperReliability,User_Fluid,User_Warpage,User_Line|中|力|not started|Element library
21|分析方法|力学分析|mode mechanics|p.71 Computing Mechanical Stress|Damascene,Cantilever,Backend_FlipChip,Backend_CopperReliability|低|力|done|Analysis methods
22|分析方法|力：收敛判据日志打印开关|pdbSet Mechanics Convergence.Info 1|p.409 Convergence Criteria|Backend_Thermomech|高|力|not started|Solver components
23|分析方法|力：牛顿迭代参数设置|pdbSet Mechanics MaxIterations 20\npdbSet Mechanics Convergence.Force.Tolerance 1e-3\npdbSet Mechanics Convergence.Energy.Tolerance 1e-3|p.409 Convergence Criteria|Backend_FlipChip,Backend_CopperReliability,Backend_Thermomech|高|力|done|Solver components
24|分析方法|力：submodel 技术|stressdata global.model=<c>\nor\npdbSet Mechanics Submodel <c>|p.148 Submodelling|Backend_FlipChip,Backend_Stress,Backend_SolderReliability,User_Warpage|高|力|ongoing|Boundary conditions & constraints
25|分析方法|力：液体表面张力|pdbSetDoubleArray WetFluid ContactAngle {Oxide @angle@}\npdbSetDoubleArray WetFluid SurfaceTension {Oxide 75}\npdbSetDoubleArray WetFluid AveragePressure {Oxide 1e9}|p.122 Effective Surface Tension and Pressure due to Fluid|User_Fluid|中|力|not started|Stress-causing mechanisms
26|分析方法|力：线性屈曲分析|mode buckling\npdbSetBoolean Mechanics ArcLength 0|p.128 Linear Buckling Analysis|User_Line|中|力|not started|Analysis methods
27|分析方法|力：非线性屈曲分析|mode buckling\npdbSetBoolean Mechanics ArcLength 1|p.130 Post-Buckling Analysis|User_Line|中|力|not started|Analysis methods
28|分析方法|力：几何非线性|pdbSetBoolean Mechanics LargeDeformation 1|p.103 Large Deformation Analysis|User_Line|高|力|not started|Nonlinearity
29|分析方法|力：追踪应力历史|pdbSet Mechanics StressHistory 1|p.126 Automated Tracing of Stress History|Damascene,Backend_Stress,User_Line|中|力|done|Analysis methods
30|分析方法|力：time step 控制|solve temperature=180.0<C> t.final=25.0<C> delNT=155.0 \\\ntime=1.0<s> init=1.0<s> maxstep=1.0<s>|p.406 Time-Step Control|Backend_FlipChip,Backend_CopperReliability,Backend_Thermomech,Backend_Stress,Backend_SolderReliability,User_Warpage|高|力|not started|Solver components
31|分析方法|力：计算主应力与主方向|pdbSet Mechanics Calculate.Principal.Stress 1\npdbSet Mechanics Calculate.Principal.Direction 1|p.145 Principal Stresses|Backend_FlipChip,Backend_CopperReliability,Backend_Thermomech,Backend_Stress,Backend_SolderReliability,User_Cap,User_Warpage,User_Line,User_TSV|低|力|not started|Post-processing & output
32|分析方法|力：追踪最大应力|pdbSet Mechanics SaveMaxStress 1|p.14? Tracking Maximum Stress（页码被指针遮挡）|Backend_FlipChip,Backend_CopperReliability,Backend_Stress,Backend_SolderReliability,User_Warpage,User_Line,User_TSV|中|力|not started|Post-processing & output
33|分析方法|传热分析|mode thermal|p.173 Thermal Analysis|Damascene,3D_Interconnect|中|热|not started|Heat transfer & materials
34|分析方法|静电分析|mode electrostatic|p.197 Electrostatic Analysis|Inverter|中|电|not started|Analysis modes
35|分析方法|电流分析|mode current|p.184 Electrical Current Analysis|Damascene|中|电|not started|Analysis modes
36|分析方法|热电耦合、焦耳热计算|pdbSet <material> Temperature JouleHeating 1\nmode current thermal|p.174 Thermal Model|3D_Interconnect,Backend_SRAM,Backend_SRAMRounding|中|热电|not started|Analysis modes
37|分析方法|三场耦合|mode mechanics current thermal|N/A|Damascene,3D_Interconnect,Backend_SRAM,Backend_SRAMRounding|高|力热电|not started|Analysis modes
38|分析方法|计算、打印 capacitance 矩阵|mode capacitance\nprintCapacitanceMatrix|p.749 Electrostatic Analysis: Capacitance Matrix; p.636 printCapacitanceMatrix; p.200 Capacitance Matrix|3D_Matrix_Calculation|中|电|not started|Analysis modes
39|分析方法|计算、打印 resistance 矩阵|mode resistance\nprintResistanceMatrix|p.757 Thermal Analysis: Thermal RC Network; p.640 printResistanceMatrix; p.193 Resistance Matrix|3D_Matrix_Calculation|中|电|not started|Analysis modes
40|分析方法|计算、打印 thermal resistance 矩阵|mode thermal.resistance\nprintThermalResistanceMatrix|p.755 Thermal Analysis: Thermal Resistance Matrix; p.644 printThermalResistanceMatrix|3D_Matrix_Calculation|中|热|not started|Heat transfer & materials
41|分析方法|Shape.Function.LinTriTet.Distance|pdbSetBoolean Mechanics Shape.Function.LinTriTet.Distance 1|N/A|Backend_Stress|高|力|not started|Element library
42|后处理|一维应力空间分布曲线|SetPlxList { StressEL_xx StressEL_yy StressEL_zz }\nWritePlx n@node@_via.plx y=0.04 z=0.35 Copper|p.682 SetPlxList; p.745 WritePlx|Damascene|中|力|not started|Post-processing & output
43|后处理|沿空间方向提取数据，生成 .plx 文件|select z="Displacement_z"\nplot.1d y=0 z=0|p.391 Selecting Fields for Viewing or Analysis; p.392 Obtaining 1D Data Cuts; p.614 plot.1d|Cantilever|中|通用|not started|Post-processing & output
44|后处理|变形可视化，支持变形系数|struct tdr=n@node@_def deform deform.scale=5.0|p.705 struct; p.591 option|Cantilever,Backend_Thermomech,User_Fluid,User_Cap,User_Warpage,User_Line|中|力|not started|Post-processing & output
45|后处理|支持 total displacement 与 step displacement|pdbSet Mechanics Save.Displacement.Field 1\npdbSet Mechanics Save.Total.Displacement 1\npdbSet Mechanics Save.Step.Displacement 1|p.166 Displacement Field|Backend_Thermomech,Backend_Stress,Backend_SolderReliability,User_Warpage,User_Line,User_TSV|中|力|not started|Post-processing & output
46|后处理|高斯点数据可视化|高斯点数据先内插为单元数据，然后按照单元数据的逻辑可视化|p.133 Description of Output Fields|Damascene,Cantilever,Backend_FlipChip,Backend_CopperReliability|中|力|not started|Post-processing & output
47|后处理|高斯点变量输出|StressGP、ElasticStrainGP 为力学分析的默认输出变量|p.127 Fields defined on Gauss points|Damascene,Cantilever,Backend_FlipChip,Backend_CopperReliability|中|力|not started|Post-processing & output
48|后处理|力：应变能密度计算与输出 ElasticEnergyDens、ElasticEnergyDensEL、ElasticEnergyDensGP|应变能密度为力学分析的默认输出变量|p.133 Description of Output Fields|Damascene,Cantilever,Backend_FlipChip,Backend_CopperReliability|中|力|not started|Post-processing & output
49|后处理|Stress-Induced Mobility Enhancement|pdbSetBoolean Mechanics Calculate.Mobility 1|p.165 Stress-Induced Mobility Enhancement|User_TSV|高|力|not started|Post-processing & output
50|几何/网格|支持更多的 transform 操作|transform translate|p.261 UseLines and the transform Command|Backend_FlipChip|中|通用|not started|Geometry & mesh
51|几何/网格|merge vertices|pdbSet Mechanics Merge.Vertices 1|N/A|Backend_FlipChip,Backend_CopperReliability|高|力|not started|Geometry & mesh
52|裂纹分析|裂纹分析|pdbSet Mechanics Model Crack|p.150 Crack Analysis|Backend_FlipChip,Backend_Thermomech|高|力|not startnot started|Nonlinearity
53|通用|场数据导出|SetTDRList {LatticeTemperature FinalTemp} !Solutions|p.683 SetTDRList|Backend_Thermomech|中|通用|not started|Post-processing & output
54|通用|tcl 脚本支持 Shell 命令|fexec rm -rf n@node@_2_sis.tdr|p.498 fexec|Backend_CopperReliability|中|通用|not started|Scripting & data exchange
55|通用|source 外部文件|source settings.cmd|N/A|Backend_Thermomech,User_Warpage|中|通用|done|Scripting & data exchange
56|通用|迭代法求解器开放接口|pdbSet Math Flow 3D ILS.method sts3\npdbSet Math Flow 3D ILS.tolrel 1e-3\npdbSetDouble Math Flow ILS.refine.residual 1e-3\npdbSet Math Flow 3D ILS.ilut.tau 1e-14\npdbSet Math Flow 3D ILS.scaling diagsym\npdbSet Math Flow 3D ILS.nonsymmOrdering none\npdbSet Math Flow 3D ILS.refine.sts 1\npdbSet Math Flow 3D ILS.leftPreconditioner 1|p.400 Setting Parameters of the Iterative Solver ILS|Backend_Thermomech,Backend_CopperReliability|中|通用|not started|Solver components
57|通用|全局温度设置|SetTemp <n>[<C>|<K>]|p.683 SetTemp|Backend_FlipChip,Backend_CopperReliability,Backend_Stress|中|热|done|Heat transfer & materials
58|通用|场数据导入|load tdr=<c> sum|p.62 Interpolating Field Data From an External Structure File Using Load Command; p.558 load|Backend_FlipChip,Backend_CopperReliability,Backend_Thermomech,Backend_Stress,Backend_SolderReliability|中|通用|not started|Scripting & data exchange
59|通用|tcl 脚本支持单位制|supply contact.name=<c> temperature=<n> [<C>|<K>]|N/A|all|中|通用|not started|Scripting & data exchange
60|通用|特征值求解器|mode buckling\npdbSetBoolean Mechanics ArcLength 0|p.128 Linear Buckling Analysis|User_Line|中|通用|not started|Solver components'''

def image_for_feature(n):
    return '466' if n <= 8 else '465' if n <= 22 else '464' if n <= 37 else '463' if n <= 49 else '462'

cases = []
for line in case_rows.splitlines():
    n, alias, name, origin, mode, path, status = line.split('|')
    cases.append(dict(row=int(n), alias=alias, name=name, origin=origin, mode=mode, path=path,
                      source_status=status, screenshot='468' if int(n)<=5 else '467' if int(n)<=13 else '466'))
cases[2]['notes'] = '原表附文：Backend_Thermomech 功率半导体封装过程的可靠性分析（热固耦合分析）Thermomechanical Reliability'
cases[7]['notes'] = '原表重复列出英文标题，并附：倒装芯片凸点热疲劳寿命 - 工艺器件模拟处 - Confluence Production'
cases[13]['notes'] = '原表附文：User_Fluid AA Bridge中的液体表面张力 - 工艺器件模拟处 - Confluence Production'
for c in cases[:8]:
    c['status_note'] = '原图状态列为跨行合并单元格：未开始。'
features = []
for line in feature_rows.splitlines():
    # Unit alternatives contain vertical bars, so protect those literal cells.
    line = line.replace('[<C>|<K>]', '[<C>／<K>]')
    n, category, name, commands, reference, aliases, difficulty, mode, status, destination = line.split('|')
    features.append(dict(row=int(n), original_category=category, name=name,
                         commands=re.sub(r'\\{2,}', lambda _: '\\', commands.replace('\\n','\n')).replace('[<C>／<K>]', '[<C>|<K>]'),
                         reference=reference, case_aliases=aliases.split(',') if aliases else [],
                         difficulty=difficulty, mode=mode, source_status=status, category=destination,
                         screenshot=image_for_feature(int(n))))
payload = dict(title='GT例子库、客户案例功能梳理',
    source_notes=['Backend基于真实场景，是解决具体问题的完整计算案例；',
                  'TrainingManual是简单案例，用于功能演示；',
                  '客户案例 /meda_tcad/sharefolder/0775/SI_user_examples/'],
    source_url='http://conf.amedac.com/pages/viewpage.action?pageId=96304158',
    cases=cases, features=features,
    transcription_notes=['原表功能第1行是标题；实际功能编号2–60。',
                         '第18、32行手册页码被鼠标遮挡，保留可辨部分并附原图，不猜测数字。',
                         '第8、9行原表mode为“力”，照录；第52行状态原文“not startnot started”照录。',
                         '原表状态与现有目录状态分别保存。'])
(ROOT/'source-table-data.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Transcribed {len(cases)} cases and {len(features)} feature rows')
