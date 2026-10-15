"""Verified image associations and calculation notes for case detail pages."""
from html import escape as E
from pathlib import Path
import json
from artifact_preview import preview_url
from cantilever_case_report import content as cantilever_report
from damascene_case_report import content as damascene_report

SVISUAL_FIELDS={
    '3D_Interconnect':['von Mises stress','Temperature','Electric potential'],
    'Inverter':['Electric potential','Electric-field magnitude'],
}

def result_content(alias,case_page,*,features=()):
    if alias=='Cantilever':
        return cantilever_report(features=features)
    if alias=='Damascene':
        return damascene_report(features=features)
    body=''
    if alias=='TSV_Local':
        body+='<h2>Result</h2>'
        for n in range(5,12):
            body+=f'<h3>Group {n-4} · n{n} → n{n+14} → n{n+35}</h3><div class="contour-gallery">'
            for i,label in enumerate(['von Mises stress','Displacement magnitude'],1):
                url=f'assets/svisual/TSV_n{n}-{i}.png'
                body+=f'<figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="TSV group {n-4} — {label}" loading="lazy"></a><figcaption>{label}</figcaption></figure>'
            body+='</div>'
    benchmarks=json.loads(Path(__file__).with_name('ppt-benchmarks.json').read_text(encoding='utf-8'))
    if alias in benchmarks:
        benchmark=benchmarks[alias]
        body+='<h2>Result data</h2><h3>Accuracy</h3>'
        for key,first_header in [('accuracy','Metric'),('performance','Stage · time (s)')]:
            if key=='performance':body+='<h3>Performance</h3>'
            body+=f'<div style="overflow-x:auto"><table><thead><tr><th>{first_header}</th><th>StressThermal</th><th>GT-S</th><th>GT-A</th></tr></thead><tbody>'
            for row in benchmark[key]:body+='<tr>'+''.join(f'<td>{E(value)}</td>' for value in row)+'</tr>'
            body+='</tbody></table></div>'
        body+=f'<p>{E(benchmark["mesh"])}</p>'
    if alias in SVISUAL_FIELDS:
        body='<h2>Result</h2><div class="contour-gallery">'
        for i,label in enumerate(SVISUAL_FIELDS[alias],1):
            url=f'assets/svisual/{alias}-{i}.png'
            body+=f'<figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="{E(alias)} — {E(label)}" loading="lazy"></a><figcaption>{E(label)}</figcaption></figure>'
        body+='</div>'
    if alias=='3D_Matrix_Calculation':
        body+='<h2>Result</h2><p>No matched result TDR is available yet.</p>'
    if alias=='Linear_Buckling':
        body+='''<h2>Calculation setup</h2><table><tbody>
<tr><th>Geometry</th><td>3D silicon column: 50 μm long, 4 × 4 μm square section; axial direction X.</td></tr>
<tr><th>Mesh definition</th><td>X spacing 1 μm; Y and Z spacing 0.5 μm; mixed.mesh initialization.</td></tr>
<tr><th>Material</th><td>Isotropic elastic model. E = 1e10 in the deck's native modulus units; ν = 0.2. Bulk and shear moduli use Enu2K and Enu2G.</td></tr>
<tr><th>Constraint</th><td>Bottom face at X = 50 μm: dx = dy = dz = 0.</td></tr>
<tr><th>Reference load</th><td>Point force at (0, 0, 0): Fx = +0.03 dyn, Fy = Fz = 0; axial compression toward the fixed end.</td></tr>
<tr><th>Requested modes</th><td>mode buckling=3; maximum iterations 2000; tolerance 1e-8.</td></tr>
<tr><th>Solver</th><td>ARPACK eigensolver; the recorded buckling run entered MUMPS factorization and ARPACK dsaupd / dseupd.</td></tr>
</tbody></table>
<h2>Buckling eigenvalues</h2><table><thead><tr><th>Mode</th><th>Eigenvalue λ</th><th>Critical force λ × 0.03 dyn</th></tr></thead><tbody>
<tr><td>1</td><td>71.761</td><td>2.15283 dyn (21.5283 μN)</td></tr>
<tr><td>2</td><td>71.761</td><td>2.15283 dyn (21.5283 μN)</td></tr>
<tr><td>3</td><td>609.80</td><td>18.294 dyn (182.94 μN)</td></tr>
</tbody></table>
<p>Values retain the precision printed by the solver. The recorded local and reference runs reported the same three eigenvalues.</p>
<h3>What does an eigenvalue mean?</h3>
<p>λ is a dimensionless critical-load multiplier. Linear buckling solves (K + λ K<sub>G</sub>) φ = 0, where K is the elastic stiffness and K<sub>G</sub> is the geometric stiffness from the reference load. For this single-load case, the predicted critical force is λ times the applied 0.03 dyn. The first positive eigenvalue gives the lowest predicted buckling load.</p>
<p>The eigenvector φ describes a buckling shape; its sign and amplitude are arbitrary. It is not the actual displacement after buckling. The equal first two eigenvalues form a repeated eigenspace: different solvers can return rotated combinations of the two shapes while describing the same instability.</p>
<p>A separate six-mode diagnostic reported 71.761, 71.761, 609.80, 609.80, 1335.7 and 1458.2. Repeated-mode subspace comparisons matched; individual vectors inside a repeated pair need not match component by component.</p>
<h3>Output and interpretation</h3><p>The recorded run exited with code 0 and wrote result_sis.tdr with Displacement, StepDisplacement and BucklingMode1–BucklingMode3. This is historical case evidence, not a new validation of the current binary. Linear buckling predicts an idealized onset of instability; post-buckling requires a separate nonlinear calculation.</p>'''
    registry=Path(__file__).with_name('gt-a-cases.json')
    if registry.exists():
        record=json.loads(registry.read_text(encoding='utf-8')).get(alias)
        if record:
            body+='<h2 id="gt-a">GT-A</h2>'
            body+=f'<p><b>{E(record["status"])}</b> · Equivalence: {E(record["equivalence"])}</p>'
            if record.get('note'):body+=f'<p>{E(record["note"].replace("ANSYS", "GT-A"))}</p>'
            if record['files']:
                body+='<ul>'+''.join(f'<li><a href="{E(preview_url(f,case_page))}">{E(f["label"].replace("ANSYS", "GT-A"))}</a></li>' for f in record['files'])+'</ul>'
            else:body+='<p>The equivalent GT-A script is pending.</p>'
    return body
