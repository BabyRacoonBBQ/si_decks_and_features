"""Export the retained tetrahedra and nodal results for the local VTK.js viewer."""
from pathlib import Path
import base64
import hashlib
import json
import numpy as np
from prepare_damascene_report import read_stage, SOLIDS, COLORS, OUT


def packed(values, dtype):
    array = np.asarray(values, dtype=dtype).ravel()
    assert np.isfinite(array).all()
    return dict(type='Float32Array' if dtype == '<f4' else 'Uint32Array',
                length=int(array.size), data=base64.b64encode(array.tobytes()).decode('ascii'))


def boundary_faces(points, tetrahedra):
    faces, inside = [], []
    for a, b, c, opposite in [(0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 3, 1), (1, 2, 3, 0)]:
        faces.append(tetrahedra[:, [a, b, c]])
        inside.append(tetrahedra[:, opposite])
    faces, inside = np.concatenate(faces), np.concatenate(inside)
    _, indices, counts = np.unique(np.sort(faces, axis=1), axis=0, return_index=True, return_counts=True)
    assert np.max(counts) <= 2
    indices = indices[counts == 1]
    faces, inside = faces[indices], inside[indices]
    q = points[faces]
    normals = np.cross(q[:, 1] - q[:, 0], q[:, 2] - q[:, 0])
    inward = (normals * (points[inside] - q[:, 0])).sum(axis=1) > 0
    faces[inward] = faces[inward][:, [0, 2, 1]]
    return faces


def main():
    stages = {n: read_stage(n) for n in (1, 2, 3)}
    p, regions, _ = stages[3]
    for n in (1, 2):
        assert np.array_equal(p, stages[n][0])
    items = []
    for rid in SOLIDS:
        r = regions[rid]
        ids = r['ids']
        source_points = p[ids]
        # Display coordinates Z, Y, -X: a rigid, right-handed transform in µm.
        points = source_points[:, [2, 1, 0]] * [1, 1, -1]
        tetrahedra = np.searchsorted(ids, r['conn'])
        faces = boundary_faces(points, tetrahedra)
        polygons = np.column_stack([np.full(len(faces), 3), faces])
        states = {}
        for n in (1, 2, 3):
            rr = stages[n][1][rid]
            assert np.array_equal(rr['ids'], ids)
            assert np.array_equal(rr['conn'], r['conn'])
            fields = rr['fields']
            values = dict(stress=fields['MisesStress'][:, 0] * 1e-7,
                          temperature=fields['Temperature'][:, 0] - 273.156)
            if n == 3 and r['material'] == 'Copper':
                values['potential'] = fields['Potential'][:, 0]
            states[str(n)] = {key: packed(value, '<f4') for key, value in values.items()}
        items.append(dict(id=rid, name=r['name'], material=r['material'], color=COLORS[r['material']],
                          points=packed(points, '<f4'), tetrahedra=packed(tetrahedra, '<u4'),
                          polygons=packed(polygons, '<u4'), states=states))
    model = dict(schemaVersion=1, id='damascene', title='Dual-damascene interconnect',
                 coordinateUnit='μm', axes=['Z', 'Y', '−X'],
                 bounds=[0, .7, -.1, .05, -.1, .7], sectionRange=[-.1, .05], sectionDefault=.04,
                 stages=[dict(id='1', label='After fabrication · 250°C'),
                         dict(id='2', label='After cooldown · 25°C'),
                         dict(id='3', label='Operating state · 1 s')], regions=items)
    target = OUT / 'vtk-model.js'
    target.write_text('window.SIMULATION_MODELS = window.SIMULATION_MODELS || {};\n'
                      'window.SIMULATION_MODELS.damascene = ' + json.dumps(model, separators=(',', ':'), allow_nan=False) + ';\n',
                      encoding='utf-8')
    audit = dict(export=target.name, sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                 source=[dict(file=f'n{n}_sis.tdr', sha256=hashlib.sha256((OUT / f'source/n{n}_sis.tdr').read_bytes()).hexdigest()) for n in (1,2,3)],
                 region_count=len(items), tetrahedra=sum(len(regions[r]['conn']) for r in SOLIDS),
                 transform='display = (Z, Y, -X) in micrometers',
                 stress_conversion='dyn/cm² × 1e-7 → MPa', celsius_offset=273.156,
                 topology='All solid tetrahedra retained; boundary faces oriented outward; no decimation',
                 fields='Float32 region-local nodal fields; no cross-material averaging; Gas excluded')
    (OUT / 'vtk-export.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    print(json.dumps(dict(file=str(target), bytes=target.stat().st_size, regions=len(items), tetrahedra=audit['tetrahedra'])))


if __name__ == '__main__':
    main()
