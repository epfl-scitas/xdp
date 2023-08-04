from collections.abc import MutableMapping
import copy
import inspect
import json
import jinja2
from jinja2 import Environment, FileSystemLoader
import os

import llnl.util.tty as tty
import llnl.util.filesystem as fs
import spack.config
import spack.util.spack_yaml as spyaml
import spack.environment as ev
from spack.util.executable import ProcessError, which

from pdb import set_trace as st

class FilterException(Exception):
    """Exception raised when filter evaluation fails"""
    def __init__(self, filter, filter_value):
        self.filter = filter
        self.filter_value = filter_value

class Stack:
    """Implements the Stack object

    Remarks:
    > A stack has one or more PE objects.
    > A stack has one or more PkgList objects.
    """

    # used in replace_tokens method and declared here for convenience
    LEFT_DELIM = "<"
    RIGHT_DELIM = ">"

    def __init__(self, config):
        """Declare class structs"""

        # Data attributes
        self.stack = self.read(config.stack_yaml)
        self.common = self.read(config.commons_yaml)
        self.platform = self.read(config.platform_yaml)

        # Replace tokens
        self.replace_tokens()

    def __str__(self):
        return json.dumps(self.stack, sort_keys=True, indent=4)

    def __repr__(self):
        return json.dumps(self.stack, sort_keys=True, indent=4)

    @property
    def pe(self) -> list:
        """Return list of `pe` objects"""

        return [ PE(k,v) for k,v in self.get_section('pe').items() ]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    #
    # INTERNAL METHODS
    #
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_section(self, section: str) -> dict:
        """Return `section` key from stack dictionary"""
        return self.group_sections(copy.deepcopy(self.stack), section)

    # There is no reason to have dic as parameter / this method is not general
    # enough to have dic as parameter. Must identify all methods calling this.
    def group_sections(self, dic: dict, section: str) -> dict:
        """Returns dictionary composed of common sections.

        stack.yaml may contain different keys that identify a PE entry or
        a PackageList entry. This method reads the metadata attribute of
        the key and returns the requested section."""

        tmp = {}
        for k, v in dic.items():
            if 'metadata' not in v:
                print(f'group_sections: metadata key not found')
            if v['metadata']['section'] == section:
                tmp[k] = copy.copy(v)
                tmp[k].pop('metadata')
        return tmp

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    #
    # NEW METHODS
    #
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def read(self, filename: str, **kwargs) -> dict:
        """Return data from yaml file"""

        with open(filename) as f:
            return spyaml.load_config(f, **kwargs)

    # TO DELETE
    def get_pe(self) -> dict:
        """Return `pe` key from stack dictionary"""
        return self.group_sections(copy.deepcopy(self.stack), 'pe')

    def pkgs(self) -> dict:
        """Return `packages` key from stack dictionary"""
        return self.get_section('packages')


    def tokens(self) -> dict:
        """Return token keys from platform dictionary"""
        return self.platform['platform']['tokens']

    def platform_odities(self) -> dict:
        """Return odities defined for platform"""
        return self.platform['platform']['filters']

    def filters(self) -> dict:
        """Return filter keys from platform dictionary"""
        return self.platform['platform']['filters']

    def replace_tokens(self) -> None:
        """Read tokens from platform file and call replacement procedure.
        Repacement is done in-place directly over self.stack dictionary"""

        for key, value in self.tokens().items():
            self._do_replace_tokens(self.stack, self.LEFT_DELIM + str(key) +
                                    self.RIGHT_DELIM, str(value))

    def _do_replace_tokens(self, d: dict, pat: str, rep: str) -> None:
        """
        Replace pattern `pat` found in dictionary `d` with replacement `rep` (in place).

        If pat = 'll' and rep = '11':

          {'william': 'tell'} > {'william': 'te11'}
          - replacement occurs only in the key value, not in the key itself.
            That is why `william` remains `william`.

          {'leonhard': 'euler'} > {'leonhard': 'euler}
          - no replacement, pat is composed of two lls.

          {'the gang': ['tell', 'euler']} > {'the gang': ['te11', 'euler']}
          - replacement occurs also inside list members."""

        if isinstance(d, dict):
            for k in d:
                if isinstance(d[k], str):
                    d[k] = d[k].replace(pat, rep)
                else:
                    self._do_replace_tokens(d[k], pat, rep)
        if isinstance(d, list):
            for idx, elem in enumerate(d):
                if isinstance(elem, str):
                    d[idx] = elem.replace(pat, rep)
                else:
                    self._do_replace_tokens(d[idx], pat, rep)

    def spec(self, pkg: dict) -> str:
        """Return spec from dict.

        This method accepts a package declaration passed as a dictionary
        and returns the implicit spec."""

        pass


