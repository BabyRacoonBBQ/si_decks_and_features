from pathlib import Path
import html, json, zipfile, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
esc = html.escape
cases = [
 dict(id='tsv',name='TSV',kind='用户案例',source='User case（用户确认）',adapt='集成到验证流程的是网格简化版本；保留原始版与简化版的身份区别。',original='用户原始 TSV deck：本机路径待补',cmd=['网格简化版 CMD 名称待补'],flow='原始 user case → 网格简化 → 验证流程',verify='已集成（用户确认）',note='verify 脚本名、CMD 数量、网格规模和版本差异待核对。',feature='TSV 场景；具体求解 feature 待读取 deck',archive=None),
 dict(id='backend',name='Backend / Package reliability',kind='改编案例',source='Backend · Package_ThermomechanicalReliability；归档记录为 PowerSO-10RF / LDMOS 改编',adapt='几何、材料与求解流程经过 adaptation；benchmark 将热与力学拆成两个求解入口。',original='benchmark-golden/original-case/dpack_struct_sis.cmd',cmd=['benchmark-golden/package/thermal_bench.cmd','benchmark-golden/package/mechanics_bench.cmd'],flow='几何 / mesh.tdr → thermal_bench.cmd → 温度输出 → mechanics_bench.cmd',verify='独立验证有记录；verify 集成待核对',note='两个求解 CMD 顺序执行；几何生成是额外前置步骤。四步力学、400 K、初温及参数错误属于此案例的变体。',feature='稳态传热 · 导热 / 对流 / 辐射 · 热膨胀 · 热应力',archive='01_Package_reliability.zip'),
 dict(id='submodel',name='Submodeling',kind='改编案例',source='从已有案例的一部分提取改编（用户确认）；精确父案例映射待核对',adapt='针对全局位移映射到单柱细网格的 feature 建立验证流程；不能标为完全无来源的自建案例。',original='候选来源：original/submodel-candidates/PackageAssembly_Stress/*；归档同时有 vendor-original.cmd，尚不等于已证明直接派生关系',cmd=['benchmark-golden/pillar/inputs/global.cmd','benchmark-golden/pillar/inputs/unit-fine.cmd'],flow='全局几何 / 网格 → global.cmd → 全局位移 → unit-fine.cmd → 局部应力',verify='独立验证有记录；verify 集成待核对',note='两个求解 CMD 存在数据依赖。冻结网格版本另有 global-freeze.cmd / unit-fine-freeze.cmd。温度是指定冷却载荷，不是热传导求解。',feature='Global-to-local displacement mapping · 局部细化 · 机械约束',archive='02_Submodelling.zip'),
 dict(id='quasistatic',name='Quasistatic equilibrium',kind='自建 feature deck',source='针对功能自行建立（用户确认）；无直接外部参考案例',adapt='同一模型按加载量形成 16 个 frame；这是一个案例系列，不是 16 个独立 feature。',original='自建基线；归档中的 vendor-reference-cantilever.cmd 仅作为另存参考，未确认派生关系',cmd=['quasistatic/frame-01/case.cmd … frame-16/case.cmd'],flow='setup.py / refine.py → 共享网格 → 各 frame 的 case.cmd',verify='运行记录存在；verify 集成待核对',note='16 个 CMD 是参数变体，不表示按 01→16 串行传递结果。另有 arch-quasistatic 变体。',feature='准静态平衡 · 位移 / 应力输出',archive='03_Quasistatic_equilibrium.zip'),
 dict(id='buckling',name='Linear buckling',kind='来源待核对',source='归档有功能演示 deck；原始来源待核对',adapt='主案例与 plate-buckling、arch-linear 分开保留；3 / 6 模态是求解配置变体。',original='linear-buckling/case.cmd（归档基线）',cmd=['linear-buckling/case.cmd'],flow='网格准备 → case.cmd → 特征值 / 屈曲模态 / TDR',verify='独立验证有记录；verify 集成待核对',note='单个主求解 CMD。实际 ARPACK 调用验证记录不代表所有屈曲变体都已验证。',feature='线性屈曲 · ARPACK · 特征值与模态输出',archive='04_Linear_buckling.zip'),
 dict(id='postbuckling',name='Post-buckling',kind='来源待核对',source='归档功能演示系列；直接来源待核对',adapt='supercritical 是主案例；post-buckling 是早期亚临界标定，arch-snap 是另一变体。',original='post-buckling-supercritical/case.cmd',cmd=['post-buckling-supercritical/case.cmd'],flow='网格准备 → 主案例 case.cmd',verify='归档存在；verify 集成待核对',note='不同目录是独立变体，不是多个 CMD 共同构成一条流水线。当前完整通过状态未确认。',feature='屈曲后响应 · 非线性路径',archive='05_Post_buckling.zip'),
 dict(id='deformation',name='Large deformation',kind='来源待核对',source='归档功能演示系列；直接来源待核对',adapt='几何非线性关闭 / 开启的配对比较；v2 是归档说明指定入口。',original='geometric-off/on 原始版本与 v2 均保留',cmd=['geometric-off-v2/case.cmd','geometric-on-v2/case.cmd'],flow='共享几何 / 网格 → OFF 与 ON 分别求解 → 比较',verify='本轮暂缓',note='两个 CMD 是配对运行，不是顺序数据依赖。用户已明确暂不做大变形验证。',feature='几何非线性 · 大变形 / 转动',archive='06_Large_deformation.zip')
]
TSV = Path('D:/WORK/qx_deck/SI/tsv_stress')
cases[0].update(
 source='用户原始案例：照片经 OCR 转换、人工校正为 CMD（用户确认原始版本身份）',
 original='D:/WORK/qx_deck/SI/tsv_stress/cmd_flat/；cmd/ 为分类副本；ocr_clean/photo_to_cmd_manifest.csv 提供照片到 CMD 的追溯',
 adapt='本目录 OCR 转换版是原始版本；代码仓库中集成的是网格简化版。cmd_flat 与 cmd 是同一组输入的两种组织方式，不是简化前后两个版本。',
 cmd=['几何：n5..n11_dvs.cmd（7 个）','材料 / 网格预处理：n19..n25_sis.cmd（7 个）','热应力求解：n40..n46_sis.cmd（7 个）','对应 pp* 副本：21 个；common 模板 / 执行图：4 个'],
 flow='照片 → OCR / 校正 → 原始 7 组 × 3 阶段链路 → 仓库网格简化版 → verify 流程',
 note='原始目录 verify_in_vm.sh 仅做 vendor 语法检查：28 个展开文件 + 1 个展开模板。仓库简化版已集成（用户确认），具体仓库路径、verify 入口及当前结果仍待核对。',
 feature='TSV 热应力 · 温度历程 · 材料 / 网格预处理 · 固定位移及方向约束')
