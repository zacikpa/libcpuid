"""
Module for compiling the C FFI.
"""


from cffi import FFI

LIBCPUID_HEADER = "libcpuid.h"

ffibuilder = FFI()

with open(LIBCPUID_HEADER, "r", encoding="UTF-8") as libcpuid_header:
    ffibuilder.cdef(libcpuid_header.read())

ffibuilder.set_source(
    "_libcpuid_cffi",
    "#include <libcpuid.h>",
    libraries=["cpuid"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
