"""Canonical English catalog: grouped features, embedded details, unified case lists."""
from pathlib import Path
from collections import OrderedDict
import json, html
from build_source_catalog import definitions, ALIASES
from catalog_english import CASE_TEXT, WORDS, SOURCE_CASE_NOTES, english_feature
from ppt_case_images import CASE_IMAGES
from feature_content import register_planned, content_html, CONTENT_CSS
from case_result_content import result_content
from damascene_case_report import FEATURE_IDS as DAMASCENE_FEATURE_IDS
from progress_log import progress_body

ROOT=Path(__file__).resolve().parent
E=html.escape
OUTPUT_FIELDS={
    'Mechanics':[
        'Displacement','Displacement increments','Pseudo displacement',
        'Stress components','von Mises stress','Pressure',
        'Principal stresses','Principal strains','Principal directions',
        'Elastic strain','Plastic strain','Viscoplastic strain','Creep strain','Swelling strain',
        'Equivalent plastic strain','Equivalent viscoplastic strain','Equivalent creep strain',
        'Strain energy densities','Energy-rate densities','Nodal forces','Reaction forces',
        'Stress maxima','Strain maxima'],
    'Thermal':['Temperature','Previous temperature','Temperature gradient','Heat flux',
        'Total heat-source density','Joule heating','Derived hotspot maps'],
}

def output_fields():
    return ''.join(f'<h3>{E(group)}</h3><ul>'+''.join(f'<li>{E(field)}</li>' for field in fields)+'</ul>' for group,fields in OUTPUT_FIELDS.items())

