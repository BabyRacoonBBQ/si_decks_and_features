"""Check imported row coverage and local navigation without running solvers."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import json

root = Path(__file__).resolve().parent
data = json.loads((root/'source-table-data.json').read_text(encoding='utf-8'))
assert [f['row'] for f in data['features']] == list(range(2,61))
aliases = {c['alias'] for c in data['cases']}
assert len(aliases)==18
assert all(a in aliases or a=='all' for f in data['features'] for a in f['case_aliases'])

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self, tag, attrs):
        for key,value in attrs:
            if key in ('href','src'): self.links.append(value)

missing=[]
for path in root.glob('*.html'):
    parser=Links()
    parser.feed(path.read_text(encoding='utf-8'))
    for href in parser.links:
        url=urlsplit(href)
        if not url.scheme and url.path and not (path.parent/unquote(unescape(url.path))).exists():
            missing.append((path.name,href))
assert not missing, missing
crosslinks=json.loads((root/'catalog-crosslinks.json').read_text(encoding='utf-8'))
assert len(crosslinks['cases'])==25
assert len(crosslinks['original_features'])==49
assert len(crosslinks['source_features'])==59
merged=json.loads((root/'catalog-merged.json').read_text(encoding='utf-8'))
features=merged['features']
assert sorted({n for f in features for n in f['details']})==list(range(2,61))
home=(root/'index.html').read_text(encoding='utf-8')
assert 'Geometry &amp; mesh' not in home
assert all(f['page'] in home for f in features if f.get('show_on_home',True))
assert not [f['name'] for f in features if f.get('show_on_home',True)
            and any(separator in f['name'] for separator in (' · ',' / ',' & ',' and '))]
for f in features:
    assert len(f['related_cases'])==len(set(f['related_cases']))
    page=(root/f['page']).read_text(encoding='utf-8')
    assert page.count('<h2>Related cases ')==1
for c in merged['cases']:
    page=(root/c['page']).read_text(encoding='utf-8')
    assert '<dt>Mode</dt>' in page
    assert 'class="case-status status-' in page
    assert '原表' not in page
assert sum((root/p).read_text(encoding='utf-8').count('class="case-status status-') for p in ['feature-tests.html','application-cases.html'])==25+sum(c.get('integrated',False) for c in merged['cases'])
tsv=next(c for c in merged['cases'] if c['alias']=='TSV_Local')
assert tsv['integrated'] and tsv['verify'].startswith('Matched')
print(f'PASS: 59 detailed records, {len(features)} canonical features, 25 case pages with Mode and status tags, unique related-case lists, and all local links.')
