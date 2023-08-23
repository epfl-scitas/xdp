# This script shows the syntax change for declaring a PE.
# The keys under the `release` value can be string, lists or dictionaries.
# List members can also be strings or dictionaries mixed (but not lists).
#
# The platform file defines the odities (mpi, gpu, etc).
# More than one odity can be declared per package.
# An odity is an object like:
#
#   odt: {key_1: val_1, ..., key_n: val_n}
#
# where:
#        - odt is a dictionary
#        - odt is declared in platform file
#        - val_1, ..., val_n are strings
#
# Given the above definition of odity, the mpi key under
# stable is not an odity because its keys are not strings.
#
# The `mpi` key `under` `openmpi:variants` does conform to the
# above definition.

from collections.abc import MutableMapping
import yaml
from pdb import set_trace as st

data = """
gcc:
  metadata:
    section: pe
  stable:
    compiler:
      - gcc@11.3.0
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
    blas:
      - openblas@0.3.20 threads=none +locking
      - atlas@3.11.41
# 19
mpi:
  infiniband: +yes
  ethernet: ~no
sample_package_list:
  metadata: { section: packages }
  pe: [intel_stable]
  dependencies: [mpi, blas, python3]
  packages:
    - petsc:
        default:
          variants:
            common:  ~int64 +double +hdf5 +metis +mpi +superlu-dist +hypre +suite-sparse
            gpu:
              nvidia: +cuda cuda_arch=<cuda_arch>
              none: ~cuda
    - cp2k:
        version: 9.1
        variants:
          common: +mpi +plumed +openmp smm=blas
          gpu:
            nvidia: +cuda cuda_arch=<cuda_arch>
            none: ~cuda
    - slepc:
        variants:
        dependencies:
          common:
            - hdf5 ~ipo +mpi +szip +hl +fortran +cxx
          gpu:
            nvidia: [petsc +cuda cuda_arch=<cuda_arch> , suite-sparse +cuda]
            none: []
    - py-petsc4py:
        dependencies:
          common:
            - hdf5 ~ipo +mpi +szip +hl +fortran +cxx
          gpu:
            nvidia: [petsc +cuda cuda_arch=<cuda_arch>, suite-sparse +cuda]
            none: []
"""
# total = 47 without odities

# The goal of this script is to replace an odity by its value.
# Given the odts declater for the platform in plat_odts, we want
# to replace
#
#   gpu: {'nvidia': '+cuda', 'none': '~cuda'}
#
# with
#
#   gpu: '+cuda'
#
# The dictionary becomes a key. It will be the responsability from
# the method variants to collect all (possibly more than one) odities
# and concatenate them with the variants key.

plat_odts = {'gpu': 'nvidia', 'mpi': 'infiniband'}

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

# Odities for dependencies are not declared in the same way as odities for
# variants. In the dependencies case, an odity will declare a list of packages.
# In this case, the values are lists of strings and not just strings.
#
#   gpu:
#     nvidia: [ petsc +cuda cuda_arch=<cuda_arch>, suite-sparse +cuda ]
#     none: []

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

def read_list(l):
    # Thsi works for both lists and dictioinaries
    # This does not work !
    data = {}

    for item in l:
        if isinstance(item, str):
            data[item] = 's'
        if isinstance(item, dict):
            data[''.join(item.keys())] = 'd'
    return data

def print_list(l):

    return list(read_list(l).keys())

# A list can ONLY contain `strings` or `dictionaries`

def dic_walk(dic):
    for k,v in dic.items():

        if is_var_odity(k,v):
            print('odity found for variant!', v, '\n')
            # continue
        if is_dep_odity(k,v):
            print('odity found for dependency!', v, '\n')
            # continue
        if is_var_odity(k,v) or is_dep_odity(k,v):
            continue

        if isinstance(v, dict):
            print(f'\'{k}\' is dict')
            print(' >> keys:', list(v.keys()))
            print(' >> value:', v, '\n')
            dic_walk(v)
        if isinstance(v, list):
            print(f'\'{k}\' is list')
            print(' >> values:', print_list(v), '\n')
            for item in v:
                if isinstance(item, dict):
                    #print('\'' + ''.join(item.keys()) + '\'', 'is dict')
                    dic_walk(item)
                else:
                    print(f'\'{item}\' is string')
                    print(' >> end of line\n')
                    # print(f' >> value: {v}\n')
        if isinstance(v, str):
            print(f'\'{k}\' is string')
            print(' >> end of line')
            print(f' >> value: {v}\n')

def dic_len(dic):

    for k,v in dic.items():

        length += 1

        if isinstance(v, dict):
            length += 1
            dic_len(v)

        if isinstance(v, list):
            for item in v:
                length += 1
                if isinstance(item, dict):
                    dic_len(item)
    return length

def dic_len_3(dic):

    global length
    for k,v in dic.items():
        length += 1

        if isinstance(v, dict):
            dic_len_3(v)

        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    dic_len_3(item)

def dic_len_2(dic, length = 0):

    for k,v in dic.items():
        length += 1
        print(f'length: {length}')

        if isinstance(v, dict):
            print(f'\'{k}\' is dict')
            print(' >> keys:', list(v.keys()))
            print(' >> value:', v, '\n')

            length += dic_len_2(v, length)
            print(f'length: {length}')

        if isinstance(v, list):
            print(f'\'{k}\' is list')
            print(' >> values:', print_list(v), '\n')

            for item in v:
                if isinstance(item, dict):

                    print(f'length: {length}')
                    length += dic_len_2(item, length)
                    print(f'length: {length}')

                else:
                    print(f'\'{item}\' is string')
                    print(' >> end of line\n')
        if isinstance(v, str):
            print(f'\'{k}\' is string')
            print(' >> end of line')
            print(f' >> value: {v}\n')

    return length

if __name__ == "__main__":
    stack = yaml.safe_load(data)

    s0 = {} # 0
    s1 = {'a':1} # 1
    s2 = {'a':[1,2,3]} # 4
    s3 = {'a':1, 'b':2, 'c':3} # 3
    s4 = {'a':1, 'b':{'a':1}} # 3
    s5 = {'a':[{'a':1},1]} # 3
    s6 = {'a':[{'a':1}]} # 2

    s7 = {'gcc':
          {'metadata': {'section': 'pe'},
           'stable': {'compiler': ['gcc@11.3.0'],
                      'mpi': [
                        {'openmpi': {
                          'version': '4.1.3',
                          'variants': {
                              'common': 'schedulers=slurm',
                              'mpi': {'infiniband': '+pmi', 'ethernet': 'fabrics=verbs'},
                              'gpu': {'nvidia': '+cuda', 'none': '~cuda'}},
                          'dependencies': ['hwloc ~libxml2']
                      }},
                        {'mvapich2': {
                          'variants': {
                              'common': 'schedulers=slurm',
                              'gpu': {'nvidia': '+cuda', 'none': '~cuda'},
                              'blas': ['openblas +locking', 'atlas']}
                        }
                      }]
           }
          }
         }

    resu = [ 0, 1, 4, 3, 3, 3, 2 ]
    dics = [ s0, s1, s2, s3, s4, s5, s6 ]
    #lens = [ dic_len(d) for d in dics ]

    test = lambda a,b: '[X]' if a!=b else '   '

    #for d,l,r in zip(dics,lens, resu):
    #    print(test(l,r), d, l)

    print()
    print(s7)
    print()

    # RESULT = 27
    length = 0
    dic_len_3(s7)
    print(f'length: {length}')
    st()
