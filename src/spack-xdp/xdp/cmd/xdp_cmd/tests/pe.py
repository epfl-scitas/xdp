import yaml
from pdb import set_trace as st

content = """
core:
  metadata:
    section: core
  compiler: gcc@8.5

gcc:
  metadata:
    section: pe
  stable:
    compiler: gcc@11.3.0
    mpi:
      infiniband: openmpi@4.1.3 on infiniband
      ethernet: openmpi@4.1.3 on ethernet
    gpu:
      nvidia: cuda@11.7.0
      none: ""
  future:
    compiler: gcc@12.1
    blas: openblas@0.3.20 threads=none +locking
    python: python@3.11.4 +tkinter
    gpu:
      nvidia: cuda@11.7.0
      none: ""

intel:
  metadata:
    section: pe
  stable:
    compiler: intel@2021.6.0
    compiler_spec: intel-oneapi-compilers-classic@2021.6.0
    gpu:
      nvidia: cuda@11.5.0
      none: ""
  deprecated:
    compiler: intel@2021.6.0
"""

class Release:

    # Temporary define here the platform odities
    plat_odts = {'gpu': 'nvidia', 'mpi': 'infiniband', 'gnu': 'xpto'}

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def __repr__(self):
        return f'{self.data.keys()}'

    @property
    def compiler(self) -> str:
        """Return compiler for release"""
        return self.data['compiler']

    @property
    def python(self):
        """Return python for release"""
        return self._library('python')

    @property
    def blas(self):
        """Return blas for release"""
        return self._library('blas')

    @property
    def mpi(self):
        """Return mpi for release"""
        return self._library('mpi')

    @property
    def gpu(self):
        """Return gpu for release"""
        return self._library('gpu')

    def _library(self, library):
        # if library is a dict, then it is an odty
        try:
            if isinstance(self.data[library], str):
                return self.data[library]
            else:
                return self._odity(self.data[library])
        except:
            pass

    def _odity(self, pkg_odt: dict) -> str:
        """Returns the package variants for the platform odities.

               pkg_odt : {'nvidia': '+cuda', 'amd': 'roce'}
              plat_odt : {'mpi': 'infiniband', 'gpu': 'nvidia'}
          return value : '+cuda'
        """
        return ''.join(pkg_odt.get(odt) for odt in self.plat_odts.values() if odt in pkg_odt)

    def _library_simple(self, library):
        try:
            return self.data[library]
        except:
            print(f'{release} has no {library} library')
            return 1

    @property
    def libraries(self) -> list:
        pass

class PE:
    """Return PE object

    REMARKS:
    > Only one compiler is allowed per PE
    """
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def __repr__(self):
        return f'{self.data}'

    @property
    def name(self) -> str:
        """Returns first key found in Yaml"""
        return list(self.data.keys())[0]

    @property
    def releases(self) -> list:
        """Return available releases"""
        return list(self.data[self.name].keys())

    @property
    def stable(self) -> dict:
        """Return stable dict"""
        return self._release('stable')

    @property
    def future(self) -> dict:
        """Return future dict"""
        return self._release('future')

    @property
    def deprecated(self) -> dict:
        """Return deprecated dict"""
        return self._release('deprecated')

    def _release(self, release):
        try:
            return Release(self.data[self.name][release])
        except:
            print(f'{self.name} has no {release} release')
            return None

    def definitions(self):
        """Returns PE definitions"""

        # expected output:
        #
        #   {
        #       'gcc_stable_compiler': 'gcc@11.3.0',
        #       'gcc_stable_mpi': 'openmpi@4.1.3 on infiniband',
        #       'gcc_stable_blas': 'openblas@0.3.20 threads=none +locking'
        #       ...
        #   }

class PE:
    """Return PE object

    REMARKS:
    > Only one compiler is allowed per PE
    """
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def __repr__(self):
        return f'{self.data}'

    @property
    def name(self) -> str:
        """Returns first key found in Yaml"""
        return list(self.data.keys())[0]

    @property
    def releases(self) -> list:
        """Return available releases"""
        return list(self.data[self.name].keys())

    @property
    def stable(self) -> dict:
        """Return stable dict"""
        return self._release('stable')

    @property
    def future(self) -> dict:
        """Return future dict"""
        return self._release('future')

    @property
    def deprecated(self) -> dict:
        """Return deprecated dict"""
        return self._release('deprecated')

    def _release(self, release):
        try:
            return Release(self.data[self.name][release])
        except:
            print(f'{self.name} has no {release} release')
            return None

    def definitions(self):
        """Returns PE definitions"""

        # expected output:
        #
        #   {
        #       'gcc_stable_compiler': 'gcc@11.3.0',
        #       'gcc_stable_mpi': 'openmpi@4.1.3 on infiniband',
        #       'gcc_stable_blas': 'openblas@0.3.20 threads=none +locking'
        #       ...
        #   }

        pass

if __name__ == "__main__":

    # The goal of this script is to create the method to add to the Stack class
    # that will read the PE defined in the stack file and create the PE objects.
    stack = yaml.safe_load(content)

    odts = {'gpu': 'nvidia', 'mpi': 'infiniband', 'gnu': 'xpto'}

    pes = []
    for pe, release in stack.items():
        release.pop('metadata') # This removes 'metadata' key and will error on
                                # second run due to missing key
        pes.append(PE({pe:release}))

    core = pes[0]
    gcc = pes[1]
    intel = pes[2]

    print(f'core: {core}')
    print(f'gcc: {gcc}')
    print(f'intel: {intel}')

    print(f'core.releases: {core.releases}')
    print(f'gcc.releases: {gcc.releases}')
    print(f'intel.releases: {intel.releases}')

    print(f'core.stable: {core.stable}')
    print(f'gcc.stable: {gcc.stable}')
    print(f'intel.future: {intel.future}')

    # None object has no attribute 'compiler'
    # >>> print(f'core.stable.compiler: {core.stable.compiler}')

    print(f'gcc.stable.compiler: {gcc.stable.compiler}')
    print(f'gcc.future.python: {gcc.future.python}')

    print(f'gcc.stable.mpi: {gcc.stable.mpi}')
    print(f'gcc.stable.gpu: {gcc.stable.gpu}')

    gcc.definitions

    # st()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#                                                                             #
# ADD CLASS METHOD DYMANICALY                                                 #
#                                                                             #
#                                                                             #
#                                                                             #
#                                                                             #
#                                                                             #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# # define a class object (your class may be more complicated than this...)
# class A(object):
#     pass
#
# # a class method takes the class object as its first variable
# def func(cls):
#     print 'I am a class method'
#
# # you can just add it to the class if you already know the name you want to use
# A.func = classmethod(func)
#
# # or you can auto-generate the name and set it this way
# the_name = 'other_func' 
# setattr(A, the_name, classmethod(func))
