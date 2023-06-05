# xdp command write

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

_subcommands = {}

from pdb import set_trace as st

def setup_parser_args(sub_parser):
    manifest = sub_parser.add_subparsers(help = 'write spack manifest')
    packages = sub_parser.add_subparsers(help = 'write packages yaml')
    modules = subp_arser.add_subparsers(help = 'write modules yaml')
    repos = sub_parser.add_subparsers(help = 'write repos yaml')
    compilers = sub_parser.add_subparsers(help = 'write compilers yaml')

def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "write", help="write spack configuration files")
    setup_parser_args(sub_parser)
    command_dict["write"] = write

def write(parser, args):
    print(f'this is write command')

