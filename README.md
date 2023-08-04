# xdp

eXtended Deploy - define and deploy a software stack over different architectures using Spack

## general overview

The goal of xdp is to install a software stack (defined by the stack file) on a given
platform (defined by the platform file). The design enables xdp to install the same
software stack over different hardware architectures.

This generality is acheived through the use of `filters` and `tokens` which are two
concepts used by xdp to read data from the platform file and write the manifest
that spack is waiting for to install the stack.

Using the filtering mechanism xdp can read the fabrics interconnect declared in the
platform file and `chose` the corresponding set of variants in the stack file when
installing the MPI library.

Using the tokens mechanism xdp can read in the platform file for the compiler provided
by the platform OS and then `replace` it in the stack file where needed.

Using this technique xdp can install the same software stack in platforms having
different specifications and arhitectures provided their differences have previously
been identified in the platform file. Each system should provide it's own platform file.

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
[NICE TO HAVE]
+ If there is no PE in the stack file, then xdp should automatically create the definition
for the core compiler and use it in the matrix definitions. Right now it seems that we
are kind of forcing the `core` key which can easely be done in the background and provide
a cleaner stack file, with less stuff to dictract users attention.
+ The metada key for the `core` key is not needed since we are already forcing
the key to be named core (are we ?).
### the package list key
The package list key is used to declare the set of packages to be installed.

```yaml
physics_lab:
  metadata:
    section: packages
  pe:
  - core
  packages:
  - zlib
```
The key for the package list can be any name except `core` because it is already
being used. In the example above, the key is `physics_lab` which can help to
identify the origin of the packages.
Like for the `core` key, the package list key also contains the metadata key. In
this case, the `section` key contains the value `packages` and, as before, is used
internaly to tell xdp the that this key contains a list of packages.
The package list key has two new child keys: `pe` and `pacakges` (the use of these
names is mandatory).
The `pe` key is a list and it contains the PE used to build the packages. For the
moment we have only talked about the `core` PE, so the this key will only contain
this value.
The `packages` key is also a list and contains the packages to build. In the example,
we see that the physics lab are still at a basic level, they only use zlib!
[NICE-TO-HAVE]
+ Having only a single PE, it makes no sense to force the user to type it. In this case,
`xdp` should be able to guess the PE and the pe key would become obsolete.
+ It would be cool to use jsonchema validation or another method so that we could guess
the kind of key we are reading and not have to add metadata as a child and polute
the stack file and make the file harder to read for the user.
### minimal stack file
What we have seen so far allow us to write a stack file contaning enough information
to execute the first xdp commands.
```yaml
core:
  metadata:
    section: core
  compiler: gcc@13.1.0
physics_lab:
  metadata:
    section: packages
  pe:
  - core
  packages:
  - zlib
```
## the platform file
The platform file gathers a bunch of definitions allowing the user to customize
the sets of variants to apply when requesting the installation of a package (filters)
and to use information specific to the platform through out the stack file (tokens).
These two mechanisms are what makes it possible to use the same stack across different
hardware systems.
```yaml
platform:
  filters:
    gpu: none
    fabrics: ethernet
  tokens:
    core_compiler: gcc@11.3.0
    target: icelake
```
In the previous example we see how filters and tokens can be declared in the
platform file. Later on we will see how they apply in the stack file.
## putting it all together
### the PE key
The core compiler does a good job, but for software that can leverage the power
of the latest features present in high end CPUs, a modern compiler would be a
nice thing to add to the stack.
The PE key is used to declare a programming environment. The PE defines a
compiler as well as other notable libraries upon which the packages to be
installed will depend, like the linear algebra library or the MPI library, to
name a few. Here is a simple schema for declaring a PE defning only a compiler
and an MPI library.
```yaml
gcc:
  metadata:
    section: pe
  stable:
    compiler: gcc@11.3.0
    mpi: openmpi@4.1.3 fabrics=ucx +pmi
```
`gcc` is the name of the stack. This name is arbitrary. This key contains the metadata
value which is used internally to declare that the `gcc` entry refers to a PE. For
this, we add the value `pe` to the `section` key. This is how xdp knows that the
`gcc` key contains information about a PE.
Next we find a key named `stable`. The name of this key is arbitrary and is used
to declare several stacks under the same common name `gcc`. An example of a use
case for this feature is to provide a `stable` release and a `future` release.
The `stable` keyword contains the compiler and libraries that we will want to
enforce as dependencies on the packages to be installed. In the example above,
we define a compiler and an mpi library.
The names `compiler` and `mpi` are arbitrary, but it makes sense to use them.
We can declare more than one PE. For this, we would just add another key, for example
`intel` having the same child keys and appropriate values.
[NICE-TO-HAVE]
+ As we already discussed, having metadata visible to the user makes the file longer
and harder to read.
## package list advanced concepts
### setting package preferences
We can flag a package if we want spack to use this set of variants when building the package
as a dependency for other pacakges. In the following example, the `defaut` keyword is added
meaning that xdp should add this package to spack `packages.yaml` configuration file.
```yaml
- zlib:
    default:
      variants: +optimize
```
In the preceeding example, xdp will add the spec `zlib` to the manifest file but in
packages.yaml the spec will be `zlib~optimize`. If we want to add a variant to the
spec being written to the manifest file, then we must add the key variants under the
spec like in the following example:
```yaml
- zlib:
    variants: +pic
    default:
      variants: +optimize
```
### package dependencies
Package dependenies can be expressed using the `dependencies` keyword. This keyword is
a child of the package spec. The result is that the dependencies are added to the
spec in the spack.yaml file.
```yaml
- lrzip:
    dependencies:
    - zlib@1.2.8
    - lzo@2.08
```
In the above example, we see that the `dependencies` keyword is a list and it may be used
to enforce some of the variants used by the package. The following spec will appear
in spack.yaml `lrzip^zlib@1.2.8^lzo@2.08`
### externals
### buildable
Sometimes we want spack to use a package that is already available on the system
and we do not want to build a new version. This can happen because the package is
proprietary sofware and there is no spack recipe for it or just because we want
to settle with the version provided by the OS. In these cases, the key `buildable`
can be used. This key is a child of the `default` key
```yaml
- zlib:
    default:
      buildable: true
```
### filters
filters is another technique used to allow the same stack definition to generalize
across multiple platforms. Supose that in your site you have two systems, one that
is GPU accelerated and the other is a classic CPU only system. You can use the same
stack for both systems by defining the GPU acceleration value in the platform file
and then make a decision based on that information in the stack file.
that you want to install a package that may benefit
from GPU acceleration.
### blacklisting a module
Not every package built with spack must have a module exposing its PATH to the
environment. Some packages are dependencies and others are used indirectly.
The `blacklist` key accepts a boolean value and is child of the package spec.
```yaml
- zlib:
    blacklist: true
```
### activated packages
### autoload
### tokens
Tokens are placeholders that allow the stack file to generalize to different
architectures or just simple flavours of the same stack. For example, you can
declare the version of the compiler provided by the OS in the platflorm file and
then place the `<core_compiler>` token under the `core` key in the stack file
when defining this PE. In simple terms, tokens allows the user to define
platform specifics in the platflorm file and have this information available in
the stack file.

