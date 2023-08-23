import yaml

from pdb import set_trace as st

data = """
- compiler: gcc@11.3.0
- mpi:
  - openmpi:
      version: 4.1.3
      variants: schedulers=slurm
  - mvapich2@2.3.7:
      variants: +pmi
- blas:
  - openblas@0.3.20 threads=none +locking
  - atlas@3.11.41
- python:
  - python:
      variants: +tkinter ~debug
"""

class Definition:
    # A Definition can be a string (compiler: gcc@11.3.0),
    # a list of strings (mpi: [openmpi@4.1.0, mvapich@2.3.7]),
    # a list of dicts or even a list of mixed elements.

    def __init__(self, name, data):
        self.data = data
        self.name = list(name)[0]
        #st()
        #self.package = self.make_package()

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

    def make_package(self):
        # If not list...
        if not isinstance(self.data, list):
            result = list(self.data)


    def specs(self) -> list:
        """Return list of specs/strings contained in definition
        after having resolved complex packages"""
        # each spec is a string as it is expected by spack.yaml
        pass

class Package:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def __repr__(self):
        return f'{self.data}'

    @property
    def spec(self) -> str:
        """Return package spec"""

        if isinstance(self.data, str):
            result = self.data

        if isinstance(self.data, list):
            for pkg in self.data:
                result = self.data

defs = yaml.safe_load(data)
stack = []
for d in defs:
    print(d)
    stack.append(Definition(d.keys(), d.values()))

st()
print('the end')
