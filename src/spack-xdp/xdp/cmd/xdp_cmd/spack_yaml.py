#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                              #
# SCITAS STACK DEPLOYMENT 2023, EPFL                                           #
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
from collections.abc import MutableMapping
from copy import deepcopy
import inspect

import llnl.util.tty as tty
import spack.schema

from .stack_file import StackFile, FilterException
from .util import *

from spack.extensions.xdp.cmd.xdp_cmd.stack_file import StackFile

class SpackYaml(StackFile):
    """Manage the packages section in stack.yaml"""

    def __init__(self, config):
        """Declare class structs"""

        # Super will invoke the __init__ method from the StackFile class
        # TODO config should be read in StackFile class ?

        super().__init__(config)
        self.schema = spack.schema.env.schema

        # These variables will be used in StackFile class.
        # Each command that write an Yaml file must define these 4 variables.
        # This technique allows for individual command customization of each
        # one of these parameters and at the same time to reuse the functions
        # all gathered in a single module.
        self.templates_path = self.config.templates_path
        self.template_file = self.config.spack_yaml_template
        self.yaml_path = self.config.output_path
        self.yaml_file = self.config.spack_yaml

        # The 4 dictionaries to give to jinja. The whole
        # purpose of this class is to construct these dicts.
        self.pe_defs = {}
        self.pkgs_defs = {}
        self.pe_specs = {}
        self.pkgs_specs = {}

        #self.definitions_list = [] # WTF is this ? (defined in create_pkgs_definitions)


    def create_pe_defs(self, core = True):
        """Regroup PE definitions in a single dictionary"""

        # outputs dictionary with structure:
        #
        #   {
        #       'gcc_stable_compiler': 'gcc@11.3.0',
        #       'gcc_stable_mpi': 'openmpi@4.1.3 on infiniband',
        #       'gcc_stable_blas': 'openblas@0.3.20 threads=none +locking'
        #       ...
        #   }

        # use: group_sections, _flatten_dict

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        # group_sections return the 'pe' from the stack
        pe = self.group_sections(deepcopy(self.data), 'pe')

        # Hack for adding core_compiler definition
        if core:
            core_compiler = self.group_sections(deepcopy(self.data), 'core')
            for k, v in core_compiler.items():
                pe[k] = v

        # Filters logic for PE
        for _, stack in pe.items():
            for _, stack_env in stack.items():
                for filter in self.filters.keys():
                    if filter in stack_env and isinstance(stack_env[filter], dict):
                        stack_env[filter] = stack_env[filter][self.filters[filter]]

        self.pe_defs = self._flatten_dict(pe)

    def create_pkgs_defs(self):
        """Regroup package lists with their specs"""

        # create dictionary with structure:
        #
        #   {
        #       'list1': ['spec1', 'spec2^dep'],
        #       'list2': ['spec1@ver', 'spec2+var'],
        #       ...
        #   }

        # use: group_sections, _skip_list, _handle_package_dictionary

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        # TODO self.pkgs_stack is used in _skip_list but it should not be an instance attribute
        pkgs = self.group_sections(deepcopy(self.data), 'packages')
        for pkg_list_name, pkg_list_cfg in pkgs.items():

            tty.debug(f'Entering package list: {pkg_list_name}')

            # skip the list if `none` is found in filters
            if self._skip_list(pkg_list_name):
                continue

            # self.definitions_list.append(pkg_list_name) # ??????????????

            self.pkgs_defs[pkg_list_name] = []
            for pkg_list in pkg_list_cfg.get('packages'):
                package = None
                # This is the case where the package has no structure
                if isinstance(pkg_list, str):
                    package = [pkg_list]
                    tty.debug(f'Reading package: {package}')

                if isinstance(pkg_list, dict):
                    package = self._handle_package_dictionary(pkg_list)

                if package:
                    self.pkgs_defs[pkg_list_name].append(((' '.join(package)).strip()))

    def create_pe_specs(self):
        """Regroup PE libraries"""

        # create dictionary with structure:
        #
        #   {
        #       'gcc_stable': ['mpi', 'gpu'],
        #       'intel_stable': ['mpi', 'blas']
        #       ...
        #   }

        # use: group_sections

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        data = self.group_sections(deepcopy(self.data), 'pe')

        for pe, stack in data.items():
            for stack_name in stack.keys():
                self.pe_specs[pe + '_' + stack_name] = list(stack[stack_name].keys())
                # Remove compilers
                if 'compiler' in self.pe_specs[pe + '_' + stack_name]:
                    self.pe_specs[pe + '_' + stack_name].remove('compiler')
                if 'compiler_spec' in self.pe_specs[pe + '_' + stack_name]:
                    self.pe_specs[pe + '_' + stack_name].remove('compiler_spec')

    def create_pkgs_specs(self):
        """Regroup package list names and corresponding PE components."""

        # create dictionary with structure:
        #
        #   {
        #       'list1': {'compilers': ['gcc_stable', 'intel_stable']},
        #       'list2': {'compilers': ['gcc_stable', 'intel_stable'], 'dependencies': ['blas', 'gpu']},
        #       ...
        #   }

        # use: group_sections, _skip_list

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        pkgs = self.group_sections(deepcopy(self.data), 'packages')
        for pkg_list_name, pkg_list_cfg in pkgs.items():

            # skip the list if `none` is found in filters
            # What does this do ?
            if self._skip_list(pkg_list_name):
                continue

            # Create new entry
            self.pkgs_specs[pkg_list_name] = {}
            # Add compilers
            self.pkgs_specs[pkg_list_name]['compilers'] = pkg_list_cfg.get('pe')
            # Add dependencies
            if 'dependencies' in pkg_list_cfg.keys():
                # Add dependencies one by one and check against filters
                # if dependency is equals to the string "none" in which
                # case do not add the dependency. In the end, if the
                # dependencies list is empty, remove it.
                self.pkgs_specs[pkg_list_name]['dependencies'] = []
                for d in pkg_list_cfg['dependencies']:
                    if d in self.filters.keys() and self.filters[d] != 'none':
                        self.pkgs_specs[pkg_list_name]['dependencies'].append(d)
                    elif d not in self.filters.keys():
                        self.pkgs_specs[pkg_list_name]['dependencies'].append(d)
                if len(self.pkgs_specs[pkg_list_name]['dependencies']) == 0:
                    self.pkgs_specs[pkg_list_name].pop('dependencies')

    def _skip_list(self, pkg_list_name):
        """Returns true if the package list passed in argument is to skip

        This method searches for the presence of the 'filters' key in the
        package configuration section. If found, it will read each filter
        here defined and if at least one has the none property, this list
        is skipped.

        - what is the package configuration section ? Are we talking about
          the package list ? I don't recall to see filters in the configuration
          section of the list (child of list name);
        """

        pkg_list_cfg = self.group_sections(deepcopy(self.data), 'packages')[pkg_list_name]
        if 'filters' in pkg_list_cfg:
            for filter in pkg_list_cfg['filters']:
                if self.filters[filter] == 'none':
                    return True
        return False

    def _flatten_dict(self, d: MutableMapping, parent_key: str = '', sep: str = '_'):
        """Returns a flat dict

        Return a 1-depth dict (flat) whose elements are formed by composing
        the nested dicts nodes using the separator sep.
        {'a':1, 'b':{'c':2}} -> {'a':1, 'b_c':2}
        origin: freecodecamp.org"""

        return dict(self._flatten_dict_gen(d, parent_key, sep))

    def _flatten_dict_gen(self, d, parent_key, sep):

        for k, v in d.items():
            new_key = parent_key + sep + str(k) if parent_key else k
            if isinstance(v, MutableMapping):
                yield from self._flatten_dict(v, new_key, sep=sep).items()
            else:
                yield new_key, v