modules = [
 ('Mechanics','LCA','Analysis methods', [('Quasistatic equilibrium','LCA','quasistatic'),('Linear buckling','TODO','buckling'),('Post-buckling','TODO','postbuckling')]),
 ('Mechanics','LCA','Material models',[(x,s,'backend' if x.startswith('Elastic') else '') for x,s in [('Elastic · isotropic / anisotropic','LCA'),('Viscous & viscoelastic','LCA'),('Plastic & viscoplastic','Alpha'),('Power-law creep','Prototype'),('Swelling','Prototype'),('Cohesive damage / softening','Prototype'),('Temperature-dependent parameters','LCA')]]),
 ('Mechanics','LCA','Element library',[(x,s,'') for x,s in [('Plane strain · 3D solid','LCA'),('Plane stress','TODO'),('Axisymmetric','TODO'),('Composite solid shell','Alpha'),('3D Timoshenko composite beam','TODO'),('First / second order','LCA'),('Mixed mesh','TODO')]]),
 ('Mechanics','LCA','Stress-causing mechanisms',[(x,s,'backend' if x.startswith('Thermal') else '') for x,s in [('Thermal mismatch · intrinsic stress','LCA'),('Densification · grain growth','TODO'),('Gravity force','Prototype'),('Surface reflow · edge dislocation','TODO'),('Inverse piezoelectric effect','TODO'),('Fluid surface tension / pressure','TODO'),('Cohesive zipping · phase change','TODO'),('Etch / deposition stress rebalancing','LCA')]]),
 ('Mechanics','LCA','Nonlinearity & boundaries',[(x,s,c) for x,s,c in [('Geometric nonlinearity','LCA','deformation'),('Mechanical contact · crack analysis','TODO',''),('Prescribed displacement / rate · traction · pressure · point force','LCA','submodel'),('Moment · symmetry · periodic boundary','Alpha',''),('Coupling · beam-plate coupling · variable boundary','Alpha','')]]),
 ('Thermal','Alpha','Heat transfer & materials',[(x,'Alpha','backend' if x.startswith('Conduction') else '') for x in ['Steady-state · transient','Conduction · convection · radiation','Conductivity · heat storage · emissivity','Temperature-dependent parameters','Applied heating · electrical heating']]),
 ('Thermal','Alpha','Boundary & interface conditions',[(x,s,'') for x,s in [('Prescribed temperature · ramps · heat flux · contact power','Alpha'),('Adiabatic · convection · radiation','Alpha'),('Thermal resistor','Prototype'),('Temperature / flux continuity','Prototype'),('Interface thermal resistance','Prototype')]]),
 ('Coupled / Electrical','','Analysis modes',[('Thermomechanical','Alpha','backend'),('Electrical current · electrostatic','TODO',''),('Electrothermal','TODO',''),('Electromechanical','TODO','')]),
 ('Numerics','','Solver components',[(x,'','buckling' if 'ARPACK' in x else '') for x in ['FEM mechanics · FVM thermal / electrical','TRBDF · Newton · direct / iterative solvers','ARPACK / MUMPS recovery: see linear buckling']])
]

