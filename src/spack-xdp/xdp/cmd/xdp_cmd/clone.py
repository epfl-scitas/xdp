# xdp command clone

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

from pdb import set_trace as st


def add_command(parser):
    sub_parser = parser.add_parser(
         "clone", help="clone some repository ion twice.")
    sub_parser.set_defaults(xdp_sub_command='clone')
    sub_parser.add_argument(
        '-r', '--repo',
        help='path to the repository'
    )
    sub_parser.add_argument(
        '-p', '--dest',
        help='destination path'
    )


def clone(parser, args):
    print(f'this is clone command')

