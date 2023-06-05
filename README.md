# xdp

eXtended Deploy - define and deploy a software stack over different architectures using Spack

## Introduction
> Escrever os ficheiros yaml
> Fornecer um conjunto de scripts para fazer o deploy da stack
> Facilitar workflows Jenkins/Gitlab
> Outras ferramentas (yammi)

Good software do simple things.

+ Given a stack file and a system configuration, xdp will write the spack
configuration. This includes spack.yaml, packages.yaml, config.yaml, etc...

+ xdp makes it easy to create a Jenkins or Gitlab workflow to add packages to
the spack in a continuous integration fashion.

+ xdp provides commands to analyse the concretization step.

## Quick start

```bash
git clone git@github.com:epfl-scitas/xdp
source xdp/share/xdp.sh # this can install spack
echo "- zlib" > stack.yaml
xdp deploy
```

## Meta

### Python packages to generate UML class diagmrams


### Docstrings

+ All docstrings should have the same max character length as comments = `72` characters.
+ reStructured Text

