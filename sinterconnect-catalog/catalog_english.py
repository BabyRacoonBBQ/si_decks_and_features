"""English presentation translations; original source records stay unchanged."""
FEATURE_NAMES = '''Point-force boundary conditions
Point-displacement rate boundary conditions
Prescribed surface displacement
Pressure boundary conditions
Surface traction
Dirichlet boundary matrix reduction
Bottom thermal boundary condition
Prescribed temperature boundary
Voltage supply
Contact-name boundary selection
Reaction-force output
Plasticity: isotropic and kinematic hardening
Viscoplasticity
Absolute / relative thermal expansion coefficients
Specific heat, thermal conductivity and density
Viscoelasticity
Electrical conductivity
Material inheritance with new.like
Second-order finite elements
Mechanical analysis
Convergence diagnostic output
Newton iteration parameters
Mechanical submodeling
Fluid surface tension and pressure
Linear buckling analysis
Post-buckling analysis
Geometric nonlinearity
Stress-history tracking
Time-step control
Principal stresses and directions
Maximum-stress tracking
Thermal analysis
Electrostatic analysis
Electrical current analysis
Electrothermal coupling and Joule heating
Thermoelectromechanical coupling
Capacitance matrix calculation and output
Resistance matrix calculation and output
Thermal resistance matrix calculation and output
Shape.Function.LinTriTet.Distance
One-dimensional stress profiles
Spatial data extraction to PLX
Deformation visualization and scale factor
Total and step displacement output
Gauss-point data visualization
Gauss-point variable output
Elastic strain-energy density output
Stress-induced mobility enhancement
Geometry translation
Merge vertices
Crack analysis
Field-data export
Shell commands from Tcl
External Tcl source files
Iterative solver configuration
Global temperature setting
Field-data import
Units in Tcl commands
Eigenvalue solver'''.splitlines()

WORDS = {'边界条件/载荷':'Boundary conditions / loads','材料':'Materials','单元':'Elements',
         '分析方法':'Analysis methods','后处理':'Post-processing','几何/网格':'Geometry / mesh',
         '裂纹分析':'Crack analysis','通用':'General','客户':'Customer','力':'Mechanics','热':'Thermal',
         '电':'Electrical','热电':'Electrothermal','力热电':'Thermoelectromechanical',
         '低':'Low','中':'Medium','高':'High','未开始':'Not started',
         '全流程跑通，输出一致':'Full workflow completed; matching output',
         '用户案例':'User case','改编案例':'Adapted case','自建 feature deck':'Purpose-built feature deck',
         '来源待核对':'Source pending confirmation'}

