"""Maintain case-specific ANSYS artifacts without inventing equivalent decks."""
from pathlib import Path
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parent
CONVERTER=Path('D:/my_repos/si_to_ans_converter')

def main():
    cases=json.loads((ROOT/'catalog-merged.json').read_text(encoding='utf-8'))['cases']
    records={}
    for case in cases:
        alias=case['alias']
        records[alias]=dict(tool='ANSYS',status='Pending',equivalence='Not validated',files=[],
            next_step='Locate the matching CMD and solve-time mesh, convert supported semantics, then compare ANSYS results.')
    folder=ROOT/'assets/gt-a/Cantilever'
    folder.mkdir(parents=True,exist_ok=True)
    artifacts=[
      ('test/3d_cantilever/ansys_mapdl/3D_Cantilever_sis.apdl','Cantilever.apdl','APDL script (existing converter output)'),
      ('test/3d_cantilever/sinterconnect/output-5/3D_Cantilever_sis.cdb','Cantilever.cdb','CDB model (current converter format)'),
      ('test/3d_cantilever/sinterconnect/output-5/3D_Cantilever_sis.cdb.converter.log','conversion.log','Conversion log'),
      ('test/3d_cantilever/sinterconnect/3D_Cantilever_sis.cmd','input.cmd','Conversion input CMD'),
      ('test/3d_cantilever/ansys_mapdl/3d_cantilever_sis.out','ansys-run.out','Historical ANSYS run log'),
    ]
    c=records['Cantilever'];c.update(status='Converted',
      note='An existing APDL script and a successful CDB conversion are available. The APDL directory contains a completed historical MAPDL run. The newer CDB conversion records solver_validation: not run. Numerical equivalence and identity with the displayed TDR variant have not been established.')
    for relative,name,label in artifacts:
        src=CONVERTER/relative;dst=folder/name
        shutil.copy2(src,dst)
        c['files'].append(dict(label=label,url=dst.relative_to(ROOT).as_posix(),
          source=str(src),sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
    c['mesh_source']=str(CONVERTER/'test/3d_cantilever/sinterconnect/3D_cantilever_pre_solve_sis.tdr')
    c['mesh_sha256']=hashlib.sha256(Path(c['mesh_source']).read_bytes()).hexdigest()
    (ROOT/'gt-a-cases.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    for alias,record in records.items():
        folder=ROOT/'assets/gt-a'/alias;folder.mkdir(parents=True,exist_ok=True)
        (folder/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Maintained {len(records)} ANSYS case records; Cantilever artifacts imported; remaining cases pending.')

if __name__=='__main__':main()
