"""Read retained DualDamascene artifacts and draw case figures; no solver runs."""
from pathlib import Path
import hashlib
import json
import re
import os

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'assets/case-reports/damascene'
os.environ.setdefault('MPLCONFIGDIR', str(OUT / '.mpl-cache'))
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

COLORS = {'Silicon': '#96a8bc', 'Nitride': '#568a93', 'Oxide': '#dde7e9', 'Copper': '#c78040'}
SOLIDS = [0, 1, 2, 4, 5, 6]
EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def read_stage(n):
    with h5py.File(OUT / f'source/n{n}_sis.tdr') as source:
        col = source['collection']
        assert col.attrs['TDR HDF5 version'] == 16
        g = col['geometry_0']
        assert g.attrs['unit:name'] == b'cm'
        assert float(g.attrs['unit:significand']) == 1
        assert np.all(g['offset'][:] == 0)
        assert np.array_equal(g['transformation/A'][:].reshape(3, 3), np.eye(3))
        assert np.all(g['transformation/b'][:] == 0)
        v = g['vertex'][:]
        points = np.column_stack([v[k] for k in 'xyz']) * 1e4
        regions = {}
        for k, r in g.items():
            if not k.startswith('region_'):
                continue
            typ = int(r.attrs['type'])
            raw = r['elements_0'][:].reshape(-1, 5 if typ == 0 else 4)
            assert np.all(raw[:, 0] == (5 if typ == 0 else 2))
            conn = raw[:, 1:].astype(int)
            regions[int(k[7:])] = dict(name=r.attrs['name'].decode(),
                material=r.attrs.get('material', b'').decode(), type=typ,
                conn=conn, ids=np.unique(conn), fields={})
        fields = []
        for key, d in g['state_0'].items():
            if not key.startswith('dataset_'):
                continue
            rid = int(d.attrs['region'])
            name = d.attrs['name'].decode()
            expected_units = {'MisesStress': (b'dyn*cm^-2', .1),
                              'Temperature': (b'K', 1.), 'Potential': (b'V', 1.)}
            if name in expected_units:
                unit, factor = expected_units[name]
                assert d.attrs['unit:name'] == unit
                assert float(d.attrs['conversion factor']) == factor
                assert float(d.attrs['unit:significand']) == 1.
                assert int(d.attrs['location type']) == 0
                assert int(d.attrs['structure type']) == 0
            data = d['values'][:]
            location = int(d.attrs['location type'])
            rows = int(d.attrs['number of values'])
            assert len(data) % rows == 0
            data = data.reshape(rows, -1)
            if location == 0:
                assert len(data) == len(regions[rid]['ids'])
            regions[rid]['fields'][name] = data
            fields.append(dict(path=d.name, name=name, region=rid,
                location=location, unit=d.attrs.get('unit:name', b'').decode(), count=rows))
        return points, regions, fields


def cut(points, r, y=.04, field=None):
    """Intersect volume tetrahedra with Y=constant; interpolate nodal scalar."""
    conn = r['conn']
    coords = points[conn]
    selected = (coords[:, :, 1].min(1) < y - 1e-10) & (coords[:, :, 1].max(1) > y + 1e-10)
    polygons, values = [], []
    lookup = None
    if field is not None:
        lookup = np.full(len(points), np.nan)
        lookup[r['ids']] = field
    for tet, q in zip(conn[selected], coords[selected]):
        vertices, samples = [], []
        for a, b in EDGES:
            da, db = q[a, 1] - y, q[b, 1] - y
            if da * db < 0:
                t = -da / (db - da)
                xyz = q[a] + t * (q[b] - q[a])
                vertices.append([xyz[2], -xyz[0]])
                if lookup is not None:
                    samples.append(lookup[tet[a]] + t * (lookup[tet[b]] - lookup[tet[a]]))
        if len(vertices) < 3:
            continue
        vertices = np.array(vertices)
        center = vertices.mean(0)
        order = np.argsort(np.arctan2(vertices[:, 1] - center[1], vertices[:, 0] - center[0]))
        polygons.append(vertices[order])
        if lookup is not None:
            values.append(np.array(samples)[order])
    return polygons, values


def axes_style(ax, title):
    ax.set_title(title, loc='left', fontsize=12, pad=14)
    ax.set(xlim=(-.025, .725), ylim=(-.13, .76), xlabel='Z (µm)', ylabel='Height −X (µm)')
    ax.set_aspect('equal')
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(labelsize=9)


