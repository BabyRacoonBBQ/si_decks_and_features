# ARPACK-NG 3.8.0 integration payload

This directory contains the CMake wiring used to install ARPACK-NG 3.8.0 as
the source third-party dependency for the recovered `sinterconnect_run`
eigenvalue path. The files are copied to the remote Geo3D checkout during the
integration step; the source package itself is copied from the already audited
official archive in the remote recovery workspace.

The build compiles only the double-precision symmetric reverse-communication
closure used by `floops::arpack_gv` (`dsaupd_`/`dseupd_`) with the repository's
existing Intel classic `ifort` 2021.8.0 and links the existing oneAPI MKL and
Fortran runtime targets. The full vendored source package retains ARPACK-NG's
BSD license and upstream files for provenance.

