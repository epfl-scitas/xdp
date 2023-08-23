import re
import yaml

from pdb import set_trace as st

data="""
- fio
- gcc@11.3.0
- openblas@0.3.20 threads=none +locking
- openmpi@4.1.3 fabrics=ucx +pmi ~memchecker ~rsh ^hwloc ~libxml2
"""

name_re = re.compile(r"""(?P<name>^[0-9a-zA-Z_-]*)""", re.X)
version_re = re.compile(r"""(?P<version>[@]{1}[0-9.a-zA-Z_-]*)""", re.X)
variants_re = re.compile(r"""(?P<variants>[+|~]{1}[]a-z0-9]*)""", re.X)

def _version(spec: str) -> str:
    """Return version from spec"""
    match = re.search(version_re, spec)
    if match is not None:
        return match.group()[1:]
    else:
        return ''

def _name(spec: str) -> str:
    """Return package name from spec"""
    match = re.search(name_re, spec)
    if match is not None:
        return match.group()
    else:
        return ''

def _variants(spec: str) -> str:
    """Return variants from spec"""
    variants = spec.replace(_name(spec), '', 1)
    variants = variants.replace(_version(spec), '', 1)
    return variants

defs = yaml.safe_load(data)
for p in defs:
    print(f'str: {p}\n',
          f'name: {_name(p)}',
          f'version: {_version(p)}',
          f'variants: {_variants(p)}')

