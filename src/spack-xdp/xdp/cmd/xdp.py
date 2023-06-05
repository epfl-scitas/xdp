# xdp entry point

from pdb import set_trace as st
description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

_subcommands = {}


def setup_parser(subparser):
    print(f'this is setup_parser')
    st()
    sp = subparser.add_subparsers(metavar="xdp commands", dest="xdp_command")
    xdp_cmds.write.add_command(sp, _subcommands)
    xdp_cmds.clone.add_command(sp, _subcommands)


def xdp(parser, args):
    print(f'this is xdp')
    st()