def section(ax, p, rs, mesh=False, y=.04):
    for rid in SOLIDS:
        r = rs[rid]
        polygons, _ = cut(p, r, y=y)
        ax.add_collection(PolyCollection(polygons, facecolors=COLORS[r['material']],
            edgecolors='#3a5868' if mesh else 'none', linewidths=.24 if mesh else 0, antialiaseds=mesh))


def save(fig, name):
    fig.savefig(OUT / f'{name}.svg', bbox_inches='tight', facecolor='white')
    fig.savefig(OUT / f'{name}.png', dpi=155, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def surface(conn):
    faces = np.concatenate([conn[:, inds] for inds in ([0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3])])
    _, index, count = np.unique(np.sort(faces, axis=1), axis=0, return_index=True, return_counts=True)
    return faces[index[count == 1]]


def geometry(p, rs):
    fig = plt.figure(figsize=(13.4, 7.2))
    ax = fig.add_subplot(121, projection='3d')
    copper = rs[6]
    faces = surface(copper['conn'])
    q = p[faces]
    q = np.stack([q[:, :, 2], q[:, :, 1], -q[:, :, 0]], axis=2)
    ax.add_collection3d(Poly3DCollection(q, facecolors=COLORS['Copper'], edgecolors='#955620', linewidths=.12))
    ax.set(xlim=(0, .7), ylim=(-.1, .05), zlim=(-.1, .7), xlabel='Z (µm)', ylabel='Y (µm)', zlabel='−X (µm)')
    ax.set_box_aspect((.7, .15, .8))
    ax.set_yticks([-.1, 0, .05])
    ax.tick_params(axis='y', labelsize=8)
    ax.view_init(20, -56)
    ax.set_title('Copper path | dielectrics and substrate hidden', fontsize=11, pad=20)
    ax = fig.add_subplot(122)
    section(ax, p, rs)
    axes_style(ax, 'Material section | Y = 0.04 µm')
    for text, xy, loc in [('M1', (.12, .2), (.12, .22)), ('Via', (.35, .4), (.46, .4)), ('M2', (.53, .55), (.55, .55))]:
        ax.annotate(text, xy=xy, xytext=loc, fontsize=10,
            arrowprops=dict(arrowstyle='-', color='#344e60'), color='#173e51')
    ax.axhline(0, color='#57738a', lw=.7)
    ax.text(.02, -.065, 'Silicon_1', fontsize=9, color='#254b61')
    fig.legend(handles=[Patch(color=c, label=m) for m, c in COLORS.items()], loc='lower center', ncol=4, frameon=False)
    fig.suptitle('Dual damascene | actual final geometry', x=.05, ha='left', fontsize=17, fontweight='bold')
    fig.text(.055, .07, 'Solid stack: 0.80 × 0.15 × 0.70 µm (X × Y × Z). Geometry shown without displacement.', color='#526b7c', fontsize=10)
    fig.subplots_adjust(top=.84, bottom=.17, wspace=.24)
    save(fig, 'geometry')


def mesh(p, rs):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 7))
    for ax in axes:
        section(ax, p, rs, mesh=True)
        axes_style(ax, 'Full section | Y = 0.04 µm')
    axes[0].add_patch(Rectangle((.275, .275), .15, .225, fill=False, ec='#c14a3a', lw=1.5))
    axes[1].set(xlim=(.275, .425), ylim=(.275, .5))
    axes[1].set_title('Via / liner detail | same physical coordinates', loc='left', fontsize=11)
    fig.suptitle('Tetrahedral mesh | section edges from the volume cells', x=.06, ha='left', fontsize=17, fontweight='bold')
    fig.text(.06, .04, 'Solid mesh: 17,887 tetrahedra / 3,729 unique vertices. Including ambient Gas: 19,434 tetrahedra / 4,064 vertices.', fontsize=10, color='#526b7c')
    fig.subplots_adjust(top=.85, bottom=.17, wspace=.32)
    save(fig, 'mesh')