#    def apply_filters(self, debug = False) -> dict:
#        """Returns PE with filters applied"""
#
#        pe = self.get_pe()
#        for _, stack in pe.items():
#            for _, stack_env in stack.items():
#                for fltr in self.filters().keys():
#                    if fltr in stack_env and isinstance(stack_env[fltr], dict):
#                        # write in place
#                        stack_env[fltr] = stack_env[fltr][self.filters()[fltr]]
#
#        # optional return value since pe is a shallow copy
#        if debug:
#            print(pe)
#        return pe

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    #
    # METHODS FROM `ReadYaml` CLASS
    #
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def do_choose(self, stack, dic, token):
        """Replace token keys in dictionary

        Example:

        Suppose the following key is found in stack:

            gpu: { nvidia: cuda, amd: rocm }

        then, if token = {gpu: nvidia} the 'key' in the stack will no longer be
        a dictionary and it will be {'gpu': 'cuda'}.

        CAVEATS: although this function works, it needs major revision. This
        function does not work if more complicated nested dictionaries are used."""

        for k, v in dic.items():
            if (isinstance(v, dict)
                and k in token.keys()):
                self._update(stack, self._dic_from_list({}, self._cursor + [k] +
                                                        [v[token[k]]], True))
            elif isinstance(v, dict):
                self._cursor.append(k)
                self.do_choose(stack, v, token)
                self._cursor.pop(-1)

            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        self._cursor.append(k)
                        self.do_choose(stack, item, token)
                        self._cursor.pop(-1)


    def read_choices(self, platform_file):
        """Return dict of keys to be replaced in stack file

        Replacements are found under the common:filter key:

            common:
              filters:
                key1: option1
                key2: option2
                ...

        This method will return a dict like this:

            {key1: option1, key2, option2, ...}
        """

        if not os.path.exists(platform_file):
            return {}

        common = ReadYaml()
        common.read(platform_file)
        return(common.data['common']['filters'])

    def read_replacements(self, platform_file):
        """Return dict of keys to be replaced in stack file

        Replacements are found under the common:variables key:

            common:
              variables:
                key1: option1
                key2: option2
                ...

        This method will return a dict like this:

            {key1: option1, key2, option2, ...}
        """

        if not os.path.exists(platform_file):
            return {}

        common = ReadYaml()
        common.read(platform_file)

        return(common.data['common']['variables'])

    def do_replace(self, d, pat, rep):
        """Attempt to replace stuff in YAML file

        d - yaml file in form of python dicy.
        pat - pattern to look for, par exemple: '<<id>>'.
        rep - replacement string, par exemple: 'xy: z')."""

        if isinstance(d, dict):
            for k in d:
                if isinstance(d[k], str):
                    d[k] = d[k].replace(pat, rep)
                else:
                    self.do_replace(d[k], pat, rep)
        if isinstance(d, list):
            for idx, elem in enumerate(d):
                if isinstance(elem, str):
                    d[idx] = elem.replace(pat, rep)
                else:
                    self.do_replace(d[idx], pat, rep)

    def _update(self, d, u):
        """Update nested dictionary (d) with given dictionary (u)"""

        # update(stack, {'intel': {'stable': {'gpu': 'edu'}}})
        # self.stack.get('core_pkgs').get('packages')
        tmp = {'core_pkgs': {'packages': {'cmake@3.9.18': {'gpu': '+cuda cuda_arch=cuda_arch'}}}}
        if u == tmp:
            pass
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                if isinstance(d.get(k, {}), collections.abc.Mapping):
                    d[k] = self._update(d.get(k, {}), v)
                if isinstance(d.get(k, {}), list):
                    d[k] = self._update(d.get(k, {})[0], v)
            else:
                d[k] = v
        return d


    def _dic_from_list(self, d, keylist, lastvalue=False):
        """Return nested dictionary whose keys are given by cursor

        Examples:

          dic_from_list({}, ['a', 'b', 'c'], lastvalue=False)
              -> {'a': {'b': {'c'}}}

          dic_from_list({}, ['a', 'b', 'c'], lastvalue=True)
              -> {'a': {'b': 'c'}}"""

        if lastvalue:
            v = keylist.pop(-1)
            lastvalue=False
            return(self._dic_from_list({ keylist.pop(-1) : v }, keylist))
        while keylist:
            return(self._dic_from_list({ keylist.pop(-1) : d }, keylist))
        return(d)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    #
    # METHODS FROM `Stack` CLASS
    #
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def _write_yaml(self, output, filename):
        with fs.write_tmp_and_move(os.path.realpath(filename)) as f:
            yaml = syaml.load_config(output)
            if self.schema:
                spack.config.validate(yaml, self.schema, filename)
            syaml.dump_config(yaml, f, default_flow_style=False)

    def write_yaml(self, **kwargs):
        """Write yaml file"""

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        # Jinja setup
        file_loader = FileSystemLoader(self.templates_path)
        jinja_env = Environment(loader = file_loader, trim_blocks = True)

        # Check that template file exists in given path
        path = os.path.join(self.templates_path, self.template_file)
        if not os.path.exists(path):
            tty.die(f'Template file {self.template_file} does not exist ',
                    f'in {self.templates_path}')

        # Render and write self.yaml_file
        jinja_template = jinja_env.get_template(self.template_file)
        output = jinja_template.render(data=kwargs['data'], tokens=self.tokens)

        tty.msg(self.yaml_file)
        print(output)

        env = ev.active_environment()
        if env:
            filename = os.path.join(
                os.path.dirname(os.path.realpath(env.manifest_path)),
                self.yaml_file)
            self._write_yaml(output, filename)
        else:
            filename = os.path.join(self.yaml_path, self.yaml_file)
            tty.msg(f'Writing file {filename}')
            self._write_yaml(output, filename)

 
    # CODE BEYOND THIS POINT IS USED ONLY
    # FOR MANIPULATING PACKAGES SECTION

    def _remove_newline(self, values):
        return ' '.join((values.strip().split('\n')))

    def _filters_in_package(self, dic):
        """Return list of filters found in dictionary"""

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')
        result = []
        for filter in self.filters.keys():
            if filter in dic:
                result.append(filter)
        return(result)

    def _handle_filter(self, attributes):
        result = []
        if isinstance(attributes, dict):
            # Check for filters presence
            for filter in self.filters.keys():
                if filter in attributes:
                    if self.filters[filter] in attributes[filter]:
                        values = attributes[filter][self.filters[filter]]
                        if isinstance(values, list):
                            result.extend(values)
                        else:
                            result.append(values)
                    else:
                        raise FilterException(filter, self.filters[filter])
        else: # We are just checking that attributes is not a structure (dict, list, etc)
            # We need to cast version to str because of ' '.join in next step
            result.append(str(attributes))
        return result

    def _handle_package_dictionary(self, pkg: dict):
        """Returns one line spec based on package attributes

        This method is responsible for processing the attributes
        included in the package dictionary writen in the stack file.
        The dictionary structure is like:

          pkg:
            default: <...>
            version: <...>
            variants: <...>
            dependencies:
              - <...>
            filters:
              filter_1: <...>
            externals: <...>

        This method returns all the information above concatenated in
        a single line according to what spack is expecting.
        """

        # ONLY USED IN PKG DEFS

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')

        # It would be cool to have a feature to enable to enter in trace mode
        # for a given package:
        #
        # if pkg == DEBUG_PKG:
        #     st()

        if len(pkg.keys()) > 1:
            print(f'Package with bad specification {pkg}')
            raise KeyError()

        pkg_name = list(pkg.keys())[0]
        pkg_attributes = pkg[pkg_name]

        if pkg_name == 'package12':
            st()

        try:
            package = [pkg_name]
            tty.debug(f'Reading package: {package}')

            # filters
            for filter in self._filters_in_package(pkg_attributes):
                package.append(pkg_attributes[filter][self.filters[filter]])

            # remaining package attributes
            for attr in ['version', 'variants', 'dependencies']:
                if attr in pkg_attributes:
                    _spack_pkg = getattr(Stack, '_spack_pkg_' + attr)
                    package.append(_spack_pkg(self, pkg_attributes[attr]))

            return package

        except FilterException as fe:
            tty.debug(f'Ignoring package {pkg_name} in `spack.yaml` due to'
                      f'missing value for {fe.filter_value} in filter {fe.filter}')
            return None

    def _spack_pkg_version(self, version_attributes):
        """Returns package version"""

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')
        version = self._handle_filter(version_attributes)
        return(self._remove_newline(' '.join(version)))

    def _spack_pkg_variants(self, variants_attributes):
        """Returns package variants"""

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')
        variants = []
        if 'common' in variants_attributes:
            variants.append(variants_attributes.get('common'))
        variants.extend(self._handle_filter(variants_attributes))

        return(self._remove_newline(' '.join(variants)))

    def _spack_pkg_dependencies(self, dependencies_attributes):
        """Returns package dependencies"""

        tty.debug(f'Entering function: {inspect.stack()[0][3]}')
        dependencies = []
        # We are just checking that version_attributes is not a structure (dict, list, etc)
        if isinstance(dependencies_attributes, list):
            dependencies = dependencies_attributes
        else:
            dependencies = self._handle_filter(dependencies_attributes)

        return(self._remove_newline(' ^' + ' ^'.join(dependencies)))