## canonical forms
### programming environment
### package list
### package definition

```yaml
- package:
    variants:
      common: spec
      filter_1:
        choice_1: spec_1
        choice_2: spec_2
    dependencies:
      common:
        - spec1
        - spec2
      filter_1:
        choice_1: spec_1
        choice_2: spec_2
    default:
      version: [version]
      variants:
        common: spec
        filter_1:
          choice_1: spec_1
          choice_2: spec_2
      dependencies:
        common:
        - spec1
        - spec2
        filter_1:
          choice_1: spec_1
          choice_2: spec_2
```
The following section will explain the expected behaviour when using each one of the
previous attributes.

#### dependencies
These are the specs on which the package depends on. This attribute can be a list
of specs or a dictionary containing the common key and optionaly a filter. In this
case, the list of specs is declared in the common key.
The resulting behaviour is that the specs declared as dependencies will be appended
at the end of the spec using the caret sign.
```yaml
- cp2k:
    dependencies:
      - boost+mpi
      - fftw+mpi+openmp
- slepc:
    dependencies:
      common:
        - hdf5~ipo+mpi
      gpu:
        nvidia:
          - petsc+cuda
          - suite-sparse+cuda
        none: []
- py-torchvision:
    dependencies:
      gpu:
        nvidia:
          - py-torch+mpi+cuda
          - magma+cuda
        none:
          - py-torch+mpi~cuda
```
Given the previous specs, we can be sure to found the folliwing lines in the
spack.yaml file for a platform where the nvidia accelerator would have been
defined:
```yaml
- cp2k ^boost+mpi ^fftw+mpi+openmp
- slepc ^hdf5~ipo+mpi ^petsc+cuda ^suite-sparse+cuda
- py-torchvision ^py-torch+mpi+cuda ^magma+cuda
```
The dependencies method from the Package class will return a string or None.
## glossary
+ manifest - spack.yaml file
+ programming environment
+ stack
+ platform
+ core compiler
+ spec
+ variant
