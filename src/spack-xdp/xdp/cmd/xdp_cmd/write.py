# xdp command write

description = "commands specific to spack-xdp"
section = "SCITAS"
level = "short"

_subcommands = {}

# def setup_parser(subparser):
#     # spack-sdploy will look for a stack after the name given in the parameter
#     # stack under the stacks directory. If it doesn't find, it will assume that
#     # the parameter stack is a fully qualified file name to a stack.yaml file.
#     subparser.add_argument(
#         '-s', '--stack',
#         help='path to the stack file'
#     )
#     subparser.add_argument(
#         '-p', '--platform',
#         help='path to the platform file.'
#     )
#     subparser.add_argument(
#         '--prefix', type=str,
#         help='path to the stacks directory.'
#     )
#     subparser.add_argument(
#         '-d', '--debug', action='store_true', default=False,
#         help='print debug information.'
#    )


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