# This does no work like this because it will ask for the config parameter
# which __init__ from Stack class is expecting.
class PackageList:

    def __init__(self, pkglist: dict):
        self.pkglist = pkglist

    def __str__(self):
        return json.dumps(self.pkglist, sort_keys=True, indent=4)

    def __call__(self):
        return json.dumps(self.pkglist, sort_keys=True, indent=4)

    def definitions(self) -> dict:
        """Returns package lists definitions"""

        # expected output:
        #
        #   {
        #       'list1': ['spec1', 'spec2^dep'],
        #       'list2': ['spec1@ver', 'spec2+var'],
        #       ...
        #   }

        dic = {}
        for lst in self.pkglist:
            dic[lst] = []
            for pkg in lst:
                dic[lst].append(pkg.spec())


    def specs(self) -> dict:
        """Returns package lists specs"""

        # expected output:
        #
        #   {
        #       'list1': {'compilers': ['gcc_stable', 'intel_stable']},
        #       'list2': {'compilers': ['gcc_stable', 'intel_stable'], 'dependencies': ['blas', 'gpu']},
        #       ...
        #   }

        pass

    def __str__(self):
        return json.dumps(self.definitions(), sort_keys=True, indent=4)


# Does this really makes sense ?
class Default:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def __repr__(self):
        return f'{self.data}'

    def version(self):
        """Return package version"""
        pass

    def variants(self):
        """Return package variants"""
        pass

    def dependencies(self):
        """Return package version"""
        pass

    def odities(self):
        """Return package version"""
        pass

