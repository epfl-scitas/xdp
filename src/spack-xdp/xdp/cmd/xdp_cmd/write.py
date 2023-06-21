# xdp command write

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

from pdb import set_trace as st
import spack.extensions.xdp.cmd.xdp_cmd.xdp_config as xdp_config

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

    config = xdp_config.Config(args)
    st()




def packages(parser, args):
    print(f'this is packages command')


def modules(parser, args):
    print(f'this is modules command')
