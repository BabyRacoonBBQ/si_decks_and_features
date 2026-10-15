from pathlib import Path

root = Path('/home/mozztcad/geo3d')
candidate = root / 'temp/submit-georun/20261012-improvement/candidate/src/abi/floops/floops'
for name in ('arpack_gv.h', 'arpack_gv.cpp', 'VectorRef.h'):
    source = candidate / name
    if not source.exists():
        raise SystemExit(f'missing candidate file: {source}')
    (root / 'src/abi/floops/floops' / name).write_text(source.read_text())

tee_h = root / 'src/abi/floops/floops/Tee.h'
text = tee_h.read_text()
if 'namespace floops { class arpack_gv; }' not in text:
    text = text.replace('class Tee;\n', 'class Tee;\nnamespace floops { class arpack_gv; }\n', 1)
if 'Tee& esepl(Tee& tee);' not in text:
    text = text.replace('Tee& tflush(Tee& tee);\n', 'Tee& tflush(Tee& tee);\nTee& esepl(Tee& tee);\n', 1)
if 'friend class floops::arpack_gv;' not in text:
    text = text.replace('private:\n    friend void FLPS_warning', 'private:\n    friend class floops::arpack_gv;\n    friend void FLPS_warning', 1)
tee_h.write_text(text)

tee_cpp = root / 'src/abi/floops/floops/Tee.cpp'
text = tee_cpp.read_text()
if 'Tee& esepl(Tee& tee)' not in text:
    marker = 'Tee& ssepl(Tee& tee)\n'
    if marker not in text:
        raise SystemExit('Tee separator marker not found')
    esepl = ('Tee& esepl(Tee& tee)\n'
             '{\n'
             '    tee << VOF_STR("==============================================================================");\n'
             '    return tee;\n'
             '}\n\n')
    text = text.replace(marker, esepl + marker, 1)
tee_cpp.write_text(text)

stubs = root / 'src/abi/floops/floops/AnnealChainProbeStubs.cpp'
text = stubs.read_text()
start = 'extern "C" void dsygv_(int*, char*, char*, int*, double*, int*, double*, int*, double*, double*, int*, int*);\n\n'
end = '// ── DataUtil ───────────────────────────────────────────────────────────────\n'
if start in text:
    if end not in text:
        raise SystemExit('ARPACK stub end marker not found')
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    text = before + end + after
elif 'arpack_gv::arpack_gv' in text:
    raise SystemExit('ARPACK stub block is present but marker changed')
stubs.write_text(text)