css='''*{box-sizing:border-box}body{margin:0;background:#f3f5f8;color:#182b3c;font:15px/1.6 "Segoe UI","Microsoft YaHei",sans-serif}nav{background:#152d3e;color:white;padding:18px 5%;display:flex;gap:28px;align-items:center}nav strong{margin-right:auto;font-size:18px}nav a{color:#bfe5e5;text-decoration:none}main{max-width:1440px;margin:auto;padding:42px 4%}h1{font-size:42px;line-height:1.2;margin:8px 0 14px}h2{font-size:22px;margin:5px 0 14px}h3{font-size:18px;margin:0 0 12px}.eyebrow{letter-spacing:2px;color:#167a80;font-size:12px;font-weight:700}.lead{color:#536678;max-width:1000px}.notice{border-left:3px solid #d69a39;background:#fff8e9;padding:13px 18px;margin:22px 0}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.card{background:white;border:1px solid #dce3ea;border-radius:12px;padding:24px;min-width:0}.card small{color:#647689}.row{display:flex;gap:12px;align-items:start;padding:9px 0;border-top:1px solid #edf0f4}.row span:first-child{flex:1}.badge{font-size:11px;white-space:nowrap;border-radius:5px;padding:2px 8px;background:#e9edf3;color:#526072;display:inline-block}.lca{background:#d7efea;color:#176a63}.alpha{background:#fff0d7;color:#986016}.prototype,.todo{background:#ede6f6;color:#715598}a{color:#087e8a}.sub{font-size:12px;color:#6d7d8c}.case{margin:20px 0;scroll-margin:20px}.case-head{display:flex;align-items:center;gap:14px;margin-bottom:14px}.case-head h2{margin:0;flex:1}.columns{display:grid;grid-template-columns:1fr 1fr;gap:28px}.label{color:#6c7f8e;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-top:12px}p{margin:5px 0 12px}code{font-family:Consolas,monospace;font-size:12px;overflow-wrap:anywhere}.flow{padding:14px;background:#eef6f7;border-radius:6px;color:#27656c;margin-top:15px}.toolbar{display:flex;gap:12px;margin:26px 0;flex-wrap:wrap}input,select{border:1px solid #ccd7df;padding:12px;border-radius:6px;background:white;font:inherit}input{flex:1;min-width:240px}table{width:100%;border-collapse:collapse;background:white}td,th{text-align:left;padding:12px;border-bottom:1px solid #e3e9ef;vertical-align:top}th{background:#e8eff3}.count{font-size:13px;color:#617787}details{margin-top:15px}summary{cursor:pointer;color:#127985}.paths{max-height:260px;overflow:auto}.paths div{padding:3px}footer{padding:30px 0;color:#6c7f8e;font-size:12px}button{cursor:pointer} @media(max-width:900px){.grid{grid-template-columns:1fr 1fr}.columns{grid-template-columns:1fr}h1{font-size:32px}}@media(max-width:600px){.grid{grid-template-columns:1fr}nav{flex-wrap:wrap}.case-head{flex-wrap:wrap}}@media print{nav,.toolbar{display:none}main{padding:10px}.card{break-inside:avoid}.paths{max-height:none}body{background:white}}'''
def badge(s): return f'<span class="badge {s.lower()}">{esc(s)}</span>' if s else ''
def shell(title,body): return f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · SInterconnect</title><style>{css}</style><nav><strong>SInterconnect / Engineering catalog</strong><a href="index.html">Features</a><a href="test-cases.html">Test cases</a></nav><main>{body}</main></html>'

