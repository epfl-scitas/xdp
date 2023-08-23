#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                              #
#  SCITAS STACK DEPLOYMENT 2023, EPFL                                          #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                                                              #
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import spack.environment as ev
import llnl.util.tty as tty

from pdb import set_trace as st
from spack.extensions.xdp.cmd.xdp_cmd.yaml_manager import ReadYaml
import spack.extensions.xdp.cmd.xdp_cmd.util as util


class Config(object):
    """Process arguments and create config object.

    This class will handle the parsing of the arguments for all the commands.
    Its goal is to define the variables baed on the argument given at command
    line and decide if its value should come from the:

            1 command line     (highest priority)
            2 xdp.yaml
            3 class contructor (lowest priority)"""

    _instance = None

    def __new__(cls, *args, **kw):
        """Class constructor"""

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, args):
        """Fills configuration options"""

        self.args = args # temporary experiment

        # These are the only parameters (4) the user can define at command line.
        # line:prefix, stack and platform can also be defined in environment.
        self.stack = 'carrot'
        self.platform = 'rabbit'
        self.prefix = os.path.join(util.get_prefix(), 'stacks')

        # Used in config.yaml - config:install_tree:root
        self.stack_ver = 'v1'

        # The following variables are used only for data separation purposes.
        # They may be redefined in xdp.yaml (higher priority).
        self.platforms_dir = 'platforms'
        self.platforms_path = None
        self.templates_dir = 'templates'
        self.templates_path = None
        # Templates
        self.spack_yaml_template = 'spack.yaml.j2'
        self.packages_yaml_template = 'packages.yaml.j2'
        self.modules_yaml_template = 'modules.yaml.j2'
        self.repos_yaml_template = 'repos.yaml.j2'
        self.mirrors_yaml_template = 'mirrors.yaml.j2'
        self.upstreams_yaml_template = 'upstreams.yaml.j2'
        self.concretizer_yaml_template = 'concretizer.yaml.j2'
        self.config_yaml_template = 'config.yaml.j2'
        # Spack configuration files (output)
        self.spack_yaml = 'spack.yaml'
        self.spack_yaml_path = None
        self.packages_yaml = 'packages.yaml'
        self.packages_yaml_path = None
        self.modules_yaml = 'modules.yaml'
        self.modules_yaml_path = None
        self.repos_yaml = 'repos.yaml'
        self.repos_yaml_path = None
        self.mirrors_yaml = 'mirrors.yaml'
        self.mirrors_yaml_path = None
        self.concretizer_yaml = 'concretizer.yaml'
        self.concretizer_yaml_path = None

        conf = ReadYaml()
        conf.read('xdp.yaml')
        c = conf.data['config']

        # prefix:
        if args.prefix:
            self.prefix = args.prefix # from command line
        elif 'prefix' in conf.data['config']:
            if conf.data['config']['prefix']:
                self.prefix = conf.data['config']['prefix'] # from xdp.yaml

        # stack (str) name of the stack
        if args.stack:
            self.stack = args.stack
        elif 'stack' in conf.data['config']:
            if conf.data['config']['stack']:
                self.stack = conf.data['config']['stack']

        # platform (str) name of the platform
        if args.platform:
            self.platform = args.platform
        elif 'platform' in conf.data['config']:
            if conf.data['config']['platform']:
                self.platform = conf.data['config']['platform']

        # output_path:
        if os.environ.get('SPACK_SYSTEM_CONFIG_PATH') is not None:
            self.output_path = os.environ.get('SPACK_SYSTEM_CONFIG_PATH')
        elif c['output_path'] is not None:
            self.output_path = c['output_path']
        else:
            self.output_path = os.getcwd()

        # Full path to yaml files can only be known
        # after settled on prefix, stack and platform.
        stack_path = os.path.join(self.prefix, self.stack)
        self.stack_yaml = os.path.join(stack_path, self.stack + '.yaml')
        self.platform_yaml = os.path.join(stack_path, self.platforms_dir, self.platform + '.yaml')
        # Hardcoded common.yaml bypassing xdp.yaml
        self.commons_yaml = os.path.join(stack_path, 'common.yaml')

        # See that in the code below we are using the 'templates_dir' value
        # from the xdp.yaml and we are ignoring that this variable could be
        # empty. For a more complete approach we should first choose the
        # 'templates_dir' value between the one given in xdp.yaml and the
        # default defined in the initializer of this class.

        # templates_path:
        # TODO: fix this logic
        if 'templates_path' in c:
            if c['templates_path']:
                self.templates_path = c['templates_path']
            else:
                self.templates_path = os.path.join(stack_path, c['templates_dir'])

    def __getattr__(self):
        print('This is __getatr__')

    #def __getattribute__(self):
    #    print('This is __getattribute__')

    def info(self, verbose=False):
        """Print xdp configuration after having
        processed all sources."""

        # Main
        print('Main parameters')
        print(f'stack: {self.stack}')
        print(f'platform: {self.platform}')
        print(f'prefix: {self.prefix}')
        print(f'output_path: {self.output_path}')

        if verbose:

            # Other
            print(f'stack_ver: {self.stack_ver}')

            # YAML configuration
            print(f'stack_yaml: {self.stack_yaml}')
            print(f'platform_yaml: {self.platform_yaml}')
            print(f'commons.yaml: {self.commons_yaml}')

            # Directory names and paths
            print(f'platforms_dir: {self.platforms_dir}')
            print(f'platforms_path: {self.platforms_path}')
            print(f'templates_dir: {self.templates_dir}')
            print(f'templates_path: {self.templates_path}')

            # Templates
            print(f'spack_yaml_template : {self.spack_yaml_template}')
            print(f'packages_yaml_template: {self.packages_yaml_template}')
            print(f'modules_yaml_template: {self.modules_yaml_template}')
            print(f'repos_yaml_template: {self.repos_yaml_template}')
            print(f'mirrors_yaml_template: {self.mirrors_yaml_template}')
            print(f'concretizer_yaml_template: {self.concretizer_yaml_template}')
            print(f'upstreams_yaml_template = {self.upstreams_yaml_template}')
            print(f'config_yaml_template: {self.config_yaml_template}')

            # Spack configuration files
            print(f'spack_yaml: {self.spack_yaml}')
            print(f'spack_yaml_path: {self.spack_yaml_path}')
            print(f'packages_yaml: {self.packages_yaml}')
            print(f'packages_yaml_path: {self.packages_yaml_path}')
            print(f'modules_yaml: {self.modules_yaml}')
            print(f'modules_yaml_path: {self.modules_yaml_path}')
            print(f'repos_yaml: {self.repos_yaml}')
            print(f'repos_yaml_path: {self.repos_yaml_path}')
            print(f'mirrors_yaml: {self.mirrors_yaml}')
            print(f'mirrors_yaml_path: {self.mirrors_yaml_path}')
            print(f'concretizer_yaml: {self.concretizer_yaml}')
            print(f'concretizer_yaml_path: {self.concretizer_yaml_path}')
