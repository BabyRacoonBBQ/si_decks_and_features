"""File preview with a persistent return link, compatible with file:// pages."""
from pathlib import Path
from html import escape as E
import os

def preview_url(artifact,case_page):
    root=Path(__file__).resolve().parent
    original=root/artifact['url']
    preview=original.with_name(original.name+'.preview.html')
    back=Path(os.path.relpath(root/case_page,preview.parent)).as_posix()+'#gt-a'
    label=artifact['label'].replace('ANSYS','GT-A')
    preview.write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(label)} · StressThermal</title>
<style>html,body{{height:100%;margin:0}}body{{display:flex;flex-direction:column;font:16px "Segoe UI",sans-serif;background:white}}header{{display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding:16px 24px;background:#152f40;color:white}}header a{{color:#a0e6ef}}header strong{{flex:1}}iframe{{width:100%;flex:1;min-height:0;border:0}}</style></head>
<body><header><a href="{E(back)}" target="_self">← Back to case</a><strong>{E(label)}</strong><a href="{E(original.name)}" download>Download</a></header>
<iframe title="{E(label)}" src="{E(original.name)}"></iframe></body></html>''',encoding='utf-8')
    return preview.relative_to(root).as_posix()
