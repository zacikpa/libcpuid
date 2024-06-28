"""
Internal module for compiling the C FFI.
"""

import subprocess
import os
from cffi import FFI


class FFIBuildException(Exception):
    """Generic exception for errors occuring during the CFFI build."""


HEADER = "libcpuid.h"

# Obtain libcpuid header file location via pkg-config
try:
    cflags = (
        subprocess.check_output(["pkg-config", "libcpuid", "--cflags-only-I"])
        .decode()
        .strip()
        .split()
    )
except subprocess.CalledProcessError as e:
    if e.returncode == 127:
        raise FFIBuildException(
            "The pkg-config command is necessary to build python-libcpuid."
        ) from e
    if e.returncode == 1:
        raise FFIBuildException("The libcpuid C library (devel) was not found.") from e
    raise FFIBuildException("Error looking for the libcpuid library") from e

# Find an existing libcpuid header file
header_path = None  # pylint: disable=invalid-name
for cflag in cflags:
    header_candidate = os.path.join(cflag[2:], HEADER)
    if os.path.isfile(header_candidate):
        header_path = header_candidate
        break
if header_path is None:
    raise FFIBuildException("Could not find header file of the libcpuid library.")

# Preprocess the header file (python-cffi only accepts preprocessed C definitions)
try:
    PREPROCESSED_HEADER = subprocess.check_output(["gcc", "-E", header_path]).decode()
except subprocess.CalledProcessError as e:
    if e.returncode == 127:
        raise FFIBuildException(
            "The gcc compiler is necessary to build python-libcpuid."
        ) from e
    raise FFIBuildException(
        f"Error preprocessing the libcpuid header file: {e.stderr}"
    ) from e

ffibuilder = FFI()
ffibuilder.cdef(PREPROCESSED_HEADER)
ffibuilder.set_source_pkgconfig(
    "libcpuid._libcpuid_cffi", ["libcpuid"], f"#include <{HEADER}>"
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
