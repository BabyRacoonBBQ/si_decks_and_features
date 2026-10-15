"""Add the photographed source tables without replacing the local inventory."""
from pathlib import Path
import ast
import html
import json
import re

ROOT = Path(__file__).resolve().parent
esc = html.escape
ALIASES = dict(tsv='TSV_Local', backend='Package_Reliability', submodel='Submodeling',
               quasistatic='Quasistatic', buckling='Linear_Buckling',
               postbuckling='Post_Buckling', deformation='Large_Deformation')


def definitions():
    tree = ast.parse((ROOT/'build_catalog.py').read_text(encoding='utf-8-sig'))
    nodes = [n for n in tree.body if
             (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {'css','modules'} for t in n.targets))
             or (isinstance(n, ast.FunctionDef) and n.name in {'shell','badge'})]
    ns = {'esc': esc}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'catalog-definitions', 'exec'), ns)
    return ns


def append_section(path, body):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<!-- source-table-start -->.*?<!-- source-table-end -->', '', text, flags=re.S)
    section = '<!-- source-table-start -->' + body + '<!-- source-table-end -->'
    path.write_text(text.replace('</main>', section+'</main>'), encoding='utf-8')


def render_source_catalog():
    ns = definitions()
    shell, badge = ns['shell'], ns['badge']
    data = json.loads((ROOT/'catalog-data.json').read_text(encoding='utf-8'))
    original_cases = data['cases']
    original_features = json.loads((ROOT/'features-data.json').read_text(encoding='utf-8'))
    table = json.loads((ROOT/'source-table-data.json').read_text(encoding='utf-8'))
    source_cases = {c['alias']: c for c in table['cases']}
    screenshots = {p.stem.split('_')[-2]:p.name for p in (ROOT/'screenshots').glob('*.jpg')}
    def image_link(code):
        return f'<a href="screenshots/{esc(screenshots[code])}" target="_blank">原图 ↗</a>'
    def case_page(alias):
        return 'case-source-'+alias.lower().replace('_','-')+'.html'
    def feature_page(n):
        return f'feature-source-{n:02d}.html'
    def related_aliases(f):
        return list(source_cases) if f['case_aliases']==['all'] else f['case_aliases']
    def case_list(aliases):
        if not aliases:
            return '<p>原表未列出关联案例。</p>'
        return '<ul>'+''.join(f'<li><a href="{case_page(a)}"><b>{esc(a)}</b></a> — {esc(source_cases[a]["name"])}</li>' for a in aliases)+'</ul>'
    def feature_list(features):
        return '<ul>'+''.join(f'<li><a href="{feature_page(f["row"])}">{esc(f["name"])}</a> <small>#{f["row"]}</small></li>' for f in features)+'</ul>'

    for f in table['features']:
        module = ('Thermal' if f['category'] in {'Heat transfer & materials','Boundary & interface conditions'} else
                  'Coupled / Electrical' if f['category']=='Analysis modes' else
                  'Numerics' if f['category']=='Solver components' else
                  'General' if f['category'] in {'Geometry & mesh','Scripting & data exchange','Post-processing & output'} else 'Mechanics')
        f['module'] = module
        f['page'] = feature_page(f['row'])
        body = (f'<a href="index.html">← Features</a><div class="eyebrow" style="margin-top:24px">{module} / {esc(f["category"])}</div>'
                f'<h1>{esc(f["name"])}</h1><p>原表 #{f["row"]} · {esc(f["original_category"])}</p>'
                f'<article class="card"><dl><dt>原表完成度</dt><dd>{esc(f["source_status"])}</dd>'
                f'<dt>开发难度 / 耗时</dt><dd>{esc(f["difficulty"])}</dd><dt>原表 mode</dt><dd>{esc(f["mode"])}</dd>'
                f'<dt>命令 / 原表说明</dt><dd><pre style="white-space:pre-wrap;overflow-wrap:anywhere">{esc(f["commands"])}</pre></dd>'
                f'<dt>功能描述 / 手册引用</dt><dd>{esc(f["reference"])}</dd></dl>{image_link(f["screenshot"])}</article>'
                '<h2 style="margin-top:28px">关联案例</h2>'
                + ('<p>原表：all</p>' if f['case_aliases']==['all'] else '') + case_list(related_aliases(f)))
        (ROOT/f['page']).write_text(shell(esc(f['name']),body),encoding='utf-8')

    # Keep original case identities separate from source-library originals.
    for c in table['cases']:
        fs = [f for f in table['features'] if c['alias'] in related_aliases(f)]
        body = (f'<a href="test-cases.html">← Test cases</a><h1>{esc(c["alias"])}</h1><h2>{esc(c["name"])}</h2>'
                f'<article class="card"><dl><dt>原表编号 / 来源</dt><dd>{c["row"]} / {esc(c["origin"])}</dd>'
                f'<dt>Mode</dt><dd><code>{esc(c["mode"])}</code></dd>'
                f'<dt>原始路径</dt><dd><code>{esc(c["path"])}</code></dd>'
                f'<dt>原表开发状态</dt><dd>{esc(c["source_status"])}</dd></dl>'
                + (f'<p>{esc(c["notes"])}</p>' if c.get('notes') else '')
                + (f'<p class="sub">{esc(c["status_note"])}</p>' if c.get('status_note') else '')
                + image_link(c['screenshot'])+'</article><h2 style="margin-top:28px">关联 Features</h2>'+feature_list(fs))
        (ROOT/case_page(c['alias'])).write_text(shell(esc(c['alias']),body),encoding='utf-8')

    # Link coarse existing features to their finer source-table items, without replacing them.
    mapping = {
        'Quasistatic equilibrium':[21], 'Linear buckling':[26,60], 'Post-buckling':[27],
        'Plastic & viscoplastic':[13,14], 'Viscous & viscoelastic':[17],
        'First / second order':[20], 'Thermal mismatch · intrinsic stress':[15],
        'Fluid surface tension / pressure':[25], 'Geometric nonlinearity':[28],
        'Mechanical contact · crack analysis':[52],
        'Prescribed displacement / rate · traction · pressure · point force':[2,3,4,5,6,7,11,12],
        'Coupling · beam-plate coupling · variable boundary':[24],
        'Steady-state · transient':[33], 'Conductivity · heat storage · emissivity':[16],
        'Prescribed temperature · ramps · heat flux · contact power':[9,57], 'Thermal resistor':[8],
        'Thermomechanical':[37], 'Electrical current · electrostatic':[10,18,34,35,38,39],
        'Electrothermal':[36], 'TRBDF · Newton · direct / iterative solvers':[22,23,30,56],
        'ARPACK / MUMPS recovery: see linear buckling':[60],
    }
    for f in original_features:
        fine = [item for item in table['features'] if item['row'] in mapping.get(f['name'],[])]
        if fine:
            aliases = list(dict.fromkeys(a for item in fine for a in related_aliases(item)))
            append_section(ROOT/f['page'], '<h2 style="margin-top:28px">原表功能细项</h2>'+feature_list(fine)
                           +'<h2>原表关联案例</h2>'+case_list(aliases))
        # Retain full names while adding the local case's fixed alias.
        page = ROOT/f['page']
        content = page.read_text(encoding='utf-8')
        for c in original_cases:
            content = content.replace(f'>{esc(c["name"])}</a>',f'>{ALIASES[c["id"]]} — {esc(c["name"])}</a>')
        page.write_text(content,encoding='utf-8')

    for c in original_cases:
        fs = [f for f in original_features if c['id'] in f['case_ids']]
        links = '<ul>'+''.join(f'<li><a href="{f["page"]}">{esc(f["name"])}</a></li>' for f in fs)+'</ul>'
        append_section(ROOT/f'case-{c["id"]}.html',f'<p>缩写名：<b>{ALIASES[c["id"]]}</b></p><h2>关联 Features</h2>'+links)

    groups = {}
    for f in original_features:
        groups.setdefault((f['module'],f['category']),[]).append(f)
    for f in table['features']:
        groups.setdefault((f['module'],f['category']),[]).append(dict(name=f['name'],page=f['page'],status='',source_row=f['row']))
    cards = ''
    for (module,category),fs in groups.items():
        rows = ''.join(f'<div class="row" id="{esc(f.get("id", "source-"+str(f.get("source_row", ""))))}"><span><a href="{f["page"]}">{esc(f["name"])}</a>'
                       + (f'<br><small>原表 #{f["source_row"]}</small>' if 'source_row' in f else '')
                       + f'</span>{badge(f["status"])}</div>' for f in fs)
        overall = {'Mechanics':'LCA', 'Thermal':'Alpha'}.get(module, '')
        cards += f'<article class="card"><small>{esc(module)} {badge(overall)}</small><h3>{esc(category)}</h3>{rows}</article>'
    (ROOT/'index.html').write_text(shell('Features','<div class="eyebrow">CAPABILITY INVENTORY</div><h1>Features</h1>'
        '<p><a href="source-table.html">原始表格</a></p><div class="grid">'+cards+'</div>'),encoding='utf-8')

    entries = [dict(alias=ALIASES[c['id']],name=c['name'],origin=c['kind'],status=c['verify'],page=f'case-{c["id"]}.html',label='现有目录') for c in original_cases]
    entries += [dict(alias=c['alias'],name=c['name'],origin=c['origin'],status=c['source_status'],page=case_page(c['alias']),label='原表') for c in table['cases']]
    rows = ''.join(f'<tr data-kind="{esc(c["origin"])}"><td><a href="{c["page"]}"><b>{esc(c["alias"])}</b></a></td>'
                   f'<td>{esc(c["name"])}</td><td>{esc(c["origin"])}</td><td><small>{c["label"]}</small><br>{esc(c["status"])}</td></tr>' for c in entries)
    kinds=''.join(f'<option>{esc(k)}</option>' for k in dict.fromkeys(c['origin'] for c in entries))
    body = '<div class="eyebrow">CASE CATALOG</div><h1>Test cases</h1><p><a href="source-table.html">原始表格</a></p>'
    body += f'<div class="toolbar"><input id="search" aria-label="搜索案例" placeholder="搜索缩写名、案例或来源…"><select id="kind" aria-label="来源筛选"><option value="">全部来源</option>{kinds}</select></div>'
    body += f'<p class="count" id="count">{len(entries)} 个案例记录</p><div style="overflow-x:auto"><table><thead><tr><th>缩写名</th><th>完整名称</th><th>来源类别</th><th>状态</th></tr></thead><tbody>{rows}</tbody></table></div><p id="empty" hidden>没有匹配的案例。</p>'
    body += '''<script>const search=document.querySelector('#search'),kind=document.querySelector('#kind');function filter(){let n=0;document.querySelectorAll('tbody tr').forEach(r=>{r.hidden=!((!kind.value||r.dataset.kind===kind.value)&&r.textContent.toLowerCase().includes(search.value.toLowerCase()));if(!r.hidden)n++});document.querySelector('#count').textContent=n+' 个案例记录';document.querySelector('#empty').hidden=n!==0}search.addEventListener('input',filter);kind.addEventListener('change',filter);</script>'''
    (ROOT/'test-cases.html').write_text(shell('Test cases',body),encoding='utf-8')

    # Complete original columns remain available alongside the reorganized views.
    body='<h1>'+esc(table['title'])+'</h1><ul>'+''.join('<li>'+esc(t)+'</li>' for t in table['source_notes'])+'</ul>'
    body+='<h2>案例</h2><div style="overflow-x:auto"><table><thead><tr><th>#</th><th>例子名</th><th>案例来源</th><th>缩写</th><th>mode</th><th>路径</th><th>当前开发状态（原表）</th><th>原图</th></tr></thead><tbody>'
    for c in table['cases']:
        body+=f'<tr><td>{c["row"]}</td><td>{esc(c["name"])}<p>{esc(c.get("notes",""))}</p></td><td>{esc(c["origin"])}</td><td><a href="{case_page(c["alias"])}">{esc(c["alias"])}</a></td><td>{esc(c["mode"])}</td><td><code>{esc(c["path"])}</code></td><td>{esc(c["source_status"])}</td><td>{image_link(c["screenshot"])}</td></tr>'
    body+='</tbody></table></div><h2>功能点梳理</h2><div style="overflow-x:auto"><table><thead><tr><th>#</th><th>功能分类</th><th>功能点</th><th>命令</th><th>功能描述</th><th>涉及案例</th><th>开发难度/耗时</th><th>mode</th><th>完成度</th><th>HTML 分类</th><th>原图</th></tr></thead><tbody>'
    for f in table['features']:
        body+=f'<tr><td>{f["row"]}</td><td>{esc(f["original_category"])}</td><td><a href="{f["page"]}">{esc(f["name"])}</a></td><td><pre style="white-space:pre-wrap;min-width:260px">{esc(f["commands"])}</pre></td><td>{esc(f["reference"])}</td><td>{esc(", ".join(f["case_aliases"]))}</td><td>{esc(f["difficulty"])}</td><td>{esc(f["mode"])}</td><td>{esc(f["source_status"])}</td><td>{esc(f["category"])}</td><td>{image_link(f["screenshot"])}</td></tr>'
    body+='</tbody></table></div><details><summary>原图与转录备注</summary><ul>'+''.join('<li>'+esc(t)+'</li>' for t in table['transcription_notes'])+'</ul>'
    body+=''.join(f'<p>{image_link(code)}</p>' for code in sorted(screenshots))+'</details>'
    (ROOT/'source-table.html').write_text(shell(esc(table['title']),body),encoding='utf-8')
    (ROOT/'catalog-crosslinks.json').write_text(json.dumps(dict(cases=entries,original_features=original_features,source_features=table['features']),ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Preserved {len(original_cases)} existing cases / {len(original_features)} features; added {len(source_cases)} source cases / {len(table["features"])} features.')
    from render_english_catalog import render
    render()


if __name__=='__main__':
    render_source_catalog()
