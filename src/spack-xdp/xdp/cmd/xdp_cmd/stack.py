from collections.abc import MutableMapping
import copy
import json
import jinja2
import os

import llnl.util.filesystem as fs
import llnl.util.tty as tty
import spack.config
import spack.environment as ev
import spack.util.spack_yaml as spyaml

import spack.extensions.xdp.cmd.xdp_cmd.xdp_config as xdp_config

from pdb import set_trace as st

class Value:
    def __init__(self, v):
        self.v = v

class Stack:
    """Implements the Stack object"""

    # used in replace_tokens method / defined here for convenience
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

        # Resolve odities
        for k, val in self._iterator(self.stack):
            if self._is_var_odity(k, val.v):
                val.v = self._resolve_odt(k, val.v)
            elif self._is_dep_odity(k, val.v):
                val.v = self._resolve_odt(k, val.v)

    def __str__(self):
        return json.dumps(self.stack, sort_keys=True, indent=4)

    def __repr__(self):
        return json.dumps(self.stack, sort_keys=True, indent=4)

    # Odities related methods
    # ..........................................................................

    def _iterator(self, o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k, (val := Value(v))
                o[k] = val.v
                yield from self._iterator(v)
        if isinstance(o, list):
            for v in o:
                yield from self._iterator(v)

    def _is_var_odity(self, key, value):
        """Return true if key is an odity defined in the platform file
        and value is a dictionary having at most n keys, all of them
        being strings."""

        found = True
        # the key is declared as an odity in platform file -->
        if not key in self.odities:
            found = False
        # --> this key is a dictionary -->
        if found and not isinstance(value, MutableMapping):
            found = False
        # --> and its keys are strings.
        if found:
            for k,v in value.items():
                if not isinstance(v, str):
                    found = False
        return found

    def _is_dep_odity(self, key, value):
        """Return true if key is an odity defined in the platform file
        and value is a dictionary having at most n keys, all of them
        being lists of strings."""

        found = True
        if not key in self.odities:
            found = False
        if found and not isinstance(value, MutableMapping):
            found = False
        if found:
            for k,v in value.items():
                if not isinstance(v, list):
                    found = False
                # each element in list is a string
                if found:
                    for item in v:
                        if not isinstance(item, str):
                            found = False
        return found

    def _resolve_odt(self, odt: str, choices: dict) -> str:
        """Returns the string spec for odt in choices"""
        return choices[self.odities[odt]]

    # Token related methods
    # ..........................................................................

    def replace_tokens(self) -> None:
        """Read tokens from platform file and call replacement procedure.
        Repacement is done in-place directly over self.stack dictionary"""

        for key, value in self.tokens.items():
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

    # Stack methods
    # ..........................................................................

    @property
    def pe(self) -> list:
        """Return list of `pe` objects"""

        return [ PE(k,v) for k,v in self._get_section('pe').items() ]

    @property
    def odities(self) -> list:
        """Return list of odities"""
        return self.platform_fetch('filters')

    @property
    def tokens(self) -> dict:
        """Return token keys from platform dictionary"""
        return self.platform_fetch('tokens')

    def platform_fetch(self, attr):
        """Fetch generic information from platform dictionary"""
        return self.platform['platform'][attr]

    # Grouping YAML sections together
    # ..........................................................................

    def _get_section(self, section: str) -> dict:
        """Return `section` key from stack dictionary"""
        return self._group_sections(copy.deepcopy(self.stack), section)

    def _group_sections(self, dic: dict, section: str) -> dict:
        """Returns dictionary composed of common sections.

        stack.yaml may contain different keys that identify a PE entry or
        a PackageList entry. This method reads the metadata attribute of
        the key and returns the requested section."""

        tmp = {}
        for k, v in dic.items():
            if 'metadata' not in v:
                print(f'_group_sections: metadata key not found')
            if v['metadata']['section'] == section:
                tmp[k] = copy.copy(v)
                tmp[k].pop('metadata')
        return tmp

    # File methods
    # ..........................................................................

    def read(self, filename: str, **kwargs) -> dict:
        """Return data from yaml file"""
        with open(filename) as f:
            return spyaml.load_config(f, **kwargs)

    def _write_yaml(self, output, filename):
        with fs.write_tmp_and_move(os.path.realpath(filename)) as f:
            yaml = syaml.load_config(output)
            if self.schema:
                spack.config.validate(yaml, self.schema, filename)
            syaml.dump_config(yaml, f, default_flow_style=False)

    def write_yaml(self, **kwargs):
        """Write yaml file"""

        # Jinja setup
        file_loader = jinja2.FileSystemLoader(self.templates_path)
        jinja_env = jinja2.Environment(loader = file_loader, trim_blocks = True)

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

class PackageList:
    # This class is a Definition object which has two more attributes:
    # - pe
    # - dependencies
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

class Package:
    # caveats: when a package is defined using a dictionary it must then
    # have a single key which should be the package name and this key
    # must be a dictionary describing the package.

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def __repr__(self):
        return f'{self.data}'

    @property
    def spec(self) -> str:
        """Return package specs"""

        if isinstance(self.data, str):
            return self.data
        else:
            return self._spec_from_dict()

    def _spec_from_dict(self):
        """Return specs from dictionary"""

        return (
            self._name + ' ' +
            self._version + ' ' +
            self._variants
        )

    @property
    def _name(self) -> str:
        """Return package name"""
        return ''.join(self.data)

    @property
    def _version(self) -> str:
        """Return version value"""
        try:
            return self._pkg_attr('version')
        except:
            print(f'package {self._name} does not have version attribute')
            return ''

    @property
    def _variants(self) -> str:
        """Return package variants, including odities"""
        # variants can be a string or a dictionary. if dictionary, then it may
        # contain the `common` keyword and all other keywords are odities. At
        # this point all odities have been resolved and any keys of attribute
        # variants must all be strings.
        try:
            variants = []
            if isinstance(self._pkg_attr('variants'), str):
                variants.append(self._pkg_attr('variants'))
            elif isinstance(self._pkg_attr('variants'), MutableMapping):
                for v in self._pkg_attr('variants').values():
                    variants.append(v)
            return ' '.join(variants)
        except:
            print(f'error processing variants for package {self._name}')
            return ''

    def _pkg_attrs_gen(self) -> dict:
        """Return all package attirbutes"""
        return self.data[self._name]

    def _pkg_attr(self, attr):
        """Return specific package attirbute"""
        return self.data[self._name][attr]

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

class Definition:
    # A Definition can be
    # > a string (compiler: gcc@11.3.0),
    # > a list of strings (mpi: [openmpi@4.1.0, mvapich@2.3.7]),
    # > a list of dicts,
    # > a list of dict and strings.
    # A Definition must either be a string or a list.
    # A Definition cannot be a dictionary not enclosed in a list.

    def __init__(self, name, data):
        self.data = data
        self.name = name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

    @property
    def pkgs(self) -> list:
        """Return list of package objects"""

        return [ Package(pkg) for pkg in self.data ]

    @property
    def specs(self) -> list:
        """Return list of specs/strings contained in definition
        after having resolved complex packages"""

        return [ pkg.spec for pkg in self.pkgs ]

class Release:
    """A Release is a list of Definition objects.
    This list is created via the definitions method."""

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

class PE:
    """A PE (programming environment) is a list of Release objects.
    This list is created via the releases method."""

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
