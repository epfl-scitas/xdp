# 1 filter for variants
pkg1 = {"bizarro": {"variants": {"common": "+sci +experiments",
                                 "gpu": {"nvidia": "+cuda",
                                         "none": "~cuda"}
                               },
                  "dependencies": {"common": ["hdf5 +mpi", "libtiff"],
                                   "gpu": {"nvidia": "pkg +cuda",
                                           "none": "pkg ~cuda"}
                                   }
                  }
        }


# 0 filters fro variants
pkg2 = {"metallo": {"variants": {"common": "~int64 +double +hdf5 +metis +mpi +superlu-dist "
                                           "+hypre +suite-sparse",
                                 },
                  "dependencies": {"common": ["hdf5 ~ipo +mpi +szip +hl +fortran +cxx",
                                              "spec2"],
                                   "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                           "none": "~cuda"}
                                   }
                  }
        }

# 2 filters for variants
pkg3 = {"metallo": {"variants": {"common": "+radiation +cyborg",
                                 "gpu": {"nvidia": "+inteligence",
                                         "none": "~cuda"},
                                 "mpi": {"infiniband": "+speed",
                                         "ethernet": "none"}
                               },
                  "dependencies": {"common": ["green", "kryptonite"],
                                   "gpu": {"nvidia": "+morph",
                                           "none": "~cuda"}
                                   }
                  }
        }

odts = {'gpu': 'nvidia', 'mpi': 'infiniband'}

# which platform ODITIES concern this package ?
def package_odities(plat_odts: dict, pkg_varts: dict) -> list:
    """Returns list of platform odities used by package.

    plat_odts - platform odities as defined in platform file.
    pkg_varts - variants in package common to all platforms.

          plat_odts: {'gpu': 'nvidia', 'mpi': 'infiniband'}
          pkg_varts: {'common': '+sci +exp', 'gpu': {'nvidia': '+cuda', 'amd': '+rocm'}
          return value: ['gpu']
    """
    return [ k for k in plat_odts.keys() if k in pkg_varts ]

# what are the platform RECOMMENDATIONS for this package ?
def platform_recommendation(plat_odts: dict, pkg_odts: list) -> list:
    """Returns the platform recomendation for the odities declared by the package.

    This function will only return the values specified in the platform dictionary
    for which the key was also declared in the package

          plat_odts: {'gpu': 'nvidia', 'mpi': 'infiniband'}
          pkg_odts: ['gpu', `mpi`]
          return value:  ['nvidia', 'infiniband']
    """
    return [ plat_odts[v] for v in pkg_odts ]

# which are the package variants given the platform odities ?
def odts_variants(plat_odts: dict, pkg_varts: dict) -> list:
    """Returns the package variants for the platform odities.

          plat_odts - platform odities as defined in platform file.
          pkg_varts - variants in package common to all platforms.

    """
    odts = package_odities(plat_odts, pkg_varts)
    recs = platform_recommendation(plat_odts, odts)
    return [ pkg_varts[odt][rec] for odt, rec in zip(odts, recs) ]


def print_case(pkg):
    """Print debug info"""

    class Variant(dict):
        def get2(self, key):
            """Return values from subdict in single key dict"""
            k = list(self.keys())[0]
            return self[k][key]

    v = Variant(pkg).get2('variants')
    print(f'pkg variants: {v}')
    print(f'package_odities: {package_odities(odts, v)}')
    print(f'platform_recommendations: {platform_recommendation (odts, package_odities(odts, v))}')
    print(f'odity variants: {odts_variants(odts, v)}')

# Initial data
print(f'platform odts: {odts}')
print()
print_case(pkg1)
print()
print_case(pkg2)
print()
print_case(pkg3)
print()

