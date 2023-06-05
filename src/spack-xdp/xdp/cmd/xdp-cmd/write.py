# xdp command write

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

_subcommands = {}

from pdb import set_trace as st

def setup_parser(subparser):
    print(f'setup_parser for write command')
    manifest = subparser.add_subparsers(help = 'write spack manifest')
    packages = subparser.add_subparsers(help = 'write packages yaml')
    modules = subparser.add_subparsers(help = 'write modules yaml')
    repos = subparser.add_subparsers(help = 'write repos yaml')
    compilers = subparser.add_subparsers(help = 'write compilers yaml')

def write(parser, args):
    print(f'this is write command')
