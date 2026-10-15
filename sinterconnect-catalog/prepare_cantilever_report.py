"""Rebuild figures and measured evidence for the retained Cantilever baseline.

Reads existing artifacts only; never runs a converter or a solver.
Requires numpy, h5py and matplotlib in the selected Python environment.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import shutil
import zipfile

import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle, Polygon
import numpy as np

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'assets/case-reports/cantilever'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_mesh(path):
    with h5py.File(path, 'r') as source:
        collection = source['collection']
        assert int(collection.attrs['TDR HDF5 version']) == 16
        geometry = collection['geometry_0']
        assert geometry.attrs['unit:name'] == b'cm'
        assert float(geometry.attrs['unit:significand']) == 1.0
        assert np.all(geometry['offset'][:] == 0)
        assert np.array_equal(geometry['transformation/A'][:].reshape(3, 3), np.eye(3))
        assert np.all(geometry['transformation/b'][:] == 0)
        raw = geometry['vertex'][:]
        points = np.column_stack([raw[key] for key in ('x', 'y', 'z')]) * 1e4
        region = geometry['region_0']
        records = region['elements_0'][:].reshape(-1, 5)
        assert np.all(records[:, 0] == 5)
        assert len(records) == int(region['elements_0'].attrs['number of elements'])
        assert len(points) == int(geometry.attrs['number of vertices'])
        assert np.allclose(points.min(0), [0, -2, -2])
        assert np.allclose(points.max(0), [50, 2, 2])
        tags = {}
        for tag in geometry['tag_group_0/tag_group_0'].values():
            if 'value' in tag.attrs:
                tags[tag.attrs['key'].decode()] = tag.attrs['value'].decode()
        metadata = dict(region=region.attrs['name'].decode(), material=region.attrs['material'].decode(),
                        coordinate_unit='cm', display_unit='um', vertices=len(points),
                        tetrahedra=len(records), connectivity='TDR record type 5, four vertices',
                        bounds_um=[points.min(0).tolist(), points.max(0).tolist()],
                        x_planes=len(np.unique(points[:, 0])), y_planes=len(np.unique(points[:, 1])),
                        z_planes=len(np.unique(points[:, 2])),
                        bottom_node_count=int(np.isclose(points[:, 0], 50, rtol=0, atol=1e-10).sum()),
                        point_load_nodes=(np.flatnonzero(np.all(np.isclose(points, [0, 0, 0], rtol=0, atol=1e-10), axis=1)) + 1).tolist(),
                        retained_pdb_tags=tags)
        metadata['spacing_um'] = {}
        for index, axis in enumerate('xyz'):
            spacing = np.diff(np.unique(points[:, index]))
            metadata['spacing_um'][axis] = [float(spacing.min()), float(spacing.max())]
        return points, records[:, 1:].astype(np.int64), metadata


def check_cdb(path, points, tetrahedra):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    begin = next(index for index, line in enumerate(lines) if line.startswith('NBLOCK,'))
    nodes = []
    ids = []
    assert lines[begin + 1] == '(3i9,6e21.13e3)'
    node_count = int(lines[begin].split(',')[-1])
    for line in lines[begin + 2:begin + 2 + node_count]:
        ids.append(int(line[:9]))
        nodes.append([float(line[27 + index * 21:48 + index * 21]) for index in range(3)])
    assert ids == list(range(1, len(points) + 1))
    delta = float(np.max(np.abs(np.array(nodes) - points * .001)))
    assert delta < 1e-14, delta  # Serialization precision, not a solver acceptance criterion.
    element_header = next(line for line in lines if line.startswith('EBLOCK,'))
    assert int(element_header.split(',')[-1]) == len(tetrahedra)
    assert lines[begin + 2 + node_count].startswith('N,UNBL,LOC,')
    # The declared blocked record for each retained 4-node solid fits one line.
    element_begin = lines.index(element_header)
    width = int(re.fullmatch(r'\(19i(\d+)\)', lines[element_begin + 1]).group(1))
    cdb_elements = []
    for line in lines[element_begin + 2:]:
        if line.strip() == '-1':
            break
        fields = [int(line[index:index + width]) for index in range(0, len(line), width) if line[index:index + width].strip()]
        assert fields[8] == 4 and len(fields) == 15, fields[:11]
        cdb_elements.append(fields[11:15])
    assert np.array_equal(np.array(cdb_elements), tetrahedra + 1)
    constraints = re.findall(r'^D,\s*(\d+),\s*(U[XYZ])\s*,\s*([^,]+)', text, re.M)
    expected_ids = set((np.flatnonzero(np.isclose(points[:, 0], 50, rtol=0, atol=1e-10)) + 1).tolist())
    assert len(constraints) == len(expected_ids) * 3
    assert {(int(node), axis) for node, axis, value in constraints} == {(node, axis) for node in expected_ids for axis in ('UX', 'UY', 'UZ')}
    assert all(float(value) == 0 for _, _, value in constraints)
    forces = re.findall(r'^F,\s*(\d+),\s*(F[XYZ])\s*,\s*([^,]+)', text, re.M)
    assert len(forces) == 1 and int(forces[0][0]) == 113 and forces[0][1] == 'FZ'
    assert float(forces[0][2]) == -3e-7
    assert 'MPDATA,UNBL,1,EX,1,1,1000' in text
    assert 'MPDATA,UNBL,1,PRXY,1,1,0.2' in text
    return dict(nodes=len(nodes), tetrahedra=len(cdb_elements), connectivity_equal=True,
                max_coordinate_serialization_difference_mm=delta,
                zero_displacement_records=len(constraints), constrained_nodes=len(expected_ids),
                point_force=dict(node=113, component='FZ', value_N=-3e-7),
                E_MPa=1000, poisson_ratio=.2,
                solver_procedure_present=bool(re.search(r'^\s*(SOLVE|ANTYPE)\b', text, re.M)),
                solver_validation='not run; retained conversion log')


def save_figure(fig, name):
    fig.savefig(OUTPUT / (name + '.svg'), bbox_inches='tight', facecolor='white')
    plt.close(fig)


def geometry_figure(points):
    fig, ax = plt.subplots(figsize=(14, 4.5))
    low, high = points.min(0), points.max(0)
    corners = np.array([[x, y, z] for x in (low[0], high[0]) for y in (low[1], high[1]) for z in (low[2], high[2])])
    azimuth, elevation = np.deg2rad(20), np.deg2rad(20)
    projection = np.array([[np.cos(azimuth), np.sin(azimuth), 0],
                           [-np.sin(azimuth)*np.sin(elevation), np.cos(azimuth)*np.sin(elevation), np.cos(elevation)]])
    projected = corners @ projection.T
    for face, color in [([0, 1, 5, 4], '#d1e8e9'), ([1, 3, 7, 5], '#e4f1f2'), ([4, 5, 7, 6], '#16818b')]:
        ax.add_patch(Polygon(projected[face], facecolor=color, edgecolor='#24495b', linewidth=1.3))
    dimension_start = projected[0] + [0, -4]
    dimension_end = projected[4] + [0, -4]
    ax.annotate('', xy=dimension_end, xytext=dimension_start, arrowprops=dict(arrowstyle='<->', color='#536678'))
    middle = (dimension_start + dimension_end)/2
    ax.text(*middle, 'L = 50 um', ha='center', va='top', rotation=-7, fontsize=11, color='#315c70')
    ax.text(17, 3.2, 'Silicon_1 | uniform rectangular beam', color='#315c70', fontsize=12)
    ax.text(0, 3, 'Free end\nX = 0 um', ha='center', fontsize=10)
    ax.annotate('4 x 4 um section\nFixed end: X = 50 um', xy=projected[[4,5,6,7]].mean(0), xytext=(48, 2),
                fontsize=10, arrowprops=dict(arrowstyle='-', color='#536678'), color='#315c70')
    origin=np.array([0.,-12.])
    for index, label in enumerate('XYZ'):
        tip=origin+projection[:,index]*3.4
        ax.annotate('',xy=tip,xytext=origin,arrowprops=dict(arrowstyle='->',color='#536678',lw=1.2))
        ax.text(*(tip+projection[:,index]*.8),label,ha='center',va='center',fontsize=10,color='#536678')
    ax.set(xlim=(-4, 59), ylim=(-14, 7)); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Cantilever geometry | 50 x 4 x 4 um', loc='left', pad=16)
    fig.subplots_adjust(left=.04,right=.98,top=.83,bottom=.14)
    fig.text(.07, .04, 'Three-dimensional rectangular beam; the physical aspect ratio is preserved. Dimensions are in micrometers.', fontsize=10, color='#536678')
    save_figure(fig, 'geometry')


def mesh_figure(points, tetrahedra):
    fig, axes = plt.subplots(2, 1, figsize=(14, 6.4), gridspec_kw={'height_ratios': [1, 1.4]})
    # An edge is on the exterior Y=-2 face only when both vertices lie on it.
    edges = np.concatenate([tetrahedra[:, [i, j]] for i, j in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))])
    mask = np.all(np.isclose(points[edges, 1], -2, rtol=0, atol=1e-10), axis=1)
    edges = np.unique(np.sort(edges[mask], axis=1), axis=0)
    segments = points[edges][:, :, [0, 2]]
    for ax, limits in zip(axes, [(0, 50), (46, 50)]):
        visible = (segments[:, :, 0].max(1) >= limits[0]) & (segments[:, :, 0].min(1) <= limits[1])
        ax.add_collection(LineCollection(segments[visible], colors='#27606c', linewidths=.35))
        ax.set_aspect('equal'); ax.set_ylabel('Z (um)'); ax.set_xlabel('X (um)')
        ax.set_ylim(-2.15, 2.15); ax.spines[['top', 'right']].set_visible(False)
    axes[0].set_xlim(0, 50); axes[0].set_title('Surface mesh at Y = -2 um | full beam', loc='left')
    axes[1].set_xlim(46, 50); axes[1].set_title('Fixed-end detail | X = 46 to 50 um', loc='left')
    fig.suptitle('37,800 vertices / 196,392 four-vertex tetrahedra', x=.08, ha='left', fontweight='bold')
    fig.tight_layout(rect=[0, .06, 1, .94])
    fig.text(.08, .02, 'Surface view and fixed-end detail of the three-dimensional volume mesh.', fontsize=10, color='#536678')
    save_figure(fig, 'mesh')


def boundary_figure():
    fig, (ax, end) = plt.subplots(1, 2, figsize=(14, 5.8), gridspec_kw={'width_ratios': [3.2, 1]})
    ax.add_patch(Rectangle((0, -2), 50, 4, facecolor='#e8f3f4', edgecolor='#315c70', linewidth=1.5))
    ax.add_patch(Rectangle((50, -3), 1.5, 6, facecolor='#d5dfe5', edgecolor='#526a78', hatch='////'))
    ax.plot([50, 50], [-2, 2], color='#087e8a', linewidth=5)
    ax.annotate('', xy=(0, -6.2), xytext=(0, 0), arrowprops=dict(arrowstyle='-|>', color='#c55b33', lw=3))
    ax.scatter([0], [0], color='#c55b33', s=30, zorder=4)
    ax.text(2, -6.2, 'BC02  pointend\nFz = -0.03 dyn = -0.3 uN\n(0, 0, 0) um', fontsize=11, color='#a84625', va='top')
    ax.text(47, 4.5, 'BC01  Bottom\nX = 50 um\nux = uy = uz = 0', fontsize=11, color='#08747f', ha='right')
    ax.annotate('', xy=(0, 4), xytext=(50, 4), arrowprops=dict(arrowstyle='<->', color='#536678'))
    ax.text(25, 4.5, 'L = 50 um', ha='center')
    ax.text(12, .1, 'Silicon_1 | 4 x 4 um square cross-section', color='#315c70', fontsize=10)
    ax.set_xlim(-3, 56); ax.set_ylim(-11, 10)
    ax.set_xlabel('X (um): free end -> fixed end'); ax.set_ylabel('Z (um)')
    ax.set_aspect('equal'); ax.set_title('X-Z view: actual baseline locations and load direction', loc='left', fontsize=11)
    ax.spines[['top', 'right']].set_visible(False)
    end.add_patch(Rectangle((-2, -2), 4, 4, facecolor='#e8f3f4', edgecolor='#315c70', linewidth=1.5))
    end.scatter([0], [0], color='#c55b33', s=40)
    end.annotate('', xy=(0, -1.4), xytext=(0, 0), arrowprops=dict(arrowstyle='-|>', color='#c55b33', lw=2))
    end.text(0, 2.7, 'BC06 Front: Z = +2', ha='center', fontsize=9)
    end.text(0, -3.2, 'BC05 Back: Z = -2', ha='center', fontsize=9)
    end.text(-2.6, 0, 'BC03 Left / Y = -2', ha='center', va='center', rotation=90, fontsize=8)
    end.text(2.6, 0, 'BC04 Right / Y = +2', ha='center', va='center', rotation=90, fontsize=8)
    end.set_xlim(-3.5, 3.5); end.set_ylim(-3.8, 3.8); end.set_aspect('equal')
    end.set_xlabel('Y (um)'); end.set_ylabel('Z (um)')
    end.set_title('Free-end Y-Z view (X = 0)', fontsize=11, pad=34)
    end.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Boundary conditions | fixed support and transverse end load', x=.06, ha='left', fontweight='bold')
    fig.text(.06, .05, 'BC03-BC06: sx = sy = sz = 0 (zero surface traction, not displacement constraints). No mechanical contact pair.', fontsize=10)
    fig.text(.06, .01, 'The fixed end constrains all three translations. The arrow indicates force direction; its length is not to scale.', fontsize=9, color='#536678')
    fig.subplots_adjust(left=.06, right=.93, bottom=.22, top=.78, wspace=.65)
    save_figure(fig, 'boundary-conditions')


def prepare(mesh, reference_archive, unit_config):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    retained_mesh = OUTPUT / 'pre-solve.tdr'
    if mesh.resolve() != retained_mesh.resolve():
        shutil.copy2(mesh, retained_mesh)
    points, tetrahedra, metadata = read_mesh(retained_mesh)
    baseline = ROOT / 'assets/gt-a/Cantilever'
    registered = json.loads((ROOT / 'gt-a-cases.json').read_text(encoding='utf-8'))['Cantilever']
    assert digest(retained_mesh) == registered['mesh_sha256']
    # The narrative and BC diagram describe this exact retained source variant.
    # A changed input requires updating the interpretation rather than silently
    # reusing this case-specific description against a different simulation.
    if digest(baseline / 'input.cmd') != '42605847847281205df3696231dfdceed95bd0b11311a3d6c0033f1e77a56fd1':
        raise ValueError('Retained input identity changed; review the report interpretation before rebuilding.')
    retained_units = OUTPUT / 'unit-system.json'
    if unit_config.resolve() != retained_units.resolve():
        shutil.copy2(unit_config, retained_units)
    units = json.loads(retained_units.read_text(encoding='utf-8'))
    assert units['defaults']['pressure'] == 'dyn/cm2'
    assert units['units']['pressure']['dyn/cm2']['factor'] == .1
    static_check = check_cdb(baseline / 'Cantilever.cdb', points, tetrahedra)
    with zipfile.ZipFile(reference_archive) as archive:
        reference_name = next(name for name in archive.namelist() if name.endswith('/vendor-reference-cantilever.cmd'))
        reference_bytes = archive.read(reference_name)
    (OUTPUT / 'archived-reference.cmd').write_bytes(reference_bytes)
    reference = reference_bytes.decode('utf-8-sig').splitlines()
    current = (baseline / 'input.cmd').read_text(encoding='utf-8-sig').splitlines()
    (OUTPUT / 'reference-to-input.diff.txt').write_text('\n'.join(difflib.unified_diff(reference, current, fromfile='archived-reference.cmd', tofile='converter-input.cmd')) + '\n', encoding='utf-8')
    replay = next(item for item in json.loads((ROOT / 'assets/svisual/validation-results.json').read_text()) if item['case'] == '3D_Cantilever')
    output_manifest = next(item for item in json.loads((ROOT / 'assets/svisual/tdr-manifest.json').read_text()) if item['alias'] == 'Cantilever')
    sources = []
    for path in [retained_mesh, retained_units, OUTPUT / 'archived-reference.cmd', baseline / 'input.cmd', baseline / 'Cantilever.cdb', baseline / 'Cantilever.apdl', baseline / 'conversion.log', baseline / 'ansys-run.out', ROOT / 'assets/svisual/Cantilever-1.png', ROOT / 'assets/svisual/Cantilever-2.png']:
        sources.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path), bytes=path.stat().st_size))
    evidence = dict(updated='2026-10-15', scope='Retained converter baseline plus separately identified historical SVisual results; no new simulation or numerical GT-A benchmark.',
                    mesh_source=registered['mesh_source'], mesh_retained_path=retained_mesh.relative_to(ROOT).as_posix(),
                    reference_archive='../Resources/case-archive/' + reference_archive.name,
                    reference_archive_sha256=digest(reference_archive), reference_entry=reference_name,
                    mesh=metadata, cdb_static_check=static_check, historical_replay=replay, displayed_result=output_manifest,
                    displayed_legend_readings=dict(method='Approximate transcription of retained SVisual color bars; not a fresh field reduction.',
                                                  MisesStress_Pa=[815.2, 1.405e6], displacement_magnitude_um=[0, .577]),
                    analytical_estimate=dict(assumption='Euler-Bernoulli slender, isotropic, linear elastic beam; nominal bending only.',
                                             E_Pa=1e9, poisson_ratio=.2, force_N=3e-7, length_m=50e-6,
                                             square_side_m=4e-6, second_moment_m4=(4e-6)**4/12,
                                             tip_displacement_um=3e-7*(50e-6)**3/(3*1e9*((4e-6)**4/12))*1e6,
                                             nominal_root_bending_stress_MPa=3e-7*50e-6*2e-6/((4e-6)**4/12)/1e6),
                    files=sources)
    (OUTPUT / 'evidence.json').write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    geometry_figure(points)
    mesh_figure(points, tetrahedra)
    boundary_figure()
    print(json.dumps(dict(mesh=metadata['vertices'], tetrahedra=metadata['tetrahedra'], cdb=static_check, output=str(OUTPUT)), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh', type=Path, default=OUTPUT / 'pre-solve.tdr')
    parser.add_argument('--reference-archive', type=Path, default=ROOT.parent / 'Resources/case-archive/03_Quasistatic_equilibrium.zip')
    parser.add_argument('--unit-config', type=Path, default=OUTPUT / 'unit-system.json')
    args = parser.parse_args()
    prepare(args.mesh, args.reference_archive, args.unit_config)
