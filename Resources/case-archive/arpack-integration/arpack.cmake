# =============================================================================
# arpack.cmake - ARPACK-NG third-party source for sinterconnect_run
# =============================================================================
#
# The recovered sinterconnect eigenvalue path calls the native ARPACK reverse
# communication ABI (`dsaupd_`/`dseupd_`).  ARPACK-NG is vendored as source so
# the standalone product does not depend on a host distribution package or on
# a generated archive left in a build directory.  Compile the exact
# double-precision symmetric closure with the same classic ifort and Intel
# runtime already used for the recovered PARDISO sources.
#
# This file is included after `SPROCESS_IFORT_*`, `GEO3D_GCC_RUNTIME_DIR`, and
# `SProcess::FortranRuntime` have been configured by cmake/sprocess.cmake.
# =============================================================================

set(SPROCESS_ARPACK_ROOT
    "${GEO3D_SOURCE_THIRD_PARTY_ROOT}/arpack-ng-3.8.0")
if(NOT IS_DIRECTORY "${SPROCESS_ARPACK_ROOT}")
    message(FATAL_ERROR
        "ARPACK-NG 3.8.0 source package is missing: ${SPROCESS_ARPACK_ROOT}")
endif()

# ARPACK's dsaupd/dseupd generalized symmetric path and its transitive utility
# routines.  The remaining single/complex/nonsymmetric routines stay vendored
# for provenance but are not part of this native sinterconnect closure.
set(SPROCESS_ARPACK_FORTRAN_SOURCES
    "${SPROCESS_ARPACK_ROOT}/SRC/dgetv0.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsaitr.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsapps.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsaup2.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsaupd.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsconv.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dseigt.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsesrt.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dseupd.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsgets.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dsortr.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dstats.f"
    "${SPROCESS_ARPACK_ROOT}/SRC/dstqrb.f"
    "${SPROCESS_ARPACK_ROOT}/UTIL/dmout.f"
    "${SPROCESS_ARPACK_ROOT}/UTIL/dvout.f"
    "${SPROCESS_ARPACK_ROOT}/UTIL/ivout.f"
    "${SPROCESS_ARPACK_ROOT}/UTIL/second_NONE.f")

foreach(SPROCESS_ARPACK_SOURCE IN LISTS SPROCESS_ARPACK_FORTRAN_SOURCES)
    if(NOT EXISTS "${SPROCESS_ARPACK_SOURCE}")
        message(FATAL_ERROR "ARPACK source file is missing: ${SPROCESS_ARPACK_SOURCE}")
    endif()
endforeach()

set(SPROCESS_ARPACK_FORTRAN_OBJECTS)
foreach(SPROCESS_ARPACK_SOURCE IN LISTS SPROCESS_ARPACK_FORTRAN_SOURCES)
    get_filename_component(SPROCESS_ARPACK_NAME
        "${SPROCESS_ARPACK_SOURCE}" NAME_WE)
    set(SPROCESS_ARPACK_OBJECT
        "${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/sprocess_arpack/${SPROCESS_ARPACK_NAME}.o")
    add_custom_command(OUTPUT "${SPROCESS_ARPACK_OBJECT}"
        COMMAND "${CMAKE_COMMAND}" -E make_directory
            "${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/sprocess_arpack"
        COMMAND "${CMAKE_COMMAND}" -E env
            "LD_LIBRARY_PATH=${GEO3D_GCC_RUNTIME_DIR}"
            "${SPROCESS_IFORT_EXECUTABLE}" -c -fPIC -fvisibility=hidden -auto
            -fno-omit-frame-pointer -O3 -assume protect_parens
            "${SPROCESS_ARPACK_SOURCE}" -o "${SPROCESS_ARPACK_OBJECT}"
        DEPENDS "${SPROCESS_ARPACK_SOURCE}"
        VERBATIM)
    set_source_files_properties("${SPROCESS_ARPACK_OBJECT}"
        PROPERTIES GENERATED TRUE EXTERNAL_OBJECT TRUE)
    list(APPEND SPROCESS_ARPACK_FORTRAN_OBJECTS "${SPROCESS_ARPACK_OBJECT}")
endforeach()

add_custom_target(sprocess_arpack_fortran
    DEPENDS ${SPROCESS_ARPACK_FORTRAN_OBJECTS})
add_dependencies(geo_core sprocess_arpack_fortran)
target_sources(geo_core PRIVATE ${SPROCESS_ARPACK_FORTRAN_OBJECTS})