class Package:

    def __init__(self, data):
        #st()
        #print('init method Package class')
        #if isinstance(data, str):
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def __repr__(self):
        return f'{self.data}'

    @property
    def spec(self) -> str:
        """Return package spec"""

        if isinstance(self.data, str):
            result = self.data

        if isinstance(self.data, list):
            for pkg in self.data:

            result = self.data

    # --------------------------------------------------------------------------

    def externals(self):
        """Return package version"""
        pass

    def default(self):
        """Return package version"""
        pass

    def autoload(self):
        """Return True if package contains the autoload flag"""
        pass

    def blacklist(self):
        """Return True if package contains the blacklist flag"""
        pass

    def activated(self):
        """Return True if package contains the activated flag"""
        pass

# ### <REGARDE VOIR> ###
#
# SE TIVERMOS UMA LISTA DE OBJECTOS PACKAGE, PODEMOS DEPOIS
# APLICAR A FUNÇÃO MAP E OBTER ASSIM A LISTA DE SPECS.

class Definition:
    # A Definition can be a string (compiler: gcc@11.3.0),
    # a list of strings (mpi: [openmpi@4.1.0, mvapich@2.3.7]),
    # a list of dicts or even a list of mixed elements.

    def __init__(self, name, data):
        self.data = self.make_package(data)
        self.name = name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

    def make_package(self):
        if isinstance(self.data, str):
            result = self.data

        if isinstance(self.data, dict):
            result = self.data

        if isinstance(self.data, list):
            for pkg in self.data:

    def specs(self) -> list:
        """Return list of specs/strings contained in definition
        after having resolved complex packages"""
        # each spec is a string as it is expected by spack.yaml
        pass

