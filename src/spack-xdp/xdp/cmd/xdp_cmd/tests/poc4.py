import yaml

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

data = yaml.safe_load(data)
plat_odts = {'gpu': 'nvidia', 'mpi': 'infiniband'}

def update_nested_dict(dic):
    for k, v in dic.items():
        if isinstance(v, dict):
            update_nested_dict(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    update_nested_dict(item)
        else:
            if is_var_odity(k, v):
                dic[k] = 'edu'

data = {'a': {'b': {'c': [{'d': 1, 'e': 2}, 1, {'g': 1, 'h': 2}, [{'i': {'j': 1}}]]}}}
print(data)
update_nested_dict(data)
print(data)
