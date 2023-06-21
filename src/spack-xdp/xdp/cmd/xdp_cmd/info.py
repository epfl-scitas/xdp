# xdp command info

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

import spack.extensions.xdp.cmd.xdp_cmd.xdp_config as xdp_config
from pdb import set_trace as st


def add_command(parser):
    info_parser = parser.add_parser(
         "info", help="show xdp configuration.")
    info_parser.set_defaults(xdp_sub_command='info')
    info_parser.add_argument('-s', '--stack', metavar="", help="stack name")
    info_parser.add_argument('-p', '--platform', metavar="", help="platform name")
    info_parser.add_argument('-o', '--prefix', metavar="", help="path to stacks directory")
    info_parser.add_argument('-v', '--verbose', action='store_true', help="show full configuration")


def info(parser, args):

    config = xdp_config.Config(args)
    config.info(args.verbose)