cards=''
for module,overall,title,rows in modules:
 content=''
 for name,status,case in rows:
  link=f'<br><a class="sub" href="test-cases.html#{case}">关联案例 →</a>' if case else ''
  content+=f'<div class="row"><span>{esc(name)}{link}</span>{badge(status)}</div>'
 cards+=f'<article class="card"><small>{module} {badge(overall)}</small><h3>{title}</h3>{content}</article>'
body='<div class="eyebrow">CAPABILITY INVENTORY</div><h1>Features</h1><p class="lead">按物理模块整理能力与案例关联。开发阶段和测试通过状态分别记录。</p><div class="notice">开发标签来自当前本机 PPT 第 1–3 页，保留 TODO / Prototype / Alpha / LCA 原标注；它们不代表当前代码验证结论。案例关联表示测试意图，不表示整个 feature 已通过。</div><div class="grid">'+cards+'</div>'
(ROOT/'index.html').write_text(shell('Features',body),encoding='utf-8')
case_html=''
inventory={}
for c in cases:
 paths=[]
 extra=''
 if c['id']=='tsv':
  import hashlib
  paths=sorted(p.relative_to(TSV).as_posix() for p in (TSV/'cmd').rglob('*.cmd'))
  assert len(paths)==46
  for rel in paths:
   p=TSV/rel
   assert p.read_bytes()==(TSV/'cmd_flat'/p.name).read_bytes(),p.name
  for p in (TSV/'cmd').rglob('n*.cmd'):
   assert p.read_bytes()==p.with_name('pp'+p.name[1:]).read_bytes(),p.name
  c['source_files']=[{'path':str(TSV/rel),'sha256':hashlib.sha256((TSV/rel).read_bytes()).hexdigest()} for rel in paths]
  rows=''.join(f'<tr><td>{i+1}</td><td><code>n{i+5}_dvs.cmd</code></td><td><code>n{i+19}_sis.cmd</code></td><td><code>n{i+40}_sis.cmd</code></td></tr>' for i in range(7))
  extra='<h3 style="margin-top:20px">原始版本：7 组多 CMD 链路</h3><table><thead><tr><th>参数组</th><th>① SDE 几何</th><th>② 材料 / 网格预处理</th><th>③ 热应力求解</th></tr></thead><tbody>'+rows+'</tbody></table><p class="sub">46 个 CMD = 21 个 n* + 21 个 pp* + 4 个 common 文件。已逐字节核对 n / pp 对应文件及 cmd / cmd_flat 副本一致；重复副本不增加案例数量。</p><div class="notice"><b>原始版历史执行记录，不代表仓库简化版：</b>28 个展开 Interconnect 文件及 1 个展开模板通过语法检查；7 个唯一 SDE 几何生成成功。代表链路 n5 → n19 → n40 中，n19 约 16 分 51 秒，网格 1,005,445 点 / 6,022,785 单元；n40 进入力学求解后因内存不足退出，未生成结果 TDR。以上来自 VM_VERIFICATION.md，本轮未重跑。</div><p class="sub">本机证据：<a href="file:///D:/WORK/qx_deck/SI/tsv_stress/README_整理说明.md">原始输入说明</a> · <a href="file:///D:/WORK/qx_deck/SI/tsv_stress/VM_VERIFICATION.md">历史验证报告</a> · <a href="file:///D:/WORK/qx_deck/SI/tsv_stress/verify_in_vm.sh">原始版语法检查脚本</a></p>'
 if c['archive']:
  with zipfile.ZipFile(BASE/'Resources/case-archive'/c['archive']) as z:
   paths=[n for n in z.namelist() if n.endswith('.cmd')]
 inventory[c['id']]=paths
 pathlist=''.join(f'<div><code>{esc(p)}</code></div>' for p in paths)
 archive=f'<a href="../Resources/case-archive/{c["archive"]}">归档 ZIP ↗</a>' if c['archive'] else '<a href="file:///D:/WORK/qx_deck/SI/tsv_stress/cmd_flat/">OCR 原始 CMD 目录 ↗</a>'
 commands=''.join(f'<li><code>{esc(cmd)}</code></li>' for cmd in c['cmd'])
 case_html+=f'''<article class="card case" id="{c['id']}" data-kind="{c['kind']}"><div class="case-head"><h2>{c['name']}</h2>{badge(c['kind'])}</div><div class="columns"><div><div class="label">Original / 原始来源</div><p>{esc(c['source'])}</p><code>{esc(c['original'])}</code><div class="label">Adaptation / 执行版本</div><p>{esc(c['adapt'])}</p><div class="label">Feature</div><p>{esc(c['feature'])}</p></div><div><div class="label">CMD composition / 主求解入口</div><ol>{commands}</ol><div class="label">Verify integration</div><p><b>{esc(c['verify'])}</b></p><p class="sub">{esc(c['note'])}</p>{archive}</div></div><div class="flow">{esc(c['flow'])}</div>{extra}<details><summary>已核实 CMD 路径（{len(paths)} 个实体条目；含历史副本，不等于案例数）</summary><div class="paths">{pathlist or '待补 TSV 原始与简化版本路径。'}</div></details></article>'''
body='''<div class="eyebrow">PROVENANCE & EXECUTION</div><h1>Test cases</h1><p class="lead">原始来源 → 改编版本 → CMD 组成 → 验证流程。应用案例、参数变体和历史运行副本分开记录。</p><div class="notice">已确认 6 类本机归档，另补入用户确认的 TSV。TSV 简化版已集成；其他案例的当前 verify 脚本映射尚待读取仓库核对。下面不将“有运行记录”视为“已纳入 verify”。</div><table><thead><tr><th>来源类别</th><th>案例</th><th>执行版说明</th></tr></thead><tbody><tr><td>用户原始案例</td><td>TSV</td><td>verify 使用网格简化版本，区别于原始输入</td></tr><tr><td>原案例改编</td><td>Backend · Submodeling</td><td>分别记录 adaptation；Submodeling 提取了原案例的一部分</td></tr><tr><td>自建 feature deck</td><td>Quasistatic</td><td>针对功能建立，无直接外部参考来源</td></tr><tr><td>来源待核对</td><td>Linear buckling · Post-buckling · Large deformation</td><td>存在归档输入；不推断其来源</td></tr></tbody></table><div class="toolbar"><input id="search" aria-label="搜索案例" placeholder="搜索案例、feature、CMD 或来源…"><select id="kind" aria-label="来源筛选"><option value="">全部来源</option><option>用户案例</option><option>改编案例</option><option>自建 feature deck</option><option>来源待核对</option></select></div><p class="count" id="count">7 个案例系列</p>'''+case_html+'''<article class="card"><h2>补充功能检查</h2><p>SetTemp 参数 / history、温度 profile 错误、功率密度转换、buckling 非整数 / 零模态等属于功能检查；独立脚本和 verify 映射待补，暂不计作新的应用案例。</p><p class="sub">证据入口：<a href="../Resources/case-archive/README.md">归档说明</a> · <a href="../Resources/case-archive/CASE-HANDOFF-thermomechanical.md">历史 handoff</a> · <a href="catalog-data.json">结构化清单</a></p></article><script>const search=document.querySelector('#search'),kind=document.querySelector('#kind');function filter(){let count=0;document.querySelectorAll('.case').forEach(c=>{const show=(!kind.value||c.dataset.kind===kind.value)&&c.textContent.toLowerCase().includes(search.value.toLowerCase());c.hidden=!show;if(show)count++});document.querySelector('#count').textContent=count+' 个案例系列'}search.addEventListener('input',filter);kind.addEventListener('change',filter);</script>'''
(ROOT/'test-cases.html').write_text(shell('Test cases',body),encoding='utf-8')
(ROOT/'catalog-data.json').write_text(json.dumps({'scope':'Local archive inventory; current remote verify mappings unverified','cases':cases,'archive_cmd_entries':inventory},ensure_ascii=False,indent=2),encoding='utf-8')
print('Created index.html, test-cases.html and catalog-data.json')
from build_feature_pages import render_features
render_features(modules, cases, badge, shell)
from build_case_pages import render_case_pages
render_case_pages(cases, shell)
from build_source_catalog import render_source_catalog
render_source_catalog()
