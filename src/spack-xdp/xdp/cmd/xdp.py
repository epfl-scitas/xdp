# xdp entry point

import sys
import spack
import llnl.util.tty as tty

# The extensions are prefixed with 'xdp_'. We will later use
# this prefix to fetch the modules.
import spack.extensions.xdp.cmd.xdp_cmd.write as xdp_write
import spack.extensions.xdp.cmd.xdp_cmd.clone as xdp_clone

from pdb import set_trace as st
description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"


def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar="xdp commands", dest="xdp_command")
    xdp_clone.add_command(sp)
    xdp_write.add_command(sp)


def xdp(parser, args):

    # Debug
    tty.debug('this is xdp')
    tty.debug(f'xdp_command: {args.xdp_command}')
    if 'xdp_sub_command' in args:
        tty.debug(f'sub_command: {args.xdp_sub_command}')

    # Execute command
    cmd_mod = getattr(sys.modules[__name__], 'xdp_'+args.xdp_command)
    cmd_fnc = getattr(cmd_mod, args.xdp_sub_command)
    cmd_fnc(parser, args)


if __name__ == '__main__':
    f'Testing module: xdp'

