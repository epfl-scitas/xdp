import yaml
from pdb import set_trace as st
data = """
- gcc@11.3.0
- openmpi:
    version: 4.1.3
"""

class PackageString:
    def version(self):
        return self.data[4:]

class PackageDict:
    def version(self):
        inner_dic = self.data[list(self.data.keys())[0]]
        return inner_dic['version']

class Package:
    def __init__(self, data):
        self.data = data

data = yaml.safe_load(data)

lst = []
for pkg in data:
    Package(pkg).version
