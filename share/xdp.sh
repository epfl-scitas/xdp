#!/bin/bash
#
# EPFL-SCITAS 2023
#
# xdp setup script
# last udpate: 02/05/2023

git clone git@github.com:spack/spack .spack
source .spack/share/spack/setup-env.sh

# Check if spack is already loaded in the environment and clean it up
unset SPACK_SYSTEM_CONFIG_PATH
