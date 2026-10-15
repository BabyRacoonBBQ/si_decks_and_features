# Case handoff to thermomechanical chat

Recommended ownership: thermomechanical chat owns remaining implementation, builds, final validation and submission. This chat has not committed or pushed.

## Historically verified package cases
Evidence: C:/Users/Yuanyuan/Desktop/si/architecture-overview/StressThermal/performance-benchmark/product-gated-verification-summary.json
Detailed scope: thermomechanical-recovery-report.md in that directory.
Historical local binary SHA256: d223681b488443d6361471cd22a621f4be94827ee6d8798e665fa73c1e115ebc.
These results are not a certification of the current post-rebase working tree.

- Adapted Backend Package_ThermomechanicalReliability thermal stage.
- Local thermal output -> local mechanical continuation, plus same-input one-step mechanics.
- Four-step mechanics (4 x 0.25 s).
- Implicit starting temperature.
- Uniform 400 K target temperature.
- Catch parameter errors, then valid four-step solve.
The retained results report TDR byte equality excluding structurally identified HDF5 timestamps.

Error/entry checks: missing profile, conflicting t.final and t.final.profile, profile without time, six SetTemp argument cases, repeated SetTemp history and power-density conversion.
Missing-profile diagnostic equality normalizes PID; complete stdout/stderr and timers are not certified identical.

VM evidence root:
/home/mozztcad/tmp/package-benchmark-20261010/thermomechanical-recovery
Recipes: run-certified-e2e-v3.sh, run-certified-v3-profile-matrix.sh, run-profile-strain-v3.sh, run-settemp-unit-v3.sh.
The timestamp comparator requires inspecting/asserting its JSON result; exit status alone does not signal mismatch.

## Mechanics slide cases to retain in final validation
VM deck paths:
- /home/mozztcad/tmp/local-mechanics/quasistatic/case.cmd
- /home/mozztcad/tmp/local-mechanics/geometric-off/case.cmd
- /home/mozztcad/tmp/local-mechanics/geometric-on/case.cmd
- /home/mozztcad/tmp/local-mechanics/linear-buckling/case.cmd
- /home/mozztcad/tmp/local-mechanics/post-buckling-supercritical/case.cmd

Local runs/outputs exist. DO NOT classify all five as vendor-identical.
The retained linear-buckling compare-final.json explicitly reports nonidentical BucklingMode1/2/3 and small differences in some other fields, even though displacement and some element/Gauss fields are exact.
Observed eigenvalues: approximately 71.7609, 71.7609, 609.8.
No complete timestamp-only byte-equality proof for the other four mechanics cases was identified in this handoff audit.
GIF regeneration is not required by the user.

Mechanics evidence:
C:/Users/Yuanyuan/Desktop/si/architecture-overview/StressThermal/performance-benchmark/slide-evidence/mechanics-local/results-summary.json
C:/Users/Yuanyuan/Desktop/si/architecture-overview/StressThermal/performance-benchmark/slide-evidence/mechanics-local/linear-buckling/compare-final.json

## Current blockers
Read /home/mozztcad/geo3d/temp/submit-georun/COORDINATION.md.
Vendor siMechPDE::computeStress (0x126dc80) and computeStressD_slsVISC (0x1266610) have product-specific logic; base-only forwarders added by this chat were withdrawn.
Current source build and final unified verify_all gate are not certified passing. The earlier scan PASS was superseded by BLOCKED.
Preserve existing code, named stash, TDR evidence and backups. No requirement to regenerate GIFs.
