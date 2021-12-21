import numpy as np

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