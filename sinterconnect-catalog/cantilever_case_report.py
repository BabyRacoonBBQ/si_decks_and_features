"""Reader-facing Cantilever report using measured case data and catalog links."""
from pathlib import Path
from html import escape as E
import json

ROOT = Path(__file__).resolve().parent
ASSETS = 'assets/case-reports/cantilever'

CSS = '''
.case-report{margin-top:24px}.case-report .report-intro{font-size:18px;max-width:1000px;color:#415b70}
.case-report .report-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:24px 0}
.case-report .report-stat{background:#fff;border:1px solid #d5dfe8;border-radius:10px;padding:18px}.case-report .report-stat b{display:block;font-size:25px;color:#125f69}.case-report .report-stat span{font-size:12px;color:#607486}
.case-report .report-toc{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0 32px}.case-report .report-toc a{padding:7px 12px;background:white;border:1px solid #d5dfe8;border-radius:6px;text-decoration:none;font-size:13px}
.case-report .report-section{margin:36px 0;scroll-margin-top:24px}.case-report .report-section>h2{font-size:25px;border-bottom:1px solid #cfdae3;padding-bottom:10px;margin-bottom:20px}
.case-report figure{margin:20px 0;background:white;border:1px solid #d5dfe8;border-radius:10px;padding:16px;min-width:0}.case-report figure img{width:100%;height:auto;display:block;object-fit:contain}.case-report figcaption{font-size:13px;color:#506b7e;margin-top:14px;line-height:1.65}
.case-report .result-figures{display:grid;grid-template-columns:1fr 1fr;gap:20px}.case-report .result-figures figure{margin:8px 0}.case-report .result-figures img{height:540px}
.case-report .table-wrap{overflow-x:auto;border:1px solid #dce3ea;border-radius:8px;margin:16px 0}.case-report table{font-size:14px}.case-report th{white-space:normal}.case-report td{min-width:110px}.case-report td:first-child{min-width:130px;font-weight:600}
.case-report .equations{font:19px/1.9 Georgia,"Cambria Math",serif;background:#e9f2f5;border-radius:8px;padding:18px 22px;margin:18px 0}
@media(max-width:900px){.case-report .report-stats{grid-template-columns:1fr 1fr}.case-report .result-figures{grid-template-columns:1fr}.case-report .result-figures img{height:480px}}
@media(max-width:500px){.case-report .report-stat b{font-size:21px}.case-report figure{padding:10px}.case-report .result-figures img{height:390px}.case-report .report-section>h2{font-size:22px}}
@media print{.case-report .report-toc{display:none}.case-report figure{break-inside:avoid}.case-report .table-wrap{overflow:visible}.case-report .result-figures img{height:380px}}
'''


def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th scope="col">{E(header)}</th>' for header in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def figure(filename, alt, caption):
    url = f'{ASSETS}/{filename}'
    return f'<figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="{E(alt)}" loading="lazy"></a><figcaption>{caption}</figcaption></figure>'


def feature_link(features, detail_row, label):
    owners = [feature for feature in features if detail_row in feature.get('details', [])]
    if len(owners) != 1:
        raise ValueError(f'Expected one catalog feature for detail {detail_row}, found {len(owners)}')
    feature = owners[0]
    return f'<a href="{E(feature["page"])}#detail-{detail_row}">{E(label)}</a>'