def boundaries(p, rs):
    fig, (ax, side) = plt.subplots(1, 2, figsize=(13.8, 7.5), gridspec_kw={'width_ratios': [1.5, 1]})
    section(ax, p, rs)
    axes_style(ax, 'Electrical / thermal boundaries | Y = 0.04 µm')
    configs = [(16, 'E1 upper\nV = 0.1 V', '#a95122', (.79, .58)),
               (17, 'E2 lower\nV = 0 V', '#22678f', (-.25, .2)),
               (18, 'T1 tm0\nT = 100 °C', '#bb403b', (.78, -.015)),
               (19, 'T2 tm1\nT = 25 °C', '#2768aa', (.27, .83))]
    for rid, label, color, loc in configs:
        c = rs[rid]['conn']
        q = p[np.unique(c)]
        if rid in (16, 17):
            x = q[:, 2].mean()
            lo, hi = -q[:, 0].max(), -q[:, 0].min()
            ax.plot([x, x], [lo, hi], color=color, lw=5, solid_capstyle='butt')
            target = (x, (lo + hi) / 2)
        else:
            h = -q[:, 0].mean()
            ax.plot([q[:, 2].min(), q[:, 2].max()], [h, h], color=color, lw=4)
            target = (.35, h)
        ax.annotate(label, xy=target, xytext=loc, fontsize=10, color=color, ha='center',
                    arrowprops=dict(arrowstyle='-', color=color, lw=1.3))
    ax.annotate('Conventional current direction', xy=(.35, .3), xytext=(.35, .52), fontsize=8, ha='center',
        arrowprops=dict(arrowstyle='->', color='#784720', lw=1.5), color='#784720')
    ax.set(xlim=(-.31, 1.0), ylim=(-.16, .93))
    side.add_patch(Rectangle((-.1, 0), .15, .7, fc='#e8f1f3', ec='#466779', lw=1.2))
    for y, label, color in [(-.1, 'M2 Left\nY = −0.10\nvy = 0', '#286d80'), (.05, 'M3 Right\nY = +0.05\nvy = 0', '#286d80')]:
        side.plot([y, y], [0, .7], color=color, lw=3)
        side.annotate(label, xy=(y, .35), xytext=(y + (-.12 if y < 0 else .12), .35),
            fontsize=9, ha='center', va='center', color=color, arrowprops=dict(arrowstyle='-', color=color))
    for z, text, loc in [(0, 'M4 Back | Z = 0 | vz = 0', -.08), (.7, 'M5 Front | Z = 0.70 | vz = 0', .78)]:
        side.plot([-.1, .05], [z, z], color='#5a6fa5', lw=3)
        side.text(-.025, loc, text, ha='center', fontsize=9, color='#435a8c')
    side.text(-.025, .99, 'M1 Bottom | X = +0.10 µm\nvx = 0; tangential motion free', ha='center', fontsize=9, color='#286d80')
    side.text(-.025, -.23, 'M6 Upper solid / Gas: traction-free\nv denotes displacement rate', ha='center', fontsize=9, color='#38586b')
    side.set(xlim=(-.43, .38), ylim=(-.3, 1.13), xlabel='Y (µm)', ylabel='Z (µm)')
    side.set_aspect('equal'); side.spines[['right', 'top']].set_visible(False)
    side.set_title('Mechanics boundary map | X-normal view', loc='left', fontsize=11, pad=16)
    fig.suptitle('Boundary conditions | final 1 s calculation', x=.06, ha='left', fontsize=17, fontweight='bold')
    fig.text(.06, .04, 'E/T: actual contacts. Mechanics: schematic of normal constraints; tangential components free. Current arrow is qualitative.', fontsize=9, color='#526b7c')
    fig.subplots_adjust(top=.83, bottom=.16, left=.06, right=.95, wspace=.27)
    save(fig, 'boundary-conditions')


def field_plot(stages, field, filename, label, unit, limits, copper_only=False, scale=1, offset=0):
    fig, axes = plt.subplots(1, len(stages), figsize=(6.8 * len(stages), 7.0), squeeze=False)
    for ax, (stage, p, rs, _) in zip(axes[0], stages):
        triangles, values = [], []
        for rid in ([6] if copper_only else SOLIDS):
            r = rs[rid]
            data = r['fields'][field][:, 0] * scale + offset
            polygons, samples = cut(p, r, field=data)
            for poly, vals in zip(polygons, samples):
                for k in range(1, len(poly) - 1):
                    triangles.append(poly[[0, k, k + 1]])
                    values.append(vals[[0, k, k + 1]])
        vertices = np.concatenate(triangles)
        indices = np.arange(len(vertices)).reshape(-1, 3)
        c = ax.tripcolor(vertices[:, 0], vertices[:, 1], indices, np.concatenate(values),
            shading='gouraud', cmap='viridis' if field == 'Potential' else 'turbo', vmin=limits[0], vmax=limits[1], rasterized=True)
        axes_style(ax, f'{label} | {"25 °C residual state" if stage == 2 else "t = 1 s"}')
        fig.colorbar(c, ax=ax, fraction=.046, pad=.04, label=unit)
    fig.suptitle(f'{label} | Y = 0.04 µm', x=.06, ha='left', fontsize=16, fontweight='bold')
    fig.text(.06, .035, 'Unscaled geometry. Piecewise-linear interpolation of saved region-local nodal fields; no extra spatial smoothing.', fontsize=9, color='#526b7c')
    fig.subplots_adjust(top=.84, bottom=.17, wspace=.35)
    save(fig, filename)