class Release:

    def __init__(self, name, data):
        self.data = data
        self.name = name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

    @property
    def definitions(self) -> list:
        """Return list of Definition objects"""
        return [ Definition(defi,libr) for defi,libr in self.data.items() ]

    # --------------------------------------------------------------------------

    @property
    def compiler(self) -> str:
        """Return compiler for release"""
        return self.data['compiler']

    @property
    def python(self):
        """Return python for release"""
        return self._library('python')

    @property
    def blas(self):
        """Return blas for release"""
        return self._library('blas')

    @property
    def mpi(self):
        """Return mpi for release"""
        return self._library('mpi')

    @property
    def gpu(self):
        """Return gpu for release"""
        return self._library('gpu')

    def _library(self, library):
        # if library is a dict, then it is an odty
        try:
            if isinstance(self.data[library], str):
                return self.data[library]
            else:
                return self._odity(self.data[library])
        except:
            pass

    def _odity(self, pkg_odt: dict) -> str:
        """Returns the package variants for the platform odities.

               pkg_odt : {'nvidia': '+cuda', 'amd': 'roce'}
              plat_odt : {'mpi': 'infiniband', 'gpu': 'nvidia'}
          return value : '+cuda'
        """
        return ''.join(pkg_odt.get(odt) for odt in self.plat_odts.values() if odt in pkg_odt)

    def _library_simple(self, library):
        try:
            return self.data[library]
        except:
            print(f'{release} has no {library} library')
            return 1

    @property
    def libraries(self) -> list:
        pass

class PE:
    """Return PE object"""
    def __init__(self, name, data):
        self.data = data
        self.name = name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

    @property
    def releases(self) -> list:
        """Return list of Release objects"""
        return [ Release(rels,defs) for rels,defs in self.data.items() ]

    # --------------------------------------------------------------------------

    @property
    def list(self) -> dict:
        """Return `pe` object"""

        # This is returning a list of strings.
        # Would be nicer to return list of objects.
        return list(self.data.keys())

    @property
    def stable(self) -> dict:
        """Return stable dict"""
        return self._release('stable')

    @property
    def future(self) -> dict:
        """Return future dict"""
        return self._release('future')

    @property
    def deprecated(self) -> dict:
        """Return deprecated dict"""
        return self._release('deprecated')

    def _release(self, release):
        try:
            return Release(self.data[self.name][release])
        except:
            print(f'{self.name} has no {release} release')
            return None
