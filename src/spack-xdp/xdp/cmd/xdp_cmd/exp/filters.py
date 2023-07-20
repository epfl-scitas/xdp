import json
from pdb import set_trace as st

filters = {"gpu": "nvidia", "mpi": "infiniband"}

# 1 filter for variants
pkg1 = {"metallo": {"variants": {"common": "~int64 +double +hdf5 +metis +mpi +superlu-dist "
                                           "+hypre +suite-sparse",
                                 "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                         "none": "~cuda"}
                               },
                  "dependencies": {"common": ["hdf5 ~ipo +mpi +szip +hl +fortran +cxx",
                                              "spec2"],
                                   "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                           "none": "~cuda"}
                                   }
                  }
        }

# 2 filters for variants
pkg2 = {"metallo": {"variants": {"common": "~int64 +double +hdf5 +metis +mpi +superlu-dist "
                                           "+hypre +suite-sparse",
                                 "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                         "none": "~cuda"},
                                 "mpi": {"infiniband": "+mpi",
                                         "ethernet": "none"}

                               },
                  "dependencies": {"common": ["hdf5 ~ipo +mpi +szip +hl +fortran +cxx",
                                              "spec2"],
                                   "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                           "none": "~cuda"}
                                   }
                  }
        }

# 0 filters fro variants
pkg3 = {"metallo": {"variants": {"common": "~int64 +double +hdf5 +metis +mpi +superlu-dist "
                                           "+hypre +suite-sparse",
                                 },
                  "dependencies": {"common": ["hdf5 ~ipo +mpi +szip +hl +fortran +cxx",
                                              "spec2"],
                                   "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                           "none": "~cuda"}
                                   }
                  }
        }

# Which filters are declared in package ?
# The answer is the subset of filters declared in platform which are also
# used in the package definition.
def fip(fltrs, pkg):
    """Returns list of filters used in package"""
    return [ k for k in fltrs.keys() if k in pkg ]

# Which values are declared in package for given filters ?
def fv(fltrs, pkg):
    """Returns filter value"""
    st()
    return fltrs[fip(fltrs,v)[0]]

v = pkg1["metallo"]["variants"]
print(fip(filters, v))
print(fv(filters, v))

v = pkg2["metallo"]["variants"]
print(fip(filters, v))
print(fv(filters, v))

v = pkg3["metallo"]["variants"]
print(fip(filters, v))
print(fv(filters, v))

st()

