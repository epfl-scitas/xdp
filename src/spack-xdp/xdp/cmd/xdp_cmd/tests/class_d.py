from pdb import set_trace as st

class Dic:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        """called when >>> print(instance)
        see that this method must return a string"""
        print("in __str__")
        return f'{self.data}'

    def __repr__(self):
        """called when >>> instance
        also called in absence of __str__
        see that this method must return a string"""
        print("in __repr__")
        return f'{self.data}'

    def __call__(self):
        """called when >>> instance()"""
        print("in __call__")
        pass

some_dic = {'a':1, 'b':2}
a = Dic(some_dic)
print()

print('what happens when I type: a')
a.__repr__()
print()

print('what happens when I type: print(a)')
print(a)
print()

print('what happens when I type: a()')
a()
print()

print('test it yourself')
st()
