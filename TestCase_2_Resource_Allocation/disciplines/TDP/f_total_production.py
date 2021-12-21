#-------------------------------------------------------------------------------
# This file contains all functions required by the discipline wrapper
#-------------------------------------------------------------------------------
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

import os, shutil, random
import warnings

from ipdb import set_trace as keyboard




def compute_daily_production(n_hrs,p,resources):
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
    N_pcs_TOT = 0

    # Loop on working time
    for h in range(n_hrs):

        N_pcs_h = 0

        # Loop on resources
        for ir in range(len(resources)):
            tag = 'Resource' + str(ir+1)
            N0i = resources[tag]['Production_Max']
            phi_i = resources[tag]['Fatigue_Coeff']

            Nhi = N0i - phi_i*(h+1)

            N_pcs_h = N_pcs_h + round(Nhi*p[ir][0])

        N_pcs_TOT = N_pcs_TOT + N_pcs_h

    # Send output
    prod_data= {'N_pcs_TOT' : N_pcs_TOT}

    return prod_data