from collections.abc import MutableMapping
import collections

from pdb import set_trace as st

s7 = {'root':
      {'a1': {'b1': 'str'},
       'a2': {'b1': ['list_elem_1'],
              'b2': [
                       {
                           'c1': {
                               'variants': {
                                   'common': 'schedulers=slurm',
                                   'mpi': {'infiniband': '+pmi', 'ethernet': 'fabrics=verbs'},
                                   'gpu': {'nvidia': '+cuda', 'none': '~cuda'}
                               },
                               'dependencies': ['hwloc ~libxml2']
                           },
                           'c2': {
                               'variants': {
                                   'common': 'schedulers=slurm',
                                   'gpu': {'nvidia': '+cuda', 'none': '~cuda'}
                               },
                               'dependencies': [
                                   'hwloc ~libxml2',
                                   {'gpu': {'nvidia': '+cuda', 'none': '~cuda'}}
                               ]
                           }
                       }
              ]
              }
       }
      }

class Iter:
    def __init__(self, data):
        self._data = data

    def __iter__(self):
        for k,v in self._data.items():
            if isinstance(v, MutableMapping):
                yield v

#    @staticmethod
#    def flatten(dictionary, parent_key='', separator='_'):
#        items = []
#        for key, value in dictionary.items():
#            new_key = parent_key + separator + key if parent_key else key
#            if isinstance(value, MutableMapping):
#                items.extend(Iter.flatten(value, new_key, separator=separator).items())
#            else:
#                items.append((new_key, value))
#        return dict(items)

    def count(self, dic):
        for k,v in self.dic.items():

            if isinstance(v, dict):
                self.keys(dic)

def flatten(dictionary, parent_key='', separator='_'):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)

def flattenl(dictionary, parent_key=False, separator='.'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, collections.abc.MutableMapping):
            items.extend(flattenl(value, new_key, separator).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                items.extend(flattenl({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)

def _flatten_dict_gen(d, parent_key, sep):
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            yield from flatten_dict(v, new_key, sep=sep).items()
        else:
            yield new_key, v

def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.'):
    return dict(_flatten_dict_gen(d, parent_key, sep))

def prin(msg=''):
    print(f'\n{msg}\n\n')

def my_iter():
    lst = 'abcdefhgijklmnopqrstuvwxyz'
    for i in lst:
        yield i

def count():
    num = 0
    while True:
        yield num
        num += 1

# <!> WORKS <!>
def simple(dic, key):
    for k,v in dic.items():
        if k == key:
            dic[k] = 'x'
        elif isinstance(v, MutableMapping):
            simple(v, key)

def _stack_gen(dic):
    for k,v in dic.items():
        if isinstance(v, MutableMapping):
            yield from _stack(v)

def _stack(dic):
    return _stack_gen(dic)

def _i(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            for keys in _i(v):
                yield [k] + keys
    else:
        yield []

data = {'a': {'b': {'c': [{'d': 1, 'e':2}, 1, {'g': 1, 'h': 2}, [{'i': {'j': 1}}]]}}}
#data = {'a': {'b': {'c': {'d': 1, 'e':2}, 'f': {'g': 1, 'h': 2}}, 'i': {'j': 1}}}

def gen(dic):
    for k,v in dic.items():
        if isinstance(v, dict):
            yield v
            gen(v)

st()
g = gen(data)
next(g)
next(g)
next(g)

st()


#prin(data)
#simple(data, 'i')
#prin()

