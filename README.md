# xdp

eXtended Deploy - define and deploy a software stack over different architectures using Spack

## general overview

The goal of xdp is to install a software stack (defined in the stack file) on a given
platform (defined in the platform file). This is acheived by designing a stack file
general enough to support different architectures between hardware platforms.

This is acheived through the use of filters and tokens which are two methods used
by xdp to read data from the platform file and write the `spack.yaml` file that spack
is waiting for to install the stack.

Using the filtering mechanism xdp can read the fabrics interconnect declared in the
platform file and `chose` the corresponding set of variants in the stack file when
installing the MPI library.

Using the tokens mechanism xdp can read in the platform file the compiler provided by
the platform OS and then `replace` it in the stack file where needed.

## the stack file

This is the main file where the packages to be installed are listed. Everything is done
using YAML syntax. This file will also contain a section to declare the compiler to use
as well as other notable libraries such as a linear algebra library, GPU driver, python
version, etc - this section is called the programming environment (PE).

This file contains three types of root keys:
+ a key to declare the system compiler
+ keys for declaring the PEs (more than one are allowed)
+ keys to declare the package lists (more than one are allowed)

```yaml
core:
  ...
pe:
  ...
pkg_list:
  ...
```
### the core key
This key is used to declare the core compiler. The syntax of the block is the following:
```yaml
core:
  metadata:
    section: core
  compiler: gcc@13.1.0
```
For the moment this key has no other functionality, but we do need to declare the core
compiler because we will need it to compile other software. In future this information
could be placed in a different location, as it does not add something new (the compiler
is already installed) and it could be classified as information related to the computing
platform. We will see later that we have a special place for the platform.

+ This key can be named anything, but it is convinient to call it by the name of the
functionality it provides: `core` (>>>TO CONFIRM<<<).
+ The section key must contain the value `core` (mandatory)

### the PE key
The PE key is used to declare a programming environment. The PE is used to declare the
compiler as well as other notable libraries upon which the packages to be installed will
depend, like the linear algebra library, the MPI library, etc.

```yaml
gcc:
  metadata:
    section: pe
  stable:
    compiler: gcc@11.3.0
    mpi: openmpi@4.1.3 fabrics=ucx +pmi
```
`gcc` is the name of the stack. This name is arbitrary. This key contains the metadata
value which is used internally to declare that the `gcc` entry refers to a PE. For this, 
we add the value `pe` to the `section` key. This is how xdp knows that the `gcc` key
contains information about a PE.

Next we find a key named `stable`. The name of this key is arbitrary and is used to
declare several stacks under the same common name `gcc`. An example of a use case for
this feature is to provide a `stable` release and a `future` release.

The `stable` keyword contains the compiler and libraries that we will want to enforce
as dependencies on the packages to be installed. In the example above, we define a
compiler and an mpi library.

The names `compiler` and `mpi` are arbitrary, but it makes sense to use them.
We can declare more than one PE. For this, we would just add another key, for example
`intel` having the same subkeys and appropriate values.

### the package list key
The package list key is used to declare the set of packages to be installed.

```yaml
physics_lab:
  metadata:
    section: packages
  pe:
  - gcc_stable
  packages:
  - hdf5~mpi
  - netcdf-fortran
  - fftw+openmp~mpi
```
Like the previous keys, the package list key also contains the metadata key. In this
case, the `section` key contains the value `packages` and, as before, is used internaly
by xdp to identify the key as a package list.

The package list key has two new keys: `pe` and `pacakges` (the names are mandatory).

The `pe` key is a list and it contains the PE used to build the packages.

The packages key is also a list and contains the packages to build.





## package list advanced concepts
### setting package preferences
We can flag a package if we want spack to use this set of variants when bulding the package
as a dependency for other pacakges. In the following example, the `defaut` keyword is added
meaning that xdp should add this package to spack `packages.yaml` configuration file.

```yaml
- zlib:
    default:
      variants: ~optimize
```
In the preceeding example, xdp will add the spec `zlib` to the manifest file but in
packages.yaml the spec will be `zlib~optimize`. If we want to add a variant to the
spec being written to the manifest file, then we must add the key variants under the
spec like in the following example:
```yaml
- zlib:
    variants:
    default:
      variants: 
```
    
## glossary

manifest - spack.yaml file
