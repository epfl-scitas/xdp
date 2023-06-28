# xdp command write

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

from pdb import set_trace as st
import llnl.util.tty as tty

import spack.extensions.xdp.cmd.xdp_cmd.xdp_config as xdp_config
import spack.extensions.xdp.cmd.xdp_cmd.spack_yaml as spack_yaml

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
    manifest_parser.add_argument('-manif')

    # Packages
    packages_parser = sp.add_parser('packages', help = 'write packages yaml configuration')
    packages_parser.add_argument('-pkg')

    # Modules
    modules_parser = sp.add_parser('modules', help = 'write modules yaml configuration')
    modules_parser.add_argument('-mod')


def manifest(parser, args):
    print(f'this is manifest command')

    # 1.set up running parameters
    # 2.create data structures
    # 3.output results
    config = xdp_config.Config(args)

    # Process Programming Environment section.
    stack = spack_yaml.SpackYaml(config)

    # Create PE definitions dictionary
    st()
    stack.create_pe_defs()

    # Create packages definitions dictionary
    st()
    stack.create_pkgs_defs()

    # Create PE matrix dictionary
    st()
    stack.create_pe_specs()

    # Create package lists matrix dictionary
    st()
    stack.create_pkgs_specs()

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
