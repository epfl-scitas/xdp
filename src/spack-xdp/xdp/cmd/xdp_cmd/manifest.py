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
from collections.abc import MutableMapping
import json
import inspect

import llnl.util.tty as tty
import spack.schema

from .stack_file import Stack, FilterException
from .util import *


class Manifest(Stack):
    """Create usefull data structures to pass to the jinja template"""

    # [ TODO ]
    #
    # THIS CLASS IS IN FACT UnNECESSARY

    # def __init__(self, config):
    #     """Declare class structs"""
    #
    #     super().__init__(config)
    #
    #     # These variables will be used in StackFile class.
    #     # Each command that write an Yaml file must define these 4 variables.
    #     # This technique allows for individual command customization of each
    #     # one of these parameters and at the same time to reuse the functions
    #     # all gathered in a single module.
    #     self.templates_path = self.config.templates_path
    #     self.template_file = self.config.spack_yaml_template
    #     self.yaml_path = self.config.output_path
    #     self.yaml_file = self.config.spack_yaml
    #
    #     # The 4 dictionaries to give to jinja. The whole
    #     # purpose of this class is to construct these dicts.
    #     self.pe_defs = {}
    #     self.pkgs_defs = {}
    #     self.pe_specs = {}
    #     self.pkgs_specs = {}


    def pe_defs(self, core = True):
        """Regroup PE definitions in a single dictionary"""

        # outputs dictionary with structure:
        #
        #   {
        #       'gcc_stable_compiler': 'gcc@11.3.0',
        #       'gcc_stable_mpi': 'openmpi@4.1.3 on infiniband',
        #       'gcc_stable_blas': 'openblas@0.3.20 threads=none +locking'
        #       ...
        #   }

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        print(self)

        st()
        # _flatten_dict should go into PE class since it is a PE method
        # in the sense that it is only used for PE objects..
        return self._flatten_dict(self.apply_filters())


    def pkgs_defs(self):
        """Regroup package lists with their specs"""

        # create dictionary with structure:
        #
        #   {
        #       'list1': ['spec1', 'spec2^dep'],
        #       'list2': ['spec1@ver', 'spec2+var'],
        #       ...
        #   }

        # [ TODO ]
        #
        # 1. replace tokens     : PE()
        # 2. set filters        : PE()
        # 3. process stack      : Here
        # 4. output structure   : Here

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        print(self)

        # _flatten_dict should go into PE class since it is a PE method
        # in the sense that it is only used for PE objects..
        return self._flatten_dict(self.apply_filters())

    def create_pe_specs(self):
        """Regroup PE libraries"""

        # create dictionary with structure:
        #
        #   {
        #       'gcc_stable': ['mpi', 'gpu'],
        #       'intel_stable': ['mpi', 'blas']
        #       ...
        #   }

        # [ TODO ]
        #
        # 1. replace tokens     : PE()
        # 2. set filters        : PE()
        # 3. process stack      : Here
        # 4. output structure   : Here

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')


    def create_pkgs_specs(self):
        """Regroup package list names and corresponding PE components."""

        # create dictionary with structure:
        #
        #   {
        #       'list1': {'compilers': ['gcc_stable', 'intel_stable']},
        #       'list2': {'compilers': ['gcc_stable', 'intel_stable'], 'dependencies': ['blas', 'gpu']},
        #       ...
        #   }

        # [ TODO ]
        #
        # 1. replace tokens     : PE()
        # 2. set filters        : PE()
        # 3. process stack      : Here
        # 4. output structure   : Here

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')


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

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

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
        origin: freecodecamp"""

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        return dict(self._flatten_dict_gen(d, parent_key, sep))

    def _flatten_dict_gen(self, d, parent_key, sep):

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        for k, v in d.items():
            new_key = parent_key + sep + str(k) if parent_key else k
            if isinstance(v, MutableMapping):
                yield from self._flatten_dict(v, new_key, sep=sep).items()
            else:
                yield new_key, v
