"""Render independently addressable feature pages from the catalog inventory."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent


def render_features(modules, cases, badge, shell):
    # Preserve the user's finer feature grouping in every catalog rebuild.
    normalized = []
    for module, overall, title, rows in modules:
        expanded = []
        for name, status, case in rows:
            names = {
                'Elastic · isotropic / anisotropic': ['Isotropic elasticity', 'Anisotropic elasticity'],
                'Plane strain · 3D solid': ['Plane strain', '3D solid'],
            }.get(name, [name])
            expanded.extend((n, status, case) for n in names)
        if title == 'Nonlinearity & boundaries':
            normalized.extend([(module, overall, 'Nonlinearity', expanded[:2]),
                               (module, overall, 'Boundary conditions & constraints', expanded[2:])])
        else:
            normalized.append((module, overall, title, expanded))

    # Relationships describe the case's documented application, not a pass verdict.
    relationships = {
        'Quasistatic equilibrium': ['quasistatic', 'backend', 'submodel'],
        'Thermomechanical': ['backend', 'tsv', 'submodel'],
        'Thermal mismatch · intrinsic stress': ['backend', 'tsv', 'submodel'],
        'Prescribed displacement / rate · traction · pressure · point force': ['submodel', 'tsv'],
    }
    by_id = {c['id']: c for c in cases}
    cards, features = [], []
    esc = html.escape
    for module, overall, title, rows in normalized:
        content = []
        for name, status, old_case in rows:
            slug = re.sub(r'[^a-z0-9]+', '-', f'{module}-{title}-{name}'.lower()).strip('-')
            filename = f'feature-{slug}.html'
            related = relationships.get(name, [old_case] if old_case else [])
            feature = dict(id=slug, name=name, module=module, category=title,
                           status=status, case_ids=related, page=filename)
            features.append(feature)
            entries = []
            for case_id in related:
                c = by_id[case_id]
                entries.append(
                    f'<li class="card case"><h3><a href="case-{esc(case_id)}.html">{esc(c["name"])}</a></h3>'
                    f'<p>{esc(c["feature"])}</p><p class="sub">{esc(c["verify"])}</p></li>')
            listing = ('<ul style="list-style:none;padding:0">' + ''.join(entries) + '</ul>'
                       if entries else '<p class="card">暂无关联案例。</p>')
            body = (f'<a href="index.html#{slug}">← Features</a>'
                    f'<div class="eyebrow" style="margin-top:24px">{esc(module)} / {esc(title)}</div>'
                    f'<h1>{esc(name)}</h1>{badge(status)}'
                    f'<h2 style="margin-top:32px">关联案例 <span class="count">({len(related)})</span></h2>{listing}')
            (ROOT / filename).write_text(shell(name, body), encoding='utf-8')
            content.append(f'<div class="row" id="{slug}"><span><a href="{filename}">{esc(name)}</a></span>{badge(status)}</div>')
        cards.append(f'<article class="card"><small>{esc(module)} {badge(overall)}</small><h3>{esc(title)}</h3>{"".join(content)}</article>')
    body = '<div class="eyebrow">CAPABILITY INVENTORY</div><h1>Features</h1><div class="grid">' + ''.join(cards) + '</div>'
    (ROOT / 'index.html').write_text(shell('Features', body), encoding='utf-8')
    (ROOT / 'features-data.json').write_text(json.dumps(features, ensure_ascii=False, indent=2), encoding='utf-8')
    return features


if __name__ == '__main__':
    # Use the generator definitions without re-reading archives or running its checks.
    import ast
    source = ast.parse((ROOT / 'build_catalog.py').read_text(encoding='utf-8-sig'))
    definitions = []
    for node in source.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {'modules', 'css'} for t in node.targets):
            definitions.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in {'badge', 'shell'}:
            definitions.append(node)
    namespace = {'esc': html.escape}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), 'catalog-definitions', 'exec'), namespace)
    cases = json.loads((ROOT / 'catalog-data.json').read_text(encoding='utf-8'))['cases']
    features = render_features(namespace['modules'], cases, namespace['badge'], namespace['shell'])
    print(f'Rendered {len(features)} feature pages and index.html')