def content(*, features):
    # Audit records stay in local assets; the report exposes case facts only.
    data = json.loads((ROOT / ASSETS / 'evidence.json').read_text(encoding='utf-8'))
    mesh = data['mesh']
    body = '<style>' + CSS + '</style><article class="case-report" aria-label="Cantilever simulation case report">'
    body += '<p class="eyebrow">SIMULATION CASE REPORT</p><p class="report-intro">A 3D cantilever under a transverse end load: understand how the beam bends, how far its free end moves, and how stress is distributed along its length.</p>'
    body += '<div class="report-stats">' + ''.join(f'<div class="report-stat"><b>{value}</b><span>{label}</span></div>' for value, label in [('50 μm', 'Beam length · axial direction X'), ('4 × 4 μm', 'Square cross-section · Y and Z'), (f'{mesh["vertices"]:,}', 'Mesh vertices'), (f'{mesh["tetrahedra"]:,}', 'Volume tetrahedra')]) + '</div>'
    sections = [('background', 'Background'), ('geometry', '1 · Geometry'), ('mesh', '2 · Mesh'), ('physics', '3 · Elastic bending'), ('boundary', '4 · Boundary conditions'), ('numerics', '5 · Numerics'), ('results', '6 · Results'), ('features', '7 · Other features'), ('gt-a', '8 · GT-A / converter')]
    body += '<div class="report-toc" aria-label="Report contents">' + ''.join(f'<a href="#{anchor}">{label}</a>' for anchor, label in sections) + '</div>'

    body += '''<section class="report-section" id="background"><h2>Background · a beam-bending example</h2>
<p>This training-manual example models a slender, homogeneous beam fixed at one end and loaded at the other. It demonstrates the displacement response and bending-stress field of a simple microscale structure.</p>
<p><b>Source:</b> “Cantilever With End Load (3D)”, <code>Applications_Library/GettingStarted/sinterconnect/3D_Cantilever</code>. The working input preserves the rectangular geometry, elastic constants and load configuration of the archived reference.</p></section>

<section class="report-section" id="geometry"><h2>1 · Geometry and scale</h2>
<p>The model is a three-dimensional rectangular beam, <b>50 μm long with a 4 × 4 μm square cross-section</b>. X runs along the beam from the free end at X = 0 to the fixed end at X = 50 μm. Y and Z both span −2 to +2 μm. The single material region is <code>Silicon_1</code>.</p>'''
    body += figure('geometry.svg', 'Three-dimensional 50 by 4 by 4 micrometer cantilever with coordinate directions', 'Beam geometry with its physical aspect ratio preserved. The shaded face is the fixed end at X = 50 μm.')
    body += '''<p><b>Geometry evolution:</b> none. The beam geometry stays fixed during model construction and the mechanics calculation. A deformed-coordinate export is used to visualize the resulting displacement.</p>
<p><b>Idealization:</b> a straight, prismatic beam with uniform properties, a perfectly fixed support and a point-applied load. Fillets, surface roughness and a finite load-introduction area are omitted.</p></section>'''

    body += '<section class="report-section" id="mesh"><h2>2 · Mesh</h2>'
    body += table(['Setting', 'Value'], [
        ['Line-spacing control', '0.3 μm in X, Y and Z, with additional coordinate lines at Y = 0 and Z = 0.'],
        ['Realized coordinate intervals', f'ΔX ≈ {mesh["spacing_um"]["x"][0]:.6f} μm; ΔY = ΔZ ≈ {mesh["spacing_um"]["y"][0]:.6f} μm.'],
        ['Mesh size', f'<b>{mesh["vertices"]:,} vertices</b> and <b>{mesh["tetrahedra"]:,} volume elements</b>.'],
        ['Topology', 'Four-vertex tetrahedra in one bulk region. The input does not explicitly specify the solve-time interpolation order.'],
        ['Local treatment', 'No local refinement, boundary layers or adaptive remeshing are specified.'],
    ])
    body += figure('mesh.svg', 'Cantilever surface mesh with a close-up of the fixed-end region', 'Surface mesh at Y = −2 μm. The close-up shows the fixed-end region, X = 46–50 μm.') + '</section>'

    body += '''<section class="report-section" id="physics"><h2>3 · Physics: elastic bending</h2>
<p>The central mechanism is <b>elastic bending</b>. The transverse force moves the free end toward −Z, while the fixed end supplies a reaction force and moment that balance the load. Bending stretches one side of the beam and compresses the other, producing stress.</p>
<p>The beam’s displacement is greatest at the free end. The bending moment grows toward the fixed end, so nominal bending stress is largest near the support and at the outer fibers of the cross-section.</p>
<p>The calculation uses <code>mode mechanics</code> to solve three-dimensional static elastic equilibrium for displacement; stresses follow from the resulting strain. There is no thermal or electrical coupling. The material is isotropic elastic, with <b>Young’s modulus E = 1 GPa</b> and <b>Poisson’s ratio ν = 0.2</b>; these example values override the constants associated with the Silicon material name.</p>
<p>For a slender beam, the familiar tip-deflection estimate summarizes the dependence on load, length and bending stiffness:</p>
<div class="equations">δ<sub>tip</sub> ≈ |F<sub>z</sub>| L³ / (3 E I<sub>y</sub>)</div>
<p>Here L is the beam length and I<sub>y</sub> is the cross-section’s second moment of area about Y. A longer beam bends much more; a higher Young’s modulus or a larger section moment makes it stiffer. This explains why both the material stiffness and the 50 × 4 × 4 μm geometry matter for the response.</p></section>'''

    body += '''<section class="report-section" id="boundary"><h2>4 · Boundary conditions and load</h2>
<p>The <b>X = 50 μm</b> end is fixed. A concentrated force acts at the free-end center, <b>(0, 0, 0) μm</b>, along <b>−Z</b>. Its magnitude is <b>0.03 dyn = 0.3 μN</b>.</p>'''
    body += figure('boundary-conditions.svg', 'Hatched fixed support and negative Z point force at the free-end center', 'The hatched support constrains all three displacement components. The arrow shows the point-force direction; its length is illustrative.')
    body += table(['Boundary', 'Location', 'Condition'], [
        ['BC01 · Bottom', 'X = 50 μm', '<code>dx = dy = dz = 0</code>.'],
        ['BC02 · pointend', '(0, 0, 0) μm', '<code>pfx = pfy = 0</code>; <code>pfz = −0.03 dyn</code>.'],
        ['BC03 · Left', 'Y = −2 μm', 'Zero surface traction: <code>sx = sy = sz = 0</code>.'],
        ['BC04 · Right', 'Y = +2 μm', 'Zero surface traction.'],
        ['BC05 · Back', 'Z = −2 μm', 'Zero surface traction.'],
        ['BC06 · Front', 'Z = +2 μm', 'Zero surface traction.'],
    ])
    body += '<p>Boundary conditions are assigned directly to the named exterior faces through <code>stressdata bc.location</code>. The point load uses <code>point.coord</code>. No separate contact definition or mechanical contact pair is used.</p></section>'

    body += '''<section class="report-section" id="numerics"><h2>5 · Numerics</h2>
<p>The input requests one mechanics solve without case-specific tolerances, iteration limits or solver-selection overrides. It contains no explicit numerical-parameter toggle or parameter sweep.</p></section>

<section class="report-section" id="results"><h2>6 · Displacement and stress</h2>
<p>Displacement is the solved variable. The main quantities of interest are the free-end deflection and the <b>von Mises stress field</b>. The field plots illustrate displacement increasing toward the free end and bending stress developing along the beam.</p>
<div class="result-figures">'''
    for number, label, caption in [
        (1, 'von Mises stress', 'MisesStress · displayed color scale: approximately 8.152e2–1.405e6 Pa.'),
        (2, 'Displacement magnitude', 'Abs(Displacement-V) · displayed color scale: 0–0.577 μm.'),
    ]:
        url = f'assets/svisual/Cantilever-{number}.png'
        body += f'<figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="Cantilever {E(label)} field" loading="lazy"></a><figcaption><b>{E(label)}</b><br>{E(caption)}</figcaption></figure>'
    body += '''</div><p>The sharp fixed-end edges and concentrated load can produce localized stresses. Their local peaks should be interpreted with the mesh and idealized load geometry in mind.</p></section>

<section class="report-section" id="features"><h2>7 · Other features</h2>'''
    body += table(['Case feature', 'How it is used', 'Feature catalog'], [
        ['Deformed-coordinate visualization', 'Export the displaced geometry with <code>deform.scale=5.0</code> to make the bending shape easier to inspect.', feature_link(features, 44, 'Field visualization · deformation scale')],
        ['Centerline displacement extraction', 'Select <code>Displacement_z</code> and extract along X at <code>Y = Z = 0</code> using <code>plot.1d</code>.', feature_link(features, 43, 'Field output · spatial data cuts')],
    ]) + '</section>'

    body += '<section class="report-section" id="gt-a"><h2>8 · GT-A benchmark and si_converter</h2>'
    body += table(['Item', 'Case status'], [
        ['GT-A benchmark', 'Numerical equivalence has not yet been validated.'],
        ['si_converter', 'The mesh, elastic material, fixed support and end point load are represented in the converted model. End-to-end solving and the requested post-processing outputs remain unverified.'],
    ]) + '</section></article>'
    return body
