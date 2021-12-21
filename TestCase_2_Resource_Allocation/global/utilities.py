import numpy as np
from math import floor

def read_resources_specs(res_file):
    """
    Reads the file containing the resources specs
    :param res_file: path towards the resources file
    :return resources: a dictionary containing the resources specifications
    """

    data = np.loadtxt(res_file, skiprows=1)

    res_production = data[:,0]
    res_fatigue = data[:,1]
    res_cost = data[:,2]

    resources = {}

    for ir in range(3):
        dictRes = {}

        dictRes['Production_Max'] =   res_production[ir]
        dictRes['Fatigue_Coeff'] = res_fatigue[ir]
        dictRes['Hourly_Cost'] =   res_cost[ir]

        tag = 'Resource' + str(ir+1)

        resources[tag] = dictRes

    return resources


def compute_visibility_vector(n_hrs,p):

    # retrieve number of resources
    n_r = len(p)

    nu = np.zeros((n_r, n_hrs))

    for ir in range(n_r):
        # Retrieve charge
        pi = p[ir][0]

        # Full working hours and residual working time
        n_hrs_i = floor(pi*n_hrs)
        r_hrs_i = pi*n_hrs - n_hrs_i

        # Fill a '1' in all the full worked hours
        nu[ir,:n_hrs_i] = 1

        # FIll the residual on the last (partial) hour
        if n_hrs_i < n_hrs:
            nu[ir, n_hrs_i] = r_hrs_i

    return nu
