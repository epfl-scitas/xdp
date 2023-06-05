# xdp command clone

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

_subcommands = {}

from pdb import set_trace as st

def setup_parser_args(sub_parser):
     sub_parser.add_argument(
         '-r', '--repo',
         help='path to the repository'
     )
     sub_parser.add_argument(
         '-p', '--dest',
         help='destination path'
     )

def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "clone", help="clone some repository ion twice.")
    setup_parser_args(sub_parser)
    command_dict["clone"] = clone


def clone(parser, args):
    print(f'this is clone command')

