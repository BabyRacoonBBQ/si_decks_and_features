from pathlib import Path
import json,hashlib
root=Path('/home/mozztcad/tmp/catalog-svisual')
base=Path('/home/mozztcad/si_workspace/integration-20261007/validation02')
records=json.loads((base/'results.json').read_text())
lines=[]; manifest=[]
for n in range(5,12):
 p=base/f'TSV_n{n}/local/n{n+35}_tsv_sis.tdr'
 record=next(r for r in records if r['case']==f'TSV_n{n}')
 comparison=next(c for c in record['comparisons'] if c['candidate']==str(p))
 assert comparison['accepted'] and hashlib.sha256(p.read_bytes()).hexdigest()==comparison['candidate_sha256']
 manifest.append(comparison)
 lines += [f'set d [load_file {{{p}}}]', 'puts [list_fields -dataset $d]']
 for i,field in enumerate(['MisesStress','Abs(Displacement-V)'],1):
  lines += ['set p [create_plot -dataset $d]', f'set_field_prop {{{field}}} -plot $p -show_bands -show -scale linear',f'set_plot_prop -plot $p -title {{TSV n{n}: {field}}} -show_title -show_legend -bg_solid -color_bg #ffffff',f'export_view {{TSV_n{n}-{i}.png}} -plots $p -format png -resolution 1400x1000 -overwrite','remove_plots $p']
 lines += [f'unload_file {{{p}}}']
(root/'tsv.tcl').write_text('\n'.join(lines+['exit']))
(root/'tsv-manifest.json').write_text(json.dumps(manifest,indent=2))
