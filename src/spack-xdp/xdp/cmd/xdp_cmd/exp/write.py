# xdp command write

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

from pdb import set_trace as st
import llnl.util.tty as tty

import spack.extensions.xdp.cmd.xdp_cmd.xdp_config as xdp_config

import spack.extensions.xdp.cmd.xdp_cmd.manifest as manifst
from spack.extensions.xdp.cmd.xdp_cmd.stack import Stack, PE, PackageList, Package

def add_command(subparser):

    write_parser = subparser.add_parser('write', help="write spack configuration files")
    # Stack and platform should be common to all configuration
    write_parser.add_argument('-s', '--stack', metavar="")
    write_parser.add_argument('-p', '--platform', metavar="")
    write_parser.add_argument('-o','--prefix', metavar="")

    # Add subparser for the different objects to write
    sp = write_parser.add_subparsers(metavar="", dest="xdp_sub_command")

    # Temporary
    yeah_parser = sp.add_parser('yeah', help = 'write spack manifest')

    # Manifest
    manifest_parser = sp.add_parser('manifest', help = 'write spack manifest')
    manifest_parser.add_argument('-manif')

    # Packages
    packages_parser = sp.add_parser('packages', help = 'write packages yaml configuration')
    packages_parser.add_argument('-pkg')

    # Modules
    modules_parser = sp.add_parser('modules', help = 'write modules yaml configuration')
    modules_parser.add_argument('-mod')


# command to be renamed to manifest
# new manifest command using the new PE class
def yeah(parser, args):
    print(f'yeah this is command')

    # if no arguments are passed to spack
    # xdp then it should print usage

    print(f'Entering config')
    config = xdp_config.Config(args)
    print(f'Config done')

    # Process Programming Environment section.
    #print(f'Initialize Stack object')
    #stck = manifst.Manifest(config)
    #print(f'Stack object initialized')

    # Concatenate all dicts
    #data = {}
    #data['pe_defs'] = stck.pe_defs() # Only this method requires data from the PE
                                      # This makes us think that we could have two
                                      # different classes both inhereting from the
                                      # Stack for the single purpose of having each
                                      # one its own __str__ method (but possibly
                                      # other will came up later)


    stack = Stack(config)

    p = {"petsc": {"variants": {"common": "~int64 +double +hdf5 +metis +mpi +superlu-dist "
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

    petsc = {"variants": {"common": "~int64 +double +hdf5 +metis +mpi +superlu-dist "
                                    "+hypre +suite-sparse",
                          "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                  "none": "~cuda"}
                          },
             "dependencies": {"common": ["hdf5 ~ipo +mpi +szip +hl +fortran +cxx"],
                              "gpu": {"nvidia": "+cuda cuda_arch=<cuda_arch>",
                                      "none": "~cuda"}
                              }
             }

    package = Package(p)
    st()


    pkg_list = PackageList(stack.pkgs())

    pkgs.definitions()


    #data['pkgs_defs'] = stack.pkgs_defs
    #data['pe_specs'] = stack.pe_specs
    #data['pkgs_specs'] = stack.pkgs_specs


def manifest(parser, args):
    print(f'this is manifest command')

    # 1.set up running parameters
    # 2.create data structures
    # 3.output results
    config = xdp_config.Config(args)

    # Process Programming Environment section.
    # stack = spack_yaml.SpackYaml(config)

    st()
    print('done')

    # Concatenate all dicts
    data = {}
    data['pe_defs'] = stack.pe_defs
    data['pkgs_defs'] = stack.pkgs_defs
    data['pe_specs'] = stack.pe_specs
    data['pkgs_specs'] = stack.pkgs_specs

    stack.write_yaml(data = data)


def packages(parser, args):
    print(f'this is packages command')


def modules(parser, args):
    print(f'this is modules command')
