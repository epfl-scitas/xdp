# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                       #
# SCITAS STACK DEPLOYMENT 2023, EPFL                                    #
#                                                                       #
# This module provides default values for all the variables. This       #
# enable xdp to work out-of-the-box with no previous configuration.     #
#                                                                       #
#                                                                       #
#                                                                       #
#                                                                       #
#                                                                       #
#                                                                       #
#                                                                       #
#                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import sys

# The following line makes de tracer available
# every time this module is imported.
from pdb import set_trace as st

def get_prefix():
    """Return prefix of xdp"""

    return(get_subdir(__loader__.get_filename(), 6))

def get_subdir(path, level = 1, sep = None):
    """Return subdirectory of specified level

    /scratch/site/user/dev -> /scratch/site/user (level=1)
    /scratch/site/user/dev -> /scratch/site      (level=2)
    """

    sep = os.sep
    path_list = path.split(sep)
    dir_levels = path_list[1:len(path_list) - level]
    return (sep + sep.join(dir_levels))
