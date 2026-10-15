"""Chinese release and development log, maintained separately from case data."""
from pathlib import Path
import json
from html import escape as E

def progress_body():
    data=json.loads(Path(__file__).with_name('progress-log.json').read_text(encoding='utf-8'))
    body='<div lang="zh-CN"><h1>进度日志</h1>'
    for week in data['weeks']:
        body+=f'<section><h2>{E(week["start"])} — {E(week["end"])}</h2><ul>'
        for entry in week['entries']:
            text=entry.get('release_note',entry['title'])
            body+=f'<li style="margin:12px 0"><a href="{E(entry["page"])}">{E(text)}</a></li>'
        body+='</ul></section>'
    return body+'</div>'
