from pathlib import Path

root = Path('/home/mozztcad/geo3d')
sprocess = root / 'cmake/sprocess.cmake'
text = sprocess.read_text()
marker = 'target_link_libraries(geo_core PUBLIC SProcess::FortranRuntime)\n'
include = marker + 'include(cmake/arpack.cmake)\n'
if 'include(cmake/arpack.cmake)' not in text:
    if marker not in text:
        raise SystemExit('sprocess marker not found')
    text = text.replace(marker, include, 1)
    sprocess.write_text(text)

common = root / 'cmake/toolchain_gcc12_common.cmake'
text = common.read_text()
marker = 'set(GEO3D_METIS_ROOT "${GEO3D_SOURCE_THIRD_PARTY_ROOT}/metis-4.0.3")\n'
line = marker + 'set(GEO3D_ARPACK_ROOT "${GEO3D_SOURCE_THIRD_PARTY_ROOT}/arpack-ng-3.8.0")\n'
if 'set(GEO3D_ARPACK_ROOT' not in text:
    if marker not in text:
        raise SystemExit('toolchain marker not found')
    common.write_text(text.replace(marker, line, 1))

arpack = root / 'cmake/arpack.cmake'
if not arpack.exists():
    raise SystemExit('arpack.cmake was not installed')