def profile_plot():
    blocks = {}
    key = None
    for line in (OUT / 'source/n2_via.plx').read_text().splitlines():
        if line.startswith('"'):
            key = line.strip('"'); blocks[key] = []
        elif line.strip():
            blocks[key].append([float(v) for v in line.split()])
    fig, ax = plt.subplots(figsize=(11.5, 4.5))
    for key, data in blocks.items():
        a = np.array(data)
        ax.plot(a[:, 0], a[:, 1] * 1e-7, lw=2, label=key.replace('StressEL_', 'σ'))
    for lo, hi in [(-.45, -.3)]:
        ax.axvspan(lo, hi, color='#e8d2b4', alpha=.45, label='Via elevation (nominal)')
    ax.set(xlabel='X (µm; negative points above the wafer)', ylabel='Normal stress (MPa)',
           title='Copper line / via profile | Y = 0.04 µm, Z = 0.35 µm | 25 °C')
    ax.spines[['right', 'top']].set_visible(False); ax.grid(alpha=.18); ax.legend(ncol=4, frameon=False, fontsize=9)
    fig.tight_layout()
    save(fig, 'via-stress-profile')
    return {k: dict(samples=len(v), min_MPa=float(np.min(v, axis=0)[1] * 1e-7),
        max_MPa=float(np.max(v, axis=0)[1] * 1e-7)) for k, v in blocks.items()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for record in (OUT / 'source').glob('*.inputs.json'):
        for path, expected in json.loads(record.read_text()).items():
            local = OUT / 'source' / path.rsplit('/', 1)[-1]
            assert hashlib.sha256(local.read_bytes()).hexdigest() == expected
    manifest = json.loads((ROOT / 'assets/svisual/tdr-manifest.json').read_text())
    final = next(record for record in manifest if record['alias'] == 'Damascene')
    assert hashlib.sha256((OUT / 'source/n3_sis.tdr').read_bytes()).hexdigest() == final['sha256']
    data = {n: read_stage(n) for n in (1, 2, 3)}
    p, rs, _ = data[3]
    # The saved slice contains no coplanar vertices; strict edge cuts are complete.
    assert not np.any(np.isclose(p[:, 1], .04, atol=1e-10, rtol=0))
    for n in [1, 2]:
        assert np.array_equal(p, data[n][0])
        for rid in SOLIDS + [3]:
            assert np.array_equal(rs[rid]['conn'], data[n][1][rid]['conn'])
    # Validate region-local sorted vertex mapping using all electrical contacts.
    cids = rs[6]['ids']; potential = rs[6]['fields']['Potential'][:, 0]
    for rid, expected in [(16, .1), (17, 0)]:
        ids = rs[rid]['ids']
        assert np.all(cids[np.searchsorted(cids, ids)] == ids)
        assert np.allclose(potential[np.searchsorted(cids, ids)], expected, atol=1e-13)
    for contact, material_region, expected_C in [(18, 0, 100.), (19, 5, 25.)]:
        bulk = rs[material_region]
        indices = np.searchsorted(bulk['ids'], rs[contact]['ids'])
        assert np.array_equal(bulk['ids'][indices], rs[contact]['ids'])
        assert np.allclose(bulk['fields']['Temperature'][indices, 0] - 273.156, expected_C, atol=1e-9)
    for rid in SOLIDS:
        for name in ('JouleHeat', 'TotalHeat', 'PowerDensity'):
            assert np.all(rs[rid]['fields'][name] == 0)
    tags = json.loads((OUT / 'retained-tags.json').read_text())
    for material in ('Silicon', 'Nitride', 'Oxide', 'Copper'):
        assert tags[f'Params&{material}&Temperature&Equation'] == 'String {0 + 0.0 + (kappa)*grad(Temperature) + 0.0 + RegionalPowerDensity + 0.0}'
    log = (OUT / 'source/n3.stdout').read_text()
    step_count = len(re.findall(r'Solve:\s+[\d.e+-]+s\s+to', log))
    assert step_count == 14
    geometry(p, rs); mesh(p, rs); boundaries(p, rs)
    selected = [(n, *data[n]) for n in [2, 3]]
    field_plot(selected, 'MisesStress', 'copper-mises', 'Copper von Mises stress', 'MPa', (0, 750), copper_only=True, scale=1e-7)
    field_plot([selected[1]], 'Temperature', 'temperature', 'Temperature', '°C', (25, 100), offset=-273.156)
    field_plot([selected[1]], 'Potential', 'potential', 'Copper potential', 'V', (0, .1), copper_only=True)
    profiles = profile_plot()
    results = {}
    for n in [1, 2, 3]:
        _, r, fields = data[n]; cu = r[6]
        s = cu['fields']['MisesStress'][:, 0] * 1e-7
        t = cu['fields']['Temperature'][:, 0] - 273.156
        peak = int(s.argmax())
        results[str(n)] = dict(copper_mises_min_MPa=float(s.min()), copper_mises_max_MPa=float(s.max()),
            copper_mises_peak_xyz_um=p[cu['ids'][peak]].tolist(), copper_temperature_C=[float(t.min()), float(t.max())],
            datasets=fields)
    evidence = dict(mesh=dict(vertices=len(p), bulk_region_local_vertices=sum(len(rs[i]['ids']) for i in range(7)),
        bulk_and_interface_region_local_vertices=sum(len(r['ids']) for r in rs.values() if r['type'] in (0,1)),
        solid_vertices=len(np.unique(np.concatenate([rs[i]['ids'] for i in SOLIDS]))),
        total_tetrahedra=sum(len(rs[i]['conn']) for i in range(7)), solid_tetrahedra=sum(len(rs[i]['conn']) for i in SOLIDS),
        bounds_solid_um=[p[np.unique(np.concatenate([rs[i]['ids'] for i in SOLIDS]))].min(0).tolist(),
                         p[np.unique(np.concatenate([rs[i]['ids'] for i in SOLIDS]))].max(0).tolist()],
        regions=[dict(name=rs[i]['name'], material=rs[i]['material'], tetrahedra=len(rs[i]['conn']), region_nodes=len(rs[i]['ids'])) for i in range(7)]),
        results=results, profiles=profiles, contacts=[dict(name=rs[i]['name'], triangles=len(rs[i]['conn']), vertices=len(rs[i]['ids']),
            bounds_um=[p[rs[i]['ids']].min(0).tolist(), p[rs[i]['ids']].max(0).tolist()]) for i in range(16,20)],
        geometry_and_mesh_unchanged_between_saved_stages=True,
        physical_checks=dict(zero_joule_heat_and_power_density=True, thermal_storage_term=False,
            electrical_contact_values_verified=True, thermal_contact_values_verified=True,
            mechanics_default_boundary_reference='Sentaurus Interconnect User Guide W-2024.09 pp.109-111; local si_ug/boundary_condition*.png',
            final_time_s=1., accepted_steps=step_count, initial_step_s=.0001),
        plot_settings=dict(section_y_um=.04, coordinate_transform='horizontal Z; vertical -X', deformation_scale=0,
            stress='saved MisesStress; region-local nodal; dyn/cm2 to MPa factor 1e-7',
            temperature='saved K minus source Celsius offset 273.156', stress_range_MPa=[0,750]),
        sources=[dict(path=str(q.relative_to(ROOT)), sha256=hashlib.sha256(q.read_bytes()).hexdigest()) for q in sorted((OUT/'source').iterdir())],
        static_converter_review=dict(root='D:/my_repos/si_to_ans_converter',
            files=['converter_core/cmd_reader/cmd_reader.py:590-594','converter_core/cmd_reader/execution_controls.py:41-43',
                   'converter_core/cmd_reader/thermal_semantics.py:66-88','converter_core/tdr_reader.py:20-25'],
            conclusion='Combined mechanics/current/thermal mode and active StressHistory/EtchDepoRelax rejected; steady constant-property thermal subset exists; no case conversion executed'),
        gt_a='No matching target solve or numerical benchmark found',
        solver_identity='Retained integrated sinterconnect_run commands; native reference comparisons in assets/svisual/validation-results.json')
    (OUT / 'evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps(dict(mesh=evidence['mesh'], results={k:{a:b for a,b in v.items() if a!='datasets'} for k,v in results.items()},profiles=profiles), indent=2))


if __name__ == '__main__':
    main()
