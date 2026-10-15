# Thermomechanical active goal

Updated from the user-designated CASE-HANDOFF-thermomechanical.md. The VM could not be reached during this update; the local archived copy was read. Reconcile it with the VM copy when connectivity returns.

## Objective

Own the remaining thermomechanical and submodeling honesty recovery, integration, builds, final validation, review and authorized submission to main. Resolve implementation defects using original-binary evidence. Do not claim completion from historical results or a narrower passing subset.

## Required scope

1. Integrate and validate the recovered submodeling chain: local global output, local displacement mapping and local stress solve. Preserve the original honesty checks and provenance requirements.
2. Retain the package thermomechanical cases: thermal stage; local thermal-to-mechanical continuation; same-input one-step mechanics; four 0.25 s steps; implicit starting temperature; uniform 400 K target; parameter error followed by a valid four-step solve.
3. Retain package entry/error checks: missing profile, conflicting t.final/t.final.profile, profile without time, six SetTemp argument cases, repeated SetTemp history and power-density conversion.
4. Include all five mechanics slide cases in final validation: quasistatic, geometric-off, geometric-on, linear-buckling and post-buckling-supercritical. Investigate the recorded BucklingMode1/2/3 differences; do not classify existing runs as vendor-identical without sufficient evidence.
5. Complete the native ARPACK recovery and review product-specific siMechPDE behavior. Base-only forwarding or an invented eigensolver cannot count as faithful recovery. Identify genuinely unexercised and unrecovered branches explicitly.
6. Produce a successful build matching the final source snapshot, a valid zero-exit scripts/verify_all.sh result, and a completed submit-georun code review before committing and pushing main.

## Acceptance evidence

- Record source and binary identities, commands, exit statuses, inputs, outputs, native comparisons and coverage limits.
- Inspect timestamp-comparator JSON assertions; its exit status alone does not prove equality.
- Distinguish raw byte equality, equality excluding identified HDF5 timestamps, semantic equality and numerical differences.
- The package's historical binary/results do not certify the current post-rebase source. Missing-profile diagnostic normalization covers PID only; complete stdout/stderr/timer parity is not established.
- Preserve existing code, named stash, TDR evidence and backups. Do not commit TDR files without the required explicit authorization.
- Do not restart live builds merely because polling times out. Avoid concurrent builds in the same output directory.
- GIF regeneration is not required.

## Current state at goal update

The existing system goal remains active and broadly covers this objective; its tool API permits status updates only, not editing the objective of an unfinished goal. This file records the user-requested scope refinement without falsely marking that goal complete.

Latest retained progress: missing stress-path integration edits and ARPACK parameter fixes exist; a fuller ARPACK candidate passed syntax checking and its open-source dependency built. Candidate integration, runtime comparisons and final submission gates remain incomplete. The most recent interface-test retry was interrupted; its outcome must be checked rather than assumed. VM access is currently timing out, so current remote build/source state remains unverified.