CASE_TEXT = {
'tsv':dict(source='Original user case: photographs converted to CMD by OCR and manually corrected; the user confirmed the original-version identity.',
adapt='The OCR-converted directory is the original input. The repository integrates a mesh-simplified version. cmd_flat and cmd organize the same inputs differently; they are not the original and simplified versions.',
original='D:/WORK/qx_deck/SI/tsv_stress/cmd_flat/; cmd/ contains categorized copies; ocr_clean/photo_to_cmd_manifest.csv traces photographs to CMD files.',
cmd=['Geometry: n5..n11_dvs.cmd (7 files)','Material / mesh preprocessing: n19..n25_sis.cmd (7 files)','Thermomechanical solution: n40..n46_sis.cmd (7 files)','Corresponding pp* copies: 21 files; common templates / execution graph: 4 files'],
flow='Photographs → OCR / correction → 7 original chains × 3 stages → repository mesh-simplified version → verification workflow',
verify='Integrated (confirmed by user)',note='The original verify_in_vm.sh performs vendor syntax checks only: 28 expanded files plus one expanded template. The user confirmed integration of the simplified version; repository paths, verification entry point and current results remain to be checked.',
feature='TSV thermal stress · temperature history · material / mesh preprocessing · fixed displacement and directional constraints'),
'backend':dict(source='Backend / Package_ThermomechanicalReliability; archived as a PowerSO-10RF / LDMOS adaptation.',
adapt='Geometry, materials and solution flow were adapted. The benchmark separates thermal and mechanical solution entry points.',
flow='Geometry / mesh.tdr → thermal_bench.cmd → temperature output → mechanics_bench.cmd',
verify='Standalone validation recorded; regression integration pending confirmation',
note='The two solution CMD files run sequentially. Geometry generation is an additional prerequisite. Four-step mechanics, 400 K, initial-temperature and parameter-error checks are variants of this case.',
feature='Steady-state heat transfer · conduction / convection / radiation · thermal expansion · thermal stress'),
'submodel':dict(source='Adapted from part of an existing case (confirmed by user); the exact parent-case mapping remains to be checked.',
adapt='The workflow targets global displacement mapping onto a refined single-pillar mesh. It is an adaptation, not an independently invented case.',
original='Candidate source: original/submodel-candidates/PackageAssembly_Stress/*; vendor-original.cmd is also archived, but this does not establish direct derivation.',
flow='Global geometry / mesh → global.cmd → global displacement → unit-fine.cmd → local stress',
verify='Standalone validation recorded; regression integration pending confirmation',
note='The two solution CMD files have a data dependency. Frozen-mesh variants are global-freeze.cmd / unit-fine-freeze.cmd. Temperature is a prescribed cooling load, not a heat-conduction solution.',
feature='Global-to-local displacement mapping · local refinement · mechanical constraints'),
'quasistatic':dict(source='Purpose-built feature case (confirmed by user), with no direct external reference case.',
adapt='The same model produces 16 frames with different loads. These form one case series, not 16 independent features.',
original='Purpose-built baseline; the archived vendor-reference-cantilever.cmd is a separately retained reference, without a confirmed derivation relationship.',
flow='setup.py / refine.py → shared mesh → case.cmd for each frame',
verify='Run records available; regression integration pending confirmation',
note='The 16 CMD files are parameter variants, not a sequential 01→16 result chain. An arch-quasistatic variant is also retained.',feature='Quasistatic equilibrium · displacement / stress output'),
'buckling':dict(source='Archived feature demonstration deck; original provenance remains to be checked.',
adapt='The main case is retained separately from plate-buckling and arch-linear. Three and six modes are solver-configuration variants.',
original='linear-buckling/case.cmd (archived baseline)',flow='Mesh preparation → case.cmd → eigenvalues / buckling modes / TDR',
verify='Standalone validation recorded; regression integration pending confirmation',
note='One main solution CMD. Recorded ARPACK-call validation does not establish validation of every buckling variant.',feature='Linear buckling · ARPACK · eigenvalue and mode output'),
'postbuckling':dict(source='Archived feature demonstration series; direct provenance remains to be checked.',
adapt='Supercritical is the main case; post-buckling is an earlier subcritical calibration, and arch-snap is a separate variant.',
flow='Mesh preparation → main case.cmd',verify='Archive available; regression integration pending confirmation',
note='The directories contain independent variants, not multiple CMD files forming one pipeline. Complete passing status has not been confirmed.',feature='Post-buckling response · nonlinear solution path'),
'deformation':dict(source='Archived feature demonstration series; direct provenance remains to be checked.',
adapt='Paired geometric-nonlinearity OFF / ON comparison; v2 is the entry point designated by the archive documentation.',
original='Original geometric-off/on versions and v2 are both retained.',flow='Shared geometry / mesh → separate OFF and ON solutions → comparison',
verify='Deferred in this round',note='The two CMD files are paired runs, not sequentially dependent. The user explicitly deferred large-deformation validation.',feature='Geometric nonlinearity · large deformation / rotation')}

SOURCE_CASE_NOTES = {
3:'Additional source caption: Backend_Thermomech — reliability analysis of power-semiconductor packaging (thermomechanical coupling); Thermomechanical Reliability.',
8:'The source repeats the English title and includes a link caption for flip-chip bump thermal fatigue life — Process and Device Simulation — Confluence Production.',
14:'Additional source caption: User_Fluid — fluid surface tension in an AA Bridge — Process and Device Simulation — Confluence Production.'}

def english_feature(row):
    f = dict(row)
    f['name'] = FEATURE_NAMES[f['row']-2]
    for k in ['original_category','mode','difficulty','source_status']:
        f[k] = WORDS.get(f[k],f[k])
    f['reference'] = f['reference'].replace('（页码被指针遮挡）',' (page number obscured by the pointer)')
    commands={46:'Interpolate Gauss-point data to element data, then visualize it using the element-data workflow.',
              47:'StressGP and ElasticStrainGP are default mechanical-analysis output variables.',
              48:'Strain-energy density is a default mechanical-analysis output variable.'}
    f['commands']=commands.get(f['row'],f['commands'])
    return f
