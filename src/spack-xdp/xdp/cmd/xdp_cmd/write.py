# xdp command write

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

from pdb import set_trace as st
from collections.abc import MutableMapping
import llnl.util.tty as tty

import spack.extensions.xdp.cmd.xdp_cmd.xdp_config as xdp_config
from spack.extensions.xdp.cmd.xdp_cmd.stack import Stack, PE, PackageList, Package

def add_command(subparser):

    write_parser = subparser.add_parser('write', help="write spack configuration files")
    # Stack and platform should be common to all configuration
    write_parser.add_argument('-s', '--stack', metavar="")
    write_parser.add_argument('-p', '--platform', metavar="")
    write_parser.add_argument('-o','--prefix', metavar="")

    # Add subparser for the different objects to write
    sp = write_parser.add_subparsers(metavar="", dest="xdp_sub_command")

    # Manifest
    manifest_parser = sp.add_parser('manifest', help = 'write spack manifest')

    # Packages
    packages_parser = sp.add_parser('packages', help = 'write packages yaml configuration')
    packages_parser.add_argument('-pkg')

    # Modules
    modules_parser = sp.add_parser('modules', help = 'write modules yaml configuration')
    modules_parser.add_argument('-mod')

# pe.definitions expected output
#
#   {
#       'gcc_stable_compiler': 'gcc@11.3.0',
#       'gcc_stable_mpi': 'openmpi@4.1.3 on infiniband',
#       'gcc_stable_blas': 'openblas@0.3.20 threads=none +locking'
#       ...
#   }

# pe.specs expected output:
#
#   {
#       'gcc_stable': ['mpi', 'gpu', ...],
#       'intel_stable': ['mpi', 'blas', ...]
#       ...
#   }

# pkgs.definitions expected output
#
#   {
#       'list1': ['spec1', 'spec2^dep'],
#       'list2': ['spec1@ver', 'spec2+var'],
#       ...
#   }

# pkgs.specs expected output
#
#   {
#       'list1': {'compilers': ['gcc_stable', 'intel_stable']},
#       'list2': {'compilers': ['gcc_stable', 'intel_stable'], 'dependencies': ['blas', 'gpu']},
#       ...
#   }

def manifest(parser, args):
    print(f'this is manifest command')

    print(f'entering config')
    config = xdp_config.Config(args)
    print(f'config done')

    print(f'entering stack')
    stack = Stack(config)
    print(f'stack done')

# OLD output
#
#   {
#       'gcc_stable_compiler': 'gcc@11.3.0',
#       'gcc_stable_mpi': 'openmpi@4.1.3 on infiniband',
#       'gcc_stable_blas': 'openblas@0.3.20 threads=none +locking'
#       ...
#   }
#
# NEW expected output (similar to pkgs.specs)
#
#   {
#       'gcc_stable_compiler': ['gcc@11.3.0', '...'],
#       'gcc_stable_mpi': ['openmpi@4.1.3 on infiniband', '...],
#       'gcc_stable_blas': ['openblas@0.3.20 threads=none +locking', '...']
#       ...
#   }
#
# >>> THE ONLY DIFFERENCE IS THAT THE VALUES ARE LISTS
# >>> THE TEMPLATES MUST BE UPDATED

    for p in stack.pe:
        for r in p.releases:
            for d in r.definitions:
                # pe_defs['_'.join([p,r,d.name])] = ' '.join(d.specs)
                print(f'{p}_{r}_{d}: {d.specs}')

    st()
    data = {}
    # data['pe_defs'] = stack.pe.definitions
    # data['pkgs_defs'] = stack.pkgs.definitions
    # data['pe_specs'] = stack.pe.specs
    # data['pkgs_specs'] = stack.pkgs.specs
    # stack.write_yaml(data = data)


def packages(parser, args):
    print(f'this is packages command')


def modules(parser, args):
    print(f'this is modules command')
