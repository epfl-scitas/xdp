from collections.abc import MutableMapping
import yaml

from pdb import set_trace as st

data = """
gcc:
  metadata:
    section: pe
  stable:
    # str
    compiler: gcc@11.3.0
# [dict, dict]
    mpi:
      - openmpi:
          version: 4.1.3
          variants:
            common: schedulers=slurm
            mpi:
              infiniband: +pmi
              ethernet: fabrics=verbs
            gpu:
              nvidia: +cuda
              none: ~cuda
          dependencies:
            - hwloc ~libxml2
      - mvapich2@2.3.7:
          variants:
            common: schedulers=slurm
            gpu:
              nvidia: +cuda
              none: ~cuda
    # [str, str]
    blas:
      - openblas@0.3.20 threads=none +locking
      - atlas@3.11.41
    # dict
    python:
      python:
        variants: <python3> +tkinter +optimizations ~debug +ssl ~libxml2
    # [str, dict]
    gpu:
      - pkg1
      - pkg2:
          variants: +spec
"""

def is_var_odity(key, value):
    """Return true if key is an odity defined in the platform file
    and value is a dictionary having at most n keys, all of them
    being strings."""

    found = True
    # the key is declared as an odity in platform file -->
    if not key in plat_odts:
        found = False
    # --> this key is a dictionary -->
    if found and not isinstance(value, MutableMapping):
        found = False
    # --> and its keys are strings.
    if found:
        for k,v in value.items():
            if not isinstance(v, str):
                found = False
    return found

def is_dep_odity(key, value):
    """Return true if key is an odity defined in the platform file
    and value is a dictionary having at most n keys, all of them
    being lists of strings."""

    found = True
    if not key in plat_odts:
        found = False
    if found and not isinstance(value, MutableMapping):
        found = False
    if found:
        for k,v in value.items():
            if not isinstance(v, list):
                found = False
            # each element in list is a string
            if found:
                for item in v:
                    if not isinstance(item, str):
                        found = False
    return found

def resolve_odt(odt: str, choices: dict) -> str:
    """"""
    # mpi: {infiniband: +pmi, ethernet: fabrics=verbs}
    return choices[plat_odts[odt]]

class Value:
    def __init__(self, v):
        self.v = v

def iterator(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k, (val := Value(v))
            o[k] = val.v
            yield from iterator(v)
    if isinstance(o, list):
        for v in o:
            yield from iterator(v)

data = yaml.safe_load(data)
plat_odts = {'gpu': 'nvidia', 'mpi': 'infiniband'}

print(data)
st()
for k, val in iterator(data):
    if is_var_odity(k, val.v):
        val.v = resolve_odt(k, val.v)
print(data)

print('end')
st()
