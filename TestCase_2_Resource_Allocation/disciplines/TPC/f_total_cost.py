#-------------------------------------------------------------------------------
# This file contains all functions required by the discipline wrapper
#-------------------------------------------------------------------------------
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

import os, shutil, random
import warnings

from ipdb import set_trace as keyboard




def compute_production_cost(n_hrs,p,resources):
    """
    COmputes total daily production from the 3 resources, according to their allocation charge pi
    :param n_hrs:
    :param p1:
    :param p2:
    :param p3:
    :param resources:
    :return:
    """

    # initialize output
    C_TOT = 0

    # Loop on working time
    for h in range(n_hrs):

        C_h = 0

        # Loop on resources
        for ir in range(len(resources)):
            tag = 'Resource' + str(ir+1)

            ci = resources[tag]['Hourly_Cost']

            C_h = C_h + ci*p[ir]

        C_TOT = C_TOT + C_h

    # Send output
    cost_data= {'C_TOT' : C_TOT}

    return cost_data