"""Split case details from the searchable case index."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent


def render_case_pages(cases, shell):
    source = (ROOT / 'test-cases.html').read_text(encoding='utf-8')
    rows = []
    for case in cases:
        cid = case['id']
        filename = f'case-{cid}.html'
        pattern = rf'<article class="card case" id="{re.escape(cid)}".*?</article>'
        match = re.search(pattern, source, re.S)
        if match:
            detail = match.group(0)
        else:
            existing = (ROOT / filename).read_text(encoding='utf-8')
            detail = re.search(pattern, existing, re.S).group(0)
        body = f'<a href="test-cases.html">← Test cases</a>{detail}'
        (ROOT / filename).write_text(shell(html.escape(case['name']), body), encoding='utf-8')
        rows.append(f'<tr data-kind="{html.escape(case["kind"])}"><td><a href="{filename}">{html.escape(case["name"])}</a></td>'
                    f'<td>{html.escape(case["kind"])}</td><td>{html.escape(case["verify"])}</td></tr>')
    kinds = ''.join(f'<option>{html.escape(k)}</option>' for k in dict.fromkeys(c['kind'] for c in cases))
    body = ('<div class="eyebrow">CASE CATALOG</div><h1>Test cases</h1>'
            '<div class="toolbar"><input id="search" aria-label="搜索案例" placeholder="搜索案例…">'
            f'<select id="kind" aria-label="来源筛选"><option value="">全部来源</option>{kinds}</select></div>'
            f'<p class="count" id="count">{len(cases)} 个案例</p>'
            '<table><thead><tr><th>案例</th><th>来源类别</th><th>验证状态</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table><p id="empty" hidden>没有匹配的案例。</p>'
            '<script>const search=document.querySelector("#search"),kind=document.querySelector("#kind");'
            'function filter(){let n=0;document.querySelectorAll("tbody tr").forEach(row=>{'
            'const show=(!kind.value||row.dataset.kind===kind.value)&&row.textContent.toLowerCase().includes(search.value.toLowerCase());'
            'row.hidden=!show;if(show)n++});document.querySelector("#count").textContent=n+" 个案例";'
            'document.querySelector("#empty").hidden=n!==0}search.addEventListener("input",filter);kind.addEventListener("change",filter);</script>')
    (ROOT / 'test-cases.html').write_text(shell('Test cases', body), encoding='utf-8')


if __name__ == '__main__':
    import ast
    tree = ast.parse((ROOT / 'build_catalog.py').read_text(encoding='utf-8-sig'))
    selected = [n for n in tree.body if
                (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'css' for t in n.targets))
                or (isinstance(n, ast.FunctionDef) and n.name == 'shell')]
    ns = {}
    exec(compile(ast.Module(body=selected, type_ignores=[]), 'catalog-shell', 'exec'), ns)
    cases = json.loads((ROOT / 'catalog-data.json').read_text(encoding='utf-8'))['cases']
    render_case_pages(cases, ns['shell'])
    print(f'Rendered {len(cases)} case pages and table index')
