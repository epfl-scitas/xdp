import json
from pdb import set_trace as st

class Package(dict):
    """Provides methods for quering a Package"""

    # For testing
    filters = {"gpu": "nvidia", "mpi": "infiniband" }

    def __init__(self, pkg):
        """Class initialize method"""
        if isinstance(pkg, str):
            pkg = {pkg: None}
        super().__init__(pkg)

    def __str__(self):
        """Print package details using json"""
        return json.dumps(self, sort_keys=False, indent=4)

    @property
    def name(self) -> str:
        """Return dictionary only key"""
        return list(self.keys())[0]

    @property
    def dependencies(self) -> list:
        """Return list of dependencies"""

        # `dependencies` can be a list (of specs) or a dictionary containing the
        #  (a) `common` key which is a list (of specs) and optionally a (b)
        #  dictionary containing the filters whose key would be the filter name.

        deps = []
        if 'dependencies' in self[self.name]:
            d = self[self.name]['dependencies']
            if isinstance(d, list):
                deps = deps + d
            if 'common' in d:
                deps = deps + d['common']
        return deps

    @property
    def variants(self):
        """Return package variants"""

        # ALMOST same code as dependencies (variants is a string, not a list).
        # `variants` can be a `string` or a `dictionary` containing the key
        # `common`.

        tmp = ''
        if 'variants' in self[self.name]:
            v = self[self.name]['variants']
            if isinstance(v, str):
                tmp = v
            elif 'common' in v:
                tmp = v['common']
        return tmp

    @property
    def version(self):
        """Return package version"""
        pass

    @property
    def spec(self, space=True) -> str:
        """Returns package spec string based on package attributes"""

        spc = ' ' if space else ''
        spec = self.variants
        for dep in self.dependencies:
            spec = spec + spc + '^' + dep
        return spec

    @property
    def blacklist(self) -> bool:
        """Returns True if the package module should be blacklisted"""
        pass

    @property
    def autoload(self) -> bool:
        """Returns True if ?"""
        pass

    @property
    def default(self) -> str:
        """Returns the default spec"""
        pass


if __name__ == "__main__":

    # random data
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


    pkg = Package(pkg1)

    print(pkg)
    print(f'pkg.name: {pkg.name}')
    print(f'pkg.variants: {pkg.variants}')
    print(f'pkg.dependencies: {pkg.dependencies}')
    print(f'pkg.spec: {pkg.spec}')

    # filters under variants, multiple filters
    pkg2 = {"krypton":
                 {"variants":
                      {"gpu": {"nivida": "+cuda",
                               "amd": "+rocm"},
                       "mpi": {"infiniband": "+cuda",
                               "ethernet": "~cuda"}},
                  "dependencies":
                       ["bizarro"]
                   }
             }

    pkg = Package(pkg2)

    print(pkg)
    print(f'pkg.name: {pkg.name}')
    print(f'pkg.variants: {pkg.variants}')
    print(f'pkg.dependencies: {pkg.dependencies}')
    print(f'pkg.spec: {pkg.spec}')

    # filters directly under package name variants, multiple filters
    pkg3 = {"brainiac":
                 {"gpu": {"nivida": "+cuda",
                          "amd": "+rocm"},
                  "mpi": {"infiniband": "+cuda",
                          "ethernet": "~cuda"},
                  "dependencies": ["faora", "jax-ur"]
                  }
            }




