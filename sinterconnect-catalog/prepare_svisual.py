"""Run on the VM to prepare bounded, sequential SVisual exports."""
from pathlib import Path
import json, hashlib
root=Path('/home/mozztcad/tmp/catalog-svisual')
base=Path('/home/mozztcad/si_workspace/integration-20261007/validation02')
cases={
 'Damascene':base/'DualDamascene/n3_sis.tdr',
 'Cantilever':base/'3D_Cantilever/local/n4_sis.tdr',
 '3D_Interconnect':base/'3D_Interconnect/n12_final_sis.tdr',
 'Inverter':base/'Inverter/n@node@_sis.tdr',
}
lines=[];manifest=[]
for alias,path in cases.items():
 manifest.append(dict(alias=alias,tdr=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 lines+= [f'set d [load_file {{{path}}}]',f'puts "FIELDS {alias}: [list_fields -dataset $d]"',f'unload_file {{{path}}}']
lines+=['exit']
(root/'fields.tcl').write_text('\n'.join(lines))
(root/'tdr-manifest.json').write_text(json.dumps(manifest,indent=2))
plots=[]
for alias,path in cases.items():
 fields={'Damascene':['MisesStress','Temperature','Potential'],
         'Cantilever':['MisesStress','Abs(Displacement-V)'],
         '3D_Interconnect':['MisesStress','Temperature','Potential'],
         'Inverter':['Potential','Abs(ElectricField-V)']}[alias]
 plots += [f'set d [load_file {{{path}}}]',f'puts "FIELDS {alias}: [list_fields -dataset $d]"']
 for i,field in enumerate(fields):
  plots += ['set p [create_plot -dataset $d]',
    f'set_field_prop {{{field}}} -plot $p -show_bands -show -scale linear',
    f'set_plot_prop -plot $p -title {{{alias}: {field}}} -show_title -show_legend -bg_solid -color_bg #ffffff',
    f'export_view {{{alias}-{i+1}.png}} -plots $p -format png -resolution 1400x1000 -overwrite',
    'remove_plots $p']
 plots += [f'unload_file {{{path}}}']
(root/'render.tcl').write_text('\n'.join(plots+['exit']))
(root/'run.sh').write_text('''#!/bin/bash
export STROOT_ARCH_OS=/home/mozztcad/synopsys/sentaurus/W-2024.09-SP1/tcad/W-2024.09-SP1/linux64
export STROOT_ARCH_OS_LIB=$STROOT_ARCH_OS/lib
export LD_LIBRARY_PATH=$STROOT_ARCH_OS/lib:$STROOT_ARCH_OS/tcad_mpi_mpich_ifort/lib
export RES_OPTIONS="attempts:1 timeout:1"
export OMP_NUM_THREADS=2
cd /home/mozztcad/tmp/catalog-svisual
timeout -k 5 55 "$STROOT_ARCH_OS/bin/svisual" -bx -mesa -threads 2 -tcl "$1"
''')
print('Prepared four retained result TDRs.')
