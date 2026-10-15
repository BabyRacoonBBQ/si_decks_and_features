"""DualDamascene report: process stress history and the operating response."""
from html import escape as E
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
ASSETS = 'assets/case-reports/damascene'
# The catalog uses these same identities for the reverse case associations.
FEATURE_IDS = ('stress-history', 'etch-stress-rebalancing',
               'deposition-stress-rebalancing', 'field-visualization')

CSS = '''
.case-report{margin-top:28px}.case-report .report-intro{font-size:19px;max-width:1000px;color:#415b70}
.case-report .report-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:24px 0}
.case-report .report-stat{background:white;border:1px solid #d5dfe8;border-radius:10px;padding:18px}.case-report .report-stat b{display:block;font-size:24px;color:#125f69}.case-report .report-stat span{font-size:12px;color:#607486}
.case-report .report-toc{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0 32px}.case-report .report-toc a{padding:7px 12px;background:white;border:1px solid #d5dfe8;border-radius:6px;text-decoration:none;font-size:13px}
.case-report .report-section{margin:38px 0;scroll-margin-top:24px}.case-report .report-section>h2{font-size:25px;border-bottom:1px solid #cfdae3;padding-bottom:10px;margin-bottom:20px}
.case-report figure{margin:20px 0;background:white;border:1px solid #d5dfe8;border-radius:10px;padding:16px;min-width:0}.case-report figure img{width:100%;height:auto;display:block}.case-report figcaption{font-size:13px;color:#506b7e;margin-top:14px;line-height:1.65}
.case-report .table-wrap{overflow-x:auto;border:1px solid #dce3ea;border-radius:8px;margin:16px 0}.case-report table{font-size:14px}.case-report th{white-space:normal}.case-report td{min-width:110px}.case-report td:first-child{min-width:130px;font-weight:600}
.case-report .equations{font:19px/1.9 Georgia,"Cambria Math",serif;background:#e9f2f5;border-radius:8px;padding:16px 22px;margin:18px 0}
.case-report .process-flow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:24px 0}.case-report .process-step{background:#e9f2f5;border-top:4px solid #568a93;padding:18px;border-radius:6px}.case-report .process-step b{display:block;margin-bottom:8px;color:#1a5566}.case-report .process-step p{margin:0;font-size:14px}
@media(max-width:850px){.case-report .report-stats{grid-template-columns:1fr 1fr}.case-report .process-flow{grid-template-columns:1fr}}
@media(max-width:500px){.case-report .report-stat b{font-size:21px}.case-report figure{padding:8px}.case-report .report-section>h2{font-size:22px}}
@media print{.case-report .report-toc{display:none}.case-report figure{break-inside:avoid}.case-report .table-wrap{overflow:visible}}
'''


def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join(
        f'<th scope="col">{E(h)}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def figure(name, alt, caption):
    return (f'<figure><a href="{ASSETS}/{name}.svg" target="_blank" rel="noopener">'
            f'<img src="{ASSETS}/{name}.png" alt="{E(alt)}" loading="lazy"></a>'
            f'<figcaption>{caption}</figcaption></figure>')


def feature_link(features, identity, detail=None):
    found = [f for f in features if f['id'] == identity]
    if len(found) != 1:
        raise ValueError(f'Expected one canonical feature for {identity}')
    f = found[0]
    if detail is not None and detail not in f['details']:
        raise ValueError(f'Detail {detail} is not owned by {identity}')
    url = f['page'] + (f'#detail-{detail}' if detail is not None else '')
    return f'<a href="{E(url)}">{E(f["name"])}</a>'


def content(*, features):
    data = json.loads((ROOT / ASSETS / 'evidence.json').read_text(encoding='utf-8'))
    mesh, results = data['mesh'], data['results']
    body = '<style>' + CSS + '</style><article class="case-report" aria-label="Damascene simulation case report">'
    body += '''<p class="eyebrow">SIMULATION CASE REPORT</p>
<p class="report-intro">How does a copper line–via–line connection inherit stress from fabrication, and how does that stress change under electrical bias and a temperature gradient? This example follows the structure from deposition and etching through cooldown to a three-field calculation.</p>'''
    body += '<div class="report-stats">' + ''.join(
        f'<div class="report-stat"><b>{value}</b><span>{label}</span></div>' for value, label in [
            ('0.80 μm', 'Solid stack thickness · X'), ('0.10 μm', 'Nominal via opening · Z'),
            ('250 → 25°C', 'Deposition temperature → cooldown'),
            (f'{mesh["solid_tetrahedra"]:,}', 'Tetrahedra in the solid materials')]) + '</div>'
    toc = [('background', 'Background'), ('geometry', 'Geometry & process'), ('model-viewer', 'Interactive model'), ('mesh', 'Mesh'),
           ('process-stress', 'Stress history'), ('boundary', 'Boundary conditions'),
           ('electrical', 'Electrical analysis'), ('thermal', 'Thermal analysis'),
           ('stress', 'Mechanical response'), ('numerics', 'Numerics'),
           ('features', 'Other features'), ('gt-a', 'GT-A / converter')]
    body += '<div class="report-toc" aria-label="Report contents">' + ''.join(
        f'<a href="#{anchor}">{label}</a>' for anchor, label in toc) + '</div>'

    body += '''<section class="report-section" id="background"><h2>Background · stress in a dual-damascene interconnect</h2>
<p>The device is a three-dimensional copper connection between two metal levels, embedded in oxide with nitride layers above a silicon substrate. Its engineering concern is <b>residual and thermomechanical stress</b>: copper and the surrounding materials cannot freely expand or contract independently, especially around the via and line corners.</p>
<p><b>Source:</b> the Sentaurus Interconnect training example “Example—Three-Dimensional Damascene Structure”, from <code>Applications_Library/GettingStarted/sinterconnect/DualDamascene</code>. The retained working decks use the example’s three-stage process, cooldown and operating calculation; the report introduces no changes to its physical setup.</p></section>

<section class="report-section" id="geometry"><h2>Geometry grows through the fabrication sequence</h2>
<p>The solid domain spans <b>0.80 × 0.15 × 0.70 μm in X × Y × Z</b>. X is the wafer-depth direction; deposited material extends toward negative X. The figures therefore use height −X. Two nominally 0.20 μm thick copper lines are joined through a via opening 0.10 μm long in Z. The modeled via occupies Y = 0.025–0.050 μm within the truncated simulation window.</p>'''
    body += figure('geometry', 'Three-dimensional copper connection and material section through the via',
                   'Final 3D copper geometry and material section at Y = 0.04 μm. The solid bounds are X = −0.70…+0.10, Y = −0.10…+0.05 and Z = 0…0.70 μm. Ambient Gas is hidden; geometry is undeformed.')
    body += '''<div class="process-flow" aria-label="Fabrication sequence schematic">
<div class="process-step"><b>1 · Lower line</b><p>Deposit oxide → pattern and etch the M1 trench → fill copper → strip resist → add a nitride cap.</p></div>
<div class="process-step"><b>2 · Via</b><p>Deposit oxide → pattern the via → etch oxide and nitride → fill copper → strip resist → fill oxide.</p></div>
<div class="process-step"><b>3 · Upper line</b><p>Pattern and etch the M2 trench → fill copper → strip resist → add the final nitride cap.</p></div></div>
<p>This sequence changes the geometry and its stress state. Oxide, nitride and copper deposition/fill steps specify <b>250°C</b>; the M1 and via etches specify 25°C, while the upper-line oxide etch specifies 0°C. After construction, cooldown and the final field calculation use the same geometry and mesh. The sequence above is a process schematic; the geometry image shows the completed structure.</p>
<p><b>Idealization:</b> mask-defined straight walls, ideal material interfaces and uniform deposited layers. The model contains copper, oxide, nitride and silicon; it does not resolve copper grains, surface roughness or a separate metal barrier/liner, and it does not simulate CMP.</p></section>'''

    body += '''<section class="report-section" id="model-viewer"><h2>Explore the model in 3D</h2>
<p class="vtk-viewer-intro">Rotate the structure, hide surrounding materials or move a Y section through the via. Switch between fabrication, cooldown and the final 1 s state to explore the copper stress and temperature fields. Electrical potential is available for the final state.</p>
<link rel="stylesheet" href="assets/vtk-viewer/viewer.css">
<div class="vtk-viewer" data-vtk-model="damascene"><div class="vtk-status" role="status">Loading the interactive model…</div></div>
<noscript><p>Enable JavaScript to explore the model interactively. The geometry and result figures remain available below.</p></noscript>
<script defer src="assets/case-reports/damascene/vtk-model.js"></script>
<script defer src="assets/vtk-viewer/vtk-model-viewer.js"></script></section>'''
    body += '<section class="report-section" id="mesh"><h2>Mesh · resolve the metal and material interfaces</h2>'
    body += table(['Control', 'Setting'], [
        ['Mesher', 'SnMesh controls; four-vertex tetrahedral volume topology.'],
        ['Interface sizing', '<code>min.normal.size = 0.020 μm</code>; <code>max.lateral.size = 0.100 μm</code>; <code>normal.growth.ratio.3d = 2.0</code>.'],
        ['Local refinement', 'Active box: 100 nm in X, Y and Z. Copper: 50 nm in each direction. Interface refinement for Copper, Nitride and Oxide.'],
        ['Solid mesh', f'<b>{mesh["solid_tetrahedra"]:,} tetrahedra</b> and <b>{mesh["solid_vertices"]:,} unique vertices</b>.'],
        ['Full mesh including Gas', f'{mesh["total_tetrahedra"]:,} tetrahedra and {mesh["vertices"]:,} unique geometric vertices.'],
    ])
    body += figure('mesh', 'Full mesh section and enlarged via and nitride detail',
                   'Section through the 3D tetrahedra at Y = 0.04 μm, with the via enlarged at right. Colors follow the material geometry. This is the shared mesh for the completed process, cooldown and final calculation.') + '</section>'

    body += '''<section class="report-section" id="process-stress"><h2>Physics · why fabrication history matters</h2>
<p><b>The main mechanism is thermal mismatch acting on a structure with process history.</b> Deposition adds material; etching removes material and releases constraints. Both operations redistribute stress. With <code>StressHistory = 1</code> and <code>EtchDepoRelax = 1</code>, that accumulated state is retained when the completed stack is cooled to 25°C using <code>mode mechanics</code>.</p>
<div class="equations">Δε<sub>mismatch</sub> ≈ (α<sub>Cu</sub> − α<sub>surrounding</sub>) ΔT</div>
<p>Here α is the thermal-expansion coefficient. Copper and the surrounding solids would change size by different amounts during cooling; their bonded interfaces enforce compatible motion and generate stress. The line–via transitions concentrate this response. Displacement is the mechanical unknown, while stress in the copper is the main quantity of interest.</p>
<p>The 25°C calculation is elastic because no duration is prescribed. The final calculation enables <code>mode mechanics current thermal</code> for 1 s and starts from this residual state. Oxide and nitride have viscoelastic behavior enabled, so the final response can also depend on time; the change in stress is not attributable to temperature alone.</p></section>

<section class="report-section" id="boundary"><h2>Boundary conditions · electrical bias and a thermal gradient</h2>
<p>Four named contacts select the electrical and thermal boundaries. These are named regions for applying conditions, rather than mechanical contact pairs.</p>'''
    body += figure('boundary-conditions', 'Electrical and thermal contact locations with a mechanics boundary map',
                   'Final 1 s conditions. E1/E2 mark the actual copper electrode faces; T1/T2 mark the temperature contacts. The mechanics map at right is schematic and shows only the constrained normal component; tangential motion remains free.')
    body += table(['ID / entity', 'Location (μm)', 'Condition'], [
        ['E1 · upper · Copper', 'Z = 0.70; X = −0.65…−0.45; Y = 0…0.05', 'V = 0.10 V'],
        ['E2 · lower · Copper', 'Z = 0; X = −0.30…−0.10; Y = 0…0.05', 'V = 0 V · electrical reference'],
        ['T1 · tm0 · Silicon', 'X = 0; full Y–Z window', 'T = 100°C'],
        ['T2 · tm1 · Nitride', 'X = −0.70; full Y–Z window', 'T = 25°C'],
        ['M1 · Bottom', 'X = +0.10', 'Default zero normal displacement rate, v<sub>x</sub> = 0.'],
        ['M2/M3 · Left / Right', 'Y = −0.10 / +0.05', 'Default v<sub>y</sub> = 0.'],
        ['M4/M5 · Back / Front', 'Z = 0 / 0.70', 'Default v<sub>z</sub> = 0.'],
        ['M6 · upper solid surface', 'Solid / Gas interface', 'Traction-free. No external mechanical force is added.'],
    ]) + '</section>'

    body += '''<section class="report-section" id="electrical"><h2>Electrical analysis · current crosses the via</h2>
<p>The 0.10 V difference drives conduction from the upper line through the narrow via into the lower line. Potential V is the electrical unknown; the current density follows <b>J = −σ<sub>e</sub>∇V</b>, where σ<sub>e</sub> is electrical conductivity. The continuous potential drop identifies the connected copper path.</p>'''
    body += figure('potential', 'Copper electric potential from zero to 0.10 volt through the via',
                   'Copper potential at t = 1 s, section Y = 0.04 μm; color scale 0–0.10 V. Only the conducting copper is shown.') + '</section>'

    body += '''<section class="report-section" id="thermal"><h2>Thermal analysis · heat flows from substrate to cap</h2>
<p>The silicon contact at 100°C and nitride cap at 25°C establish the temperature field. Heat conduction follows <b>q = −κ∇T</b>, where κ is thermal conductivity. The heat equation in this calculation has no heat-storage term, so this is a steady conduction field accompanying the time-dependent mechanics calculation.</p>
<p><b>Joule heating is zero in this result.</b> The temperature distribution is driven by the prescribed thermal boundaries; it does not demonstrate current-induced self-heating. Temperature feeds the mechanical response through thermal expansion.</p>'''
    body += figure('temperature', 'Temperature distribution in the solid stack from 25 to 100 degrees Celsius',
                   'Solid temperature at t = 1 s, section Y = 0.04 μm; color scale 25–100°C. Ambient Gas is excluded. Across the full copper region, temperature ranges from '
                   f'{results["3"]["copper_temperature_C"][0]:.1f} to {results["3"]["copper_temperature_C"][1]:.1f}°C.') + '</section>'

    body += '<section class="report-section" id="stress"><h2>Mechanical response · residual stress remains dominant</h2><p><a href="#model-viewer" data-explore-field="stress">Explore copper stress in the interactive 3D model ↑</a></p>'
    body += figure('copper-mises', 'Copper von Mises stress after cooldown and after the final 1 second calculation',
                   'Copper von Mises stress at Y = 0.04 μm: cooldown at left, final t = 1 s state at right. Both panels use 0–750 MPa and undeformed geometry. Saved nodal fields are interpolated within each tetrahedron, without additional spatial smoothing.')
    body += table(['State', 'Copper temperature', 'Peak copper von Mises stress'], [
        ['Completed process', '250°C', f'{results["1"]["copper_mises_max_MPa"]:.1f} MPa'],
        ['After elastic cooldown', '25°C', f'{results["2"]["copper_mises_max_MPa"]:.1f} MPa'],
        ['Final field calculation · 1 s', f'{results["3"]["copper_temperature_C"][0]:.1f}–{results["3"]["copper_temperature_C"][1]:.1f}°C',
         f'{results["3"]["copper_mises_max_MPa"]:.1f} MPa'],
    ])
    body += '''<p>These peaks are taken over all saved copper nodes, rather than only the displayed section. Cooling creates a much larger stress change than the subsequent operating calculation. In both later states the copper peak occurs at the upper-line edge, near (X, Y, Z) = (−0.65, 0.05, 0.25) μm.</p>
<p>The via profile below separates the three normal-stress components after cooldown. It helps reveal the multiaxial stress state that a single equivalent-stress field cannot describe.</p>'''
    body += figure('via-stress-profile', 'Three normal stress components along a copper line through the via after cooldown',
                   'σ<sub>xx</sub>, σ<sub>yy</sub> and σ<sub>zz</sub> along X at Y = 0.04 μm and Z = 0.35 μm, after cooling to 25°C. Positive values are tensile. The shaded interval marks the nominal via elevation.')
    body += '''<p>Sharp, ideal corners can produce mesh-sensitive stress peaks. The values describe this mesh and material model; a copper failure or reliability judgment would require an appropriate criterion and a mesh-sensitivity study.</p></section>

<section class="report-section" id="numerics"><h2>Numerics · preserve the state between stages</h2>
<p>The process stage enables stress history and etch/deposition relaxation before geometry construction. Cooldown imports that state for an elastic solve. The final stage imports the cooled state, applies the four contacts and advances to 1 s in 14 steps, starting at 10<sup>−4</sup> s. The decks do not prescribe special convergence tolerances or a parameter-sweep comparison.</p></section>'''

    body += '<section class="report-section" id="features"><h2>Other features used in this case</h2><ul>'
    body += '<li>' + feature_link(features, 'stress-history', 29) + ' carries fabrication-induced stress into cooldown and the subsequent field calculation.</li>'
    body += '<li>' + feature_link(features, 'etch-stress-rebalancing') + ' and ' + feature_link(features, 'deposition-stress-rebalancing') + ' update equilibrium as material is removed or added.</li>'
    body += '<li>' + feature_link(features, 'field-visualization', 42) + ' includes a copper-only stress cut through the via, using <code>SetPlxList</code> and <code>WritePlx</code> to extract the three normal components.</li></ul></section>'

    body += '''<section class="report-section" id="gt-a"><h2>GT-A benchmark and si_converter</h2>
<p>GT-A numerical benchmarking has not been completed for this case. The current <code>si_converter</code> does not yet support conversion of the complete process-history and joint mechanics/current/thermal workflow; this case is not fully supported.</p></section></article>'''
    return body