def render():
    raw=json.loads((ROOT/'source-table-data.json').read_text(encoding='utf-8'))
    original=json.loads((ROOT/'catalog-data.json').read_text(encoding='utf-8'))
    base=json.loads((ROOT/'features-data.json').read_text(encoding='utf-8'))
    features=[dict(f,details=[]) for f in base]
    by_name={f['name']:f for f in features}
    def add(name,category,module,rows):
        if name not in by_name:
            slug=name.lower().replace(' / ','-').replace(' & ','-').replace(' ','-')
            f=dict(id=slug,name=name,category=category,module=module,status='',case_ids=[],page='feature-'+slug+'.html',details=[])
            features.append(f);by_name[name]=f
        by_name[name]['details'] += rows
    assignments={
        'Prescribed displacement / rate · traction · pressure · point force':[2,3,4,5,6,7,11,12],
        'Thermal resistor':[8], 'Prescribed temperature · ramps · heat flux · contact power':[9,57],
        'Electrical current · electrostatic':[10,18,34,35,38,39],
        'Plastic & viscoplastic':[13,14], 'Thermal mismatch · intrinsic stress':[15],
        'Conductivity · heat storage · emissivity':[16], 'Viscous & viscoelastic':[17],
        'First / second order':[20], 'Quasistatic equilibrium':[21],
        'TRBDF · Newton · direct / iterative solvers':[22,23,30,56],
        'Coupling · beam-plate coupling · variable boundary':[24],
        'Fluid surface tension / pressure':[25], 'Linear buckling':[26], 'Post-buckling':[27],
        'Geometric nonlinearity':[28], 'Steady-state · transient':[33], 'Electrothermal':[36],
        'Temperature / flux continuity':[], 'Shape functions': [41],
        'Mechanical contact · crack analysis':[52], 'ARPACK / MUMPS recovery: see linear buckling':[60],
    }
    for name,rows in assignments.items():
        add(name,'Element library','Mechanics',rows)
    add('Material inheritance','Material models','Mechanics',[19])
    add('Thermoelectromechanical coupling','Analysis modes','Coupled / Electrical',[37])
    add('Thermal resistance matrix','Heat transfer & materials','Thermal',[40])
    add('Stress analysis and history','Post-processing & output','General',[29,31,32])
    add('Field visualization and output','Post-processing & output','General',[42,43,44,45,46,47,48,53])
    add('Stress-induced mobility enhancement','Stress-causing mechanisms','Mechanics',[49])
    add('Geometry transformations and vertex merging','Geometry & mesh','General',[50,51])
    add('Tcl scripting and units','Scripting & data exchange','General',[54,55,59])
    add('Field-data import','Scripting & data exchange','General',[58])
    by_name['Field visualization and output']['output_fields']=OUTPUT_FIELDS
    by_name['Geometry transformations and vertex merging']['show_on_home']=False
    # The slide grouped these only to save space; each solver is a feature.
    solver_splits={
        'FEM mechanics · FVM thermal / electrical': [('FEM mechanics',[]),('FVM thermal',[]),('FVM electrical',[])],
        'TRBDF · Newton · direct / iterative solvers': [('TRBDF',[30]),('Newton',[22,23]),('Direct solvers',[]),('Iterative solvers',[56])],
        'ARPACK / MUMPS recovery: see linear buckling': [('ARPACK',[60]),('MUMPS',[])],
        'Steady-state · transient': [('Steady-state thermal analysis',[33]),('Transient thermal analysis',[33])],
        'Conduction · convection · radiation': [('Conduction',[]),('Convection',[]),('Radiation',[])],
        'Conductivity · heat storage · emissivity': [('Thermal conductivity',[16]),('Heat storage',[16]),('Emissivity',[])],
        'Applied heating · electrical heating': [('Applied heating',[]),('Electrical heating',[])],
        'Prescribed temperature · ramps · heat flux · contact power': [('Prescribed temperature',[9,57]),('Temperature ramps',[]),('Prescribed heat flux',[]),('Contact power',[])],
        'Adiabatic · convection · radiation': [('Adiabatic boundary',[]),('Convection boundary',[]),('Radiation boundary',[])],
        'Temperature / flux continuity': [('Temperature continuity',[]),('Heat-flux continuity',[])],
        'Electrical current · electrostatic': [('Electrical current',[10,18,35,39]),('Electrostatic',[34,38])],
        'Thermal mismatch · intrinsic stress': [('Thermal mismatch',[15]),('Intrinsic stress',[])],
        'Densification · grain growth': [('Densification',[]),('Grain growth',[])],
        'Surface reflow · edge dislocation': [('Surface reflow',[]),('Edge dislocation',[])],
        'Cohesive zipping · phase change': [('Cohesive zipping',[]),('Phase change',[])],
        'Viscous & viscoelastic': [('Viscous',[]),('Viscoelastic',[17])],
        'Plastic & viscoplastic': [('Plastic',[13]),('Viscoplastic',[14])],
        'Cohesive damage / softening': [('Cohesive damage',[]),('Softening',[])],
        'First / second order': [('First-order elements',[]),('Second-order elements',[20])],
        'Fluid surface tension / pressure': [('Fluid surface tension',[25]),('Fluid pressure',[25])],
        'Etch / deposition stress rebalancing': [('Etch stress rebalancing',[]),('Deposition stress rebalancing',[])],
        'Mechanical contact · crack analysis': [('Mechanical contact',[]),('Crack analysis',[52])],
        'Prescribed displacement / rate · traction · pressure · point force': [
            ('Prescribed displacement',[4,7,11]),('Prescribed displacement rate',[3]),
            ('Traction',[6]),('Pressure boundary',[5]),('Point force',[2]),('Reaction-force output',[12])],
        'Moment · symmetry · periodic boundary': [('Moment',[]),('Symmetry',[]),('Periodic boundary',[])],
        'Coupling · beam-plate coupling · variable boundary': [('Coupling boundary',[24]),('Beam-plate coupling',[]),('Variable boundary',[])],
        'Stress analysis and history': [('Stress analysis',[31,32]),('Stress history',[29])],
        'Field visualization and output': [('Field visualization',[42,44,46]),('Field output',[43,45,47,48,53])],
        'Tcl scripting and units': [('Tcl scripting',[54,55]),('Units',[59])],
    }
    legacy_solver_pages=[]
    for name,parts in solver_splits.items():
        old=by_name[name]
        position=features.index(old)
        children=[]
        for title,detail_rows in parts:
            add(title,old['category'],old['module'],detail_rows)
            child=by_name[title]
            child['case_ids']=list(old['case_ids'])
            child['status']=old['status']
            if title=='Field output':child['output_fields']=OUTPUT_FIELDS
            features.remove(child)
            children.append(child)
        features[position:position+1]=children
        legacy_solver_pages.append((old,children))
    register_planned(features)
    rows={f['row']:english_feature(f) for f in raw['features']}
    owner={n:f for f in features for n in f['details']}
    assert sorted(owner)==list(range(2,61))
    # A combined record may describe multiple independent capabilities.
    assert {n for f in features for n in f['details']}==set(range(2,61))
    ns=definitions();css=ns['css']+'''pre{white-space:pre-wrap;overflow-wrap:anywhere}dd{margin:0 0 14px}dt{font-weight:600}h2{margin-top:28px}.detail{margin:16px 0;scroll-margin:24px}.meta{display:flex;gap:20px;flex-wrap:wrap}.case-list li{margin:12px 0}.case-list p{margin:2px 0}.row a{text-decoration:none}.row a:hover{text-decoration:underline}'''
    def shell(title,body,active):
        chinese=active=='progress.html'
        labels=['功能目录','功能测试','应用案例'] if chinese else ['Features','Feature tests','Application cases']
        links=list(zip(['index.html','feature-tests.html','application-cases.html'],labels))+[('progress.html','进度日志')]
        tabs="".join(f'<a href="{url}"'+(' aria-current="page"' if url==active else '')+(' lang="zh-CN"' if url=='progress.html' else '')+f'>{label}</a>' for url,label in links)
        brand='StressThermal / 工程目录' if chinese else 'StressThermal / Engineering catalog'
        lang='zh-CN' if chinese else 'en'
        return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} · StressThermal</title><style>{css}</style></head><body><nav><strong>{brand}</strong>{tabs}</nav><main>{body}</main></body></html>'
    def write(page,title,body):
        active=page if page in ('feature-tests.html','application-cases.html','progress.html') else 'index.html'
        for c in cases.values():
            if c['page']==page:active='feature-tests.html' if c['category']=='Feature tests' else 'application-cases.html'
        (ROOT/page).write_text(shell(title,body,active),encoding='utf-8')
    def badge(s):return f'<span class="badge {E(s.lower())}">{E(s)}</span>' if s else ''
    css+=CONTENT_CSS
    css+=' .case-status{display:inline-block;padding:4px 10px;border-radius:6px;font-size:13px;font-weight:600;white-space:nowrap}.status-integrated{background:#d4eeea;color:#17645f}.status-review{background:#fff0d7;color:#875000}.status-deferred{background:#eee5f7;color:#68448a}.status-pending{background:#e9eef3;color:#485d70}.status-matched{background:#dceee0;color:#28603a}'
    css+=' .contour-gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:20px}.contour-gallery figure{margin:0;padding:16px;background:white;border:1px solid #d5dfeb;border-radius:12px}.contour-gallery img{display:block;width:100%;height:320px;object-fit:contain}.contour-gallery figcaption{margin-top:12px;font-weight:600}'
    def case_status(c):
        text=c['verify']
        if text.startswith('Matched'):label,style='Matched','matched'
        elif text.startswith('Deferred'):label,style='Deferred','deferred'
        elif text=='Not started':label,style='Not started','pending'
        elif text.startswith('Full workflow'):label,style='Matched','matched'
        else:label,style='Needs review','review'
        result=f'<span class="case-status status-{style}" title="{E(text,quote=True)}">{label}</span>'
        if c.get('integrated'):
            result+=' <span class="case-status status-integrated" title="Included in the case collection">Integrated</span>'
        return result
    css+=' nav a[aria-current=page]{background:#28495e;color:white;border-radius:6px;box-shadow:inset 0 -3px #68d2dc;padding:10px 12px}nav{flex-wrap:wrap}'
    cases=OrderedDict()
    for c in original['cases']:
        c=dict(c,**CASE_TEXT[c['id']]); c.update(alias=ALIASES[c['id']],page=f'case-{c["id"]}.html',record_type='Catalog record')
        c['mode'] = {'tsv':'mode mechanics','backend':'mode thermal; mode mechanics',
                     'submodel':'mode mechanics','quasistatic':'mode mechanics',
                     'buckling':'mode buckling','postbuckling':'mode buckling',
                     'deformation':'mode mechanics'}[c['id']]
        cases[c['alias']]=c
    for c in raw['cases']:
        c=dict(c); c.update(page='case-source-'+c['alias'].lower().replace('_','-')+'.html',verify=WORDS.get(c['source_status'],c['source_status']),record_type='Table record')
        cases[c['alias']]=c
    # Only dedicated feature-development examples are small feature tests.
    # Backend, user and Getting Started examples are application cases.
    feature_tests={'Quasistatic','Linear_Buckling','Post_Buckling','Large_Deformation'}
    for alias,c in cases.items():
        c['category']='Feature tests' if alias in feature_tests else 'Application cases'
        c['integrated']=alias=='TSV_Local'
        if alias=='TSV_Local':c['verify']='Matched (confirmed by user)'
        if alias=='Package_Reliability':
            c['device']='Power semiconductor package, adapted from a PowerSO-10RF / LDMOS device package.'
            c['background']='Uneven heating causes differential thermal expansion between package materials, producing thermomechanical stress. The temperature field is mapped into the mechanical calculation.'
        if alias=='Submodeling':
            c['device']='Flip-chip package with a 3 × 3 copper-pillar array and a single-pillar submodel.'
            c['background']='Cooling from 180 °C to 25 °C. Global displacement is mapped to the refined single-pillar mesh to solve local stress.'
        c['display_alias']={'Package_Reliability':'Backend_Package_Reliability','Submodeling':'Backend_Submodeling'}.get(alias,alias)
        c['application_group']=('Backend' if alias.startswith('Backend_') or alias in ('Package_Reliability','Submodeling')
                                else 'User' if alias.startswith('User_') or alias=='TSV_Local'
                                else 'Getting Started' if alias not in feature_tests else '')
    # Only exact case identifiers are deduplicated. Originals and adaptations stay distinct.
    for f in features:
        linked=[ALIASES[x] for x in f['case_ids']]
        for n in f['details']:
            aliases=rows[n]['case_aliases']
            linked += [c['alias'] for c in raw['cases']] if aliases==['all'] else aliases
        f['related_cases']=list(dict.fromkeys(linked))
        if f['id'] in DAMASCENE_FEATURE_IDS and 'Damascene' not in f['related_cases']:
            f['related_cases'].append('Damascene')
    def case_list(aliases):
        if not aliases:return '<p>No associated cases recorded.</p>'
        out='<ul class="case-list">'
        for a in aliases:
            c=cases[a]
            out+=f'<li><a href="{c["page"]}"><b>{E(c["display_alias"])}</b></a> — {E(c["name"])}'
            if c.get('feature'):out+=f'<p>{E(c["feature"])}</p>'
            out+=f'<p>{case_status(c)}</p></li>'
        return out+'</ul>'
    def detail(n):
        r=rows[n]
        # Keep source field labels here so unlike status schemes cannot overwrite each other.
        return (f'<article class="card detail" id="detail-{n}"><h3>{E(r["name"])}</h3>'
                f'<div class="meta"><span>Recorded status: <b>{E(r["source_status"])}</b></span><span>Difficulty / effort: {E(r["difficulty"])}</span><span>Recorded mode: {E(r["mode"])}</span></div>'
                f'<dl><dt>Command / behavior</dt><dd><pre>{E(r["commands"])}</pre></dd><dt>Manual reference</dt><dd>{E(r["reference"])}</dd></dl>'
                f'<p class="sub">Record {n} · Original category: {E(r["original_category"])} · Case scope: {E(", ".join(r["case_aliases"])) or "Not specified"}</p></article>')
    for f in features:
        body=f'<a href="index.html#{f["id"]}">← Features</a><div class="eyebrow" style="margin-top:24px">{E(f["module"])} / {E(f["category"])}</div><h1>{E(f["name"])}</h1>{badge(f["status"])}'
        body+=content_html(f)
        if f['details']:body+='<h2>Detailed capabilities</h2>'+''.join(detail(n) for n in f['details'])
        if f.get('output_fields'):body+='<h2>Supported output fields</h2>'+output_fields()
        body+=f'<h2>Related cases <span class="count">({len(f["related_cases"])})</span></h2>'
        for category in ('Feature tests','Application cases'):
            related=[a for a in f['related_cases'] if cases[a]['category']==category]
            if category=='Application cases':
                related.sort(key=lambda a: 0 if cases[a]['application_group']=='Backend' else 1)
            body+=f'<section class="related-case-group"><h3>{category} <span class="count">({len(related)})</span></h3>'+case_list(related)+'</section>'
        write(f['page'],f['name'],body)
    for old,children in legacy_solver_pages:
        write(old['page'],old['name'],f'<h1>{E(old["category"])}</h1><ul>'+''.join(f'<li><a href="{f["page"]}">{E(f["name"])}</a></li>' for f in children)+'</ul>')
    # Old fine-item URLs continue to work and target the merged detail section.
    for n,f in owner.items():
        dest=f'{f["page"]}#detail-{n}'
        (ROOT/f'feature-source-{n:02d}.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={dest}"><title>{E(rows[n]["name"])}</title></head><body><a href="{dest}">{E(rows[n]["name"])}</a></body></html>',encoding='utf-8')
    groups=OrderedDict()
    for f in features:
        if f.get('show_on_home',True):groups.setdefault((f['module'],f['category']),[]).append(f)
    body='<div class="eyebrow">CAPABILITY INVENTORY</div><h1>Features</h1><div class="grid">'
    for (module,category),fs in groups.items():
        overall={'Mechanics':'LCA','Thermal':'Alpha'}.get(module,'')
        body+=f'<article class="card"><small>{E(module)} {badge(overall)}</small><h3>{E(category)}</h3>'
        for f in fs:
            body+=f'<div class="row" id="{f["id"]}"><span><a href="{f["page"]}">{E(f["name"])}</a></span>{badge(f["status"])}</div>'
            if f.get('output_fields'):body+=output_fields()
        body+='</article>'
    write('index.html','Features',body+'</div>')
    for alias,c in cases.items():
        category_page='feature-tests.html' if c['category']=='Feature tests' else 'application-cases.html'
        body=f'<a href="{category_page}">← {c["category"]}</a><h1>{E(c["display_alias"])}</h1><h2>{E(c["name"])}</h2><article class="card"><dl><dt>Status</dt><dd>{case_status(c)}</dd>'
        if c.get('mode'):body+=f'<dt>Mode</dt><dd><code>{E(c["mode"])}</code></dd>'
        for key,label in [('device','Device'),('background','Case background'),('adapt','Configuration'),('feature','Capabilities'),('flow','Execution flow'),('note','Execution notes')]:
            if c.get(key):body+=f'<dt>{label}</dt><dd>{E(c[key])}</dd>'
        if c.get('cmd'):body+='<dt>Commands</dt><dd><ol>'+''.join(f'<li><code>{E(x)}</code></li>' for x in c['cmd'])+'</ol></dd>'
        body+='</dl></article>'
        if alias in ('Backend_FlipChip','Submodeling'):
            url='assets/ppt-contours/slide-5-image-1.gif'
            body+=f'<h2>Flip-chip package</h2><div class="contour-gallery"><figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="Flip-chip package geometry illustration" loading="lazy"></a><figcaption>Package geometry illustration</figcaption></figure></div>'
        body+=result_content(alias,c['page'],features=features)
        if alias in CASE_IMAGES:
            heading,images=CASE_IMAGES[alias]
            body+=f'<h2>{E(heading)}</h2><div class="contour-gallery">'
            for filename,caption in images:
                url='assets/ppt-contours/'+filename
                body+=f'<figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="{E(caption)}" loading="lazy"></a><figcaption>{E(caption)}</figcaption></figure>'
            body+='</div>'
        if c.get('id')=='tsv':
            body+='<h2>Original input: seven three-stage chains</h2><table><thead><tr><th>Group</th><th>Geometry</th><th>Material / mesh</th><th>Thermal stress</th></tr></thead><tbody>'
            body+=''.join(f'<tr><td>{i+1}</td><td>n{i+5}_dvs.cmd</td><td>n{i+19}_sis.cmd</td><td>n{i+40}_sis.cmd</td></tr>' for i in range(7))+'</tbody></table>'
            body+='<p>46 CMD files: 21 n* files, 21 corresponding pp* copies and four common files. The n / pp pairs and cmd / cmd_flat copies were byte-compared; copies do not increase the case count.</p><p>Historical original-version run: 28 expanded Interconnect files and one expanded template passed syntax checks; all seven unique SDE geometries were generated. In the n5 → n19 → n40 chain, n19 took approximately 16 minutes 51 seconds and produced 1,005,445 points / 6,022,785 elements. n40 entered the mechanics solver but ran out of memory without producing a result TDR. This is not a result for the repository’s simplified version.</p>'
        if c.get('id'):
            paths=original['archive_cmd_entries'].get(c['id'],[])
            body+=f'<details><summary>CMD inventory ({len(paths)} physical entries, including historical copies)</summary><div class="paths">'+''.join(f'<div><code>{E(p)}</code></div>' for p in paths)+'</div></details>'
            if c.get('archive'):body+=f'<p><a href="../Resources/case-archive/{E(c["archive"])}">Download case archive</a></p>'
        if alias in ('Cantilever','Damascene'):
            write(c['page'],c['display_alias'],body)
            continue
        linked=[f for f in features if alias in f['related_cases']]
        body+='<h2>Related features</h2>'
        feature_groups=OrderedDict()
        for f in linked:
            feature_groups.setdefault(f['module'],OrderedDict()).setdefault(f['category'],[]).append(f)
        for module,categories in feature_groups.items():
            body+=f'<section class="related-feature-module"><h3>{E(module)}</h3><div class="grid">'
            for category,items in categories.items():
                body+=f'<article class="card"><h4>{E(category)}</h4><ul>'+''.join(f'<li><a href="{f["page"]}">{E(f["name"])}</a></li>' for f in items)+'</ul></article>'
            body+='</div></section>'
        if not linked:body+='<p>No related features recorded.</p>'
        write(c['page'],c['display_alias'],body)
    for category,page in [('Feature tests','feature-tests.html'),('Application cases','application-cases.html')]:
        group=[(a,c) for a,c in cases.items() if c['category']==category]
        body=f'<div class="eyebrow">CASE CATALOG</div><h1>{category}</h1><p class="count">{len(group)} cases</p>'
        sections=('Backend','User','Getting Started') if category=='Application cases' else ('',)
        for section in sections:
            entries=[(a,c) for a,c in group if not section or c['application_group']==section]
            if section:body+=f'<h2>{section} <span class="count">({len(entries)})</span></h2>'
            body+='<table><thead><tr><th>Abbreviation</th><th>Case</th><th>Mode</th><th>Status</th></tr></thead><tbody>'
            body+=''.join(f'<tr><td><a href="{c["page"]}"><b>{E(c["display_alias"])}</b></a></td><td>{E(c["name"])}</td><td><code>{E(c["mode"])}</code></td><td>{case_status(c)}</td></tr>' for a,c in entries)+'</tbody></table>'
        write(page,category,body)
    (ROOT/'test-cases.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=application-cases.html"><title>StressThermal cases</title></head><body><a href="feature-tests.html">Feature tests</a><a href="application-cases.html">Application cases</a></body></html>',encoding='utf-8')
    # A separate English reference view retains every field omitted from product pages.
    shots={p.stem.split('_')[-2]:p.name for p in (ROOT/'screenshots').glob('*.jpg')}
    body='<h1>Original table records</h1><p>GT library and customer case capability inventory.</p><ul><li>Backend cases model real scenarios and provide complete workflows for specific problems.</li><li>Training manual cases demonstrate individual capabilities.</li><li>Customer case collection: <code>/meda_tcad/sharefolder/0775/SI_user_examples/</code></li></ul><h2>Case records</h2>'
    for c in raw['cases']:
        body+=f'<article class="card detail"><h3>{c["row"]}. {E(c["alias"])}</h3><p>{E(c["name"])}</p><dl><dt>Original category</dt><dd>{E(WORDS.get(c["origin"],c["origin"]))}</dd><dt>Mode</dt><dd>{E(c["mode"])}</dd><dt>Path</dt><dd><code>{E(c["path"])}</code></dd><dt>Recorded status</dt><dd>{E(WORDS.get(c["source_status"],c["source_status"]))}</dd></dl>'
        if c.get('notes'):body+=f'<p>{E(SOURCE_CASE_NOTES[c["row"]])}</p>'
        if c.get('status_note'):body+='<p>The original status cell spans multiple rows: Not started.</p>'
        body+=f'<a href="screenshots/{E(shots[c["screenshot"]])}">Original screenshot</a></article>'
    body+='<h2>Existing catalog records</h2>'
    for c in cases.values():
        if not c.get('id'):continue
        body+=f'<article class="card detail"><h3>{E(c["alias"])}</h3><dl>'
        for k,label in [('source','Original context'),('original','Original input'),('adapt','Adaptation'),('note','Notes')]:body+=f'<dt>{label}</dt><dd>{E(c[k])}</dd>'
        body+='</dl></article>'
    body+='<h2>Detailed feature records</h2>'+''.join(detail(n)+f'<a href="{owner[n]["page"]}#detail-{n}">Open feature</a> · <a href="screenshots/{E(shots[rows[n]["screenshot"]])}">Original screenshot</a>' for n in rows)
    body+='<h2>Transcription notes</h2><ul><li>Row 1 is the header; feature records are numbered 2–60.</li><li>Manual page numbers in rows 18 and 32 are obscured by the pointer; visible portions are retained without guessing.</li><li>Rows 8 and 9 retain the original Mechanics mode. Row 52 retains the original status typo: not startnot started.</li><li>Recorded table statuses and existing catalog statuses remain separate.</li></ul><h2>Original screenshots</h2>'
    body+=''.join(f'<p><a href="screenshots/{E(name)}">Screenshot {code}</a></p>' for code,name in sorted(shots.items()))
    body+='<p><a href="source-table-data.json">Unmodified table transcription (JSON)</a> · <a href="catalog-data.json">Original catalog data (JSON)</a></p>'
    write('source-table.html','Original table records',body)
    write('progress.html','进度日志',progress_body())
    (ROOT/'catalog-merged.json').write_text(json.dumps(dict(features=features,cases=list(cases.values()),details=list(rows.values())),ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Rendered {len(features)} canonical features, 59 embedded details, {len(cases)} cases in English.')

if __name__=='__main__':render()
