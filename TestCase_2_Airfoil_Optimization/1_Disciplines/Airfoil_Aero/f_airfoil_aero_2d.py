#-------------------------------------------------------------------------------
# This file contains all functions required by the discipline wrapper
#-------------------------------------------------------------------------------
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

import os, shutil, random
import warnings

from ipdb import set_trace as keyboard





def create_XFOIL_input_files(xfoil_path, airfoil_shape, xfoil_set = None):
    """
    Creates the input files which are necessary for XFOIL to run. These are:
    1) A file with the geometry of the airfoil
    2) An instruction file which is used to run XFOIL automatically
    3) A debug batch file to run an XFOIL analysis outside the optimization loop
    :param xfoil_path: path pointing to XFOIL main folder
    :param airfoil_shape: a list containing (x,y) coordinates of an airfoil
    :param xfoil_set: a dictionary containing some XFOIL settings (i.e. Reynolds etc..)
    :return runtime_id: ID of the runtime folder containing XFOIL inputs/outputs
    """

    # Recover XFOIl settings or, if None is supplied, use the internal default settings
    # ----------------------------------------------------------------------
    xfoil_set_DEFAULT = {'Reynolds'     :   3000000,
                         'NumbIter'     :   100,
                         'Alpha_Min'    :   -5,
                         'Alpha_Max'    :   15,
                         'Alpha_Delta'  :   1.0}

    if not xfoil_set:
        xfoil_set = xfoil_set_DEFAULT


    # Create a runtime folder >> XFOIL Inputs/Outputs will be created here
    # ----------------------------------------------------------------------
    runtime_path = create_runtime_folder(xfoil_path)
    runtime_id   =  runtime_path.split("RunTime_")[1]

    # 1) Write airfoil file
    # ----------------------------------------------------------------------
    airfoil_path = runtime_path + os.sep + 'airfoil_input.dat'
    np.savetxt(airfoil_path, np.transpose([airfoil_shape[0], airfoil_shape[1]]),
               fmt='%.8f', header='Airfoil', comments='')

    # 2) Write XFOIL Instructions file
    # ----------------------------------------------------------------------
    # Address of the instructions path and (relative) path to the airfoil
    instr_path = runtime_path + os.sep + 'instructions.txt'
    airfoil_file_path = './RunTime_' + runtime_id + '/airfoil_input.dat'
    polar_file_path = './RunTime_' + runtime_id + '/polar_output.dat'

    # Fill template with all the lines to write >> some values are set from the xfoil_set dictionary
    instr_template = ['load \n',
                      airfoil_file_path + '\n',
                      'pane \n',
                      'oper \n',
                      'iter \n',
                      str(xfoil_set['NumbIter']) + '\n',
                      'visc \n',
                      str(xfoil_set['Reynolds'])+ '\n',
                      'pacc \n',
                      polar_file_path + '\n',
                      '\n',
                      'aseq \n',
                      str(xfoil_set['Alpha_Min']) + '\n',
                      str(xfoil_set['Alpha_Max']) + '\n',
                      str(xfoil_set['Alpha_Delta']) + '\n',
                      '\n',
                      'quit'
                      ]

    # Write instructions file
    with open(instr_path, 'w') as f:
        for line in instr_template:
            f.write(line)

    # 3) Write debug batch file
    # ----------------------------------------------------------------------
    # If some problems occur in the simulation, this file allows to quickly run a debug
    batch_file_path = runtime_path + os.sep  + '/debug.bat'
    debug_line = 'start cmd.exe /k "cd.. && xfoil.exe < ' + './RunTime_' + str(runtime_id) + '/instructions.txt"'

    f2=open(batch_file_path, 'w')
    f2.write(debug_line)
    f2.close()


    return runtime_id


def run_XFOIL(xfoil_path, runtime_id):
    """
    Runs XFOIL with a set of instructions provided in a separate file
    :param xfoil_path: path pointing to the XFOIL folder
    :param runtime_path:  path pointing to the RunTime folder (stroing Inputs/Outputs)
    :return:
    """

    command = 'cd ' + xfoil_path + ' && ' + 'xfoil.exe < ./RunTime_' + str(runtime_id) +'/instructions.txt'

    os.system(command)


def read_XFOIL_results(xfoil_path, runtime_id):
    """
    Reads the polar file coming from XOFIL. COmputes aerodynamic efficiency and returns the max value
    :param xfoil_path: path pointing to the XFOIL folder
    :param runtime_path:  path pointing to the RunTime folder (stroing Inputs/Outputs)
    :return:
    """
    # Initialize output
    results = {}


    polar_path = xfoil_path + os.sep + 'RunTime_' + str(runtime_id) + os.sep +'polar_output.dat'

    # Read polar output data
    try:
        data = np.loadtxt(polar_path, skiprows=12)
    except:
        raise ValueError('Error on reading polar file ' + polar_path)

    alpha = data[:, 0]
    cl = data[:, 1]
    cd = data[:, 2]
    eff = cl/cd

    # Find max efficiency
    eff_max         = np.max(eff)
    i_eff_max       = np.argmax(eff)
    alpha_eff_max   = alpha[i_eff_max]

    # Assign output
    results['Alpha']        = alpha
    results['CL']           = cl
    results['CD']           = cd
    results['E']            = eff
    results['E_max']        = eff_max
    results['Alpha_E_max']  = alpha_eff_max

    return results


def create_airfoil_geometry(m, p, t, plot_shape = False):
    """
    Applies the relations of NACA 4-digits series to generate the airfoil geometry.
    The mathematical formulation can be found in several sources, including Wikipedia
    Airfoil chord is assumed unitary
    :param m: maximum airfoil camber
    :param p: position of max camber
    :param t: max thickness
    :param plot_shape: if True, plot the generated airfoil shape
    :return airfoil_shape: a list containing x, y coordinates of the generated airfoil
    """

    # Recover correct order of magnitude
    t = t/100
    p = p/10
    m = m/100


    # Define X (chord-wise axis) and initialize running quantities
    x  = np.linspace(0,1,100)

    yc = np.zeros_like(x)
    yt = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)


    if m!=0:

        # Compute the camber line
        for i in range(len(x)):
            xi = x[i]
            if xi <= p:
                yc[i] = (m/(p**2))*(2*p*xi-xi**2)
            else:
                yc[i] = (m/((1-p)**2))*(1 -2*p +2*p*xi - xi**2)

        # Compute derivative of the camber line
        for i in range(len(x)):
            xi = x[i]
            if xi <= p:
                dyc_dx[i] = ((2*m)/(p**2))*(p-xi)
            else:
                dyc_dx[i] = ((2*m)/(1-p)**2)*(p-xi)

    # Compute arctan
    theta = np.arctan(dyc_dx)

    # Compute half thickness
    for i in range(len(x)):
        xi = x[i]
        yt[i] = (t/0.2)*(0.2969*sqrt(xi) - 0.1260*xi -0.3516*(xi**2) + 0.2843*(xi**3) -0.1015*(xi**4))




    # Compute upper/lower surfaces
    xup = x - yt*np.sin(theta)
    yup = yc + yt * np.cos(theta)

    xdn = x + yt * np.sin(theta)
    ydn = yc - yt * np.cos(theta)

    # Override x[0],y[0] to avoid numerical issues set == 0
    xup[0] = 0
    xdn[0] = 0
    yup[0] = 0
    ydn[0] = 0

    # Create airfoil shape to output
    xairf = np.concatenate((np.flip(xup), xdn[1:]))
    yairf = np.concatenate((np.flip(yup), ydn[1:]))

    airfoil_shape = [xairf, yairf]

    # Keyboard
    if plot_shape:
        plot_airfoil_shape(airfoil_shape)



    return airfoil_shape



def plot_airfoil_shape(airfoil_shape):
    """
    Plot the upper and lower shape of an airfoil
    """



    fig, ax = plt.subplots()


    ax.plot(airfoil_shape[0], airfoil_shape[1], color='b')


    ax.set_xlabel("X", fontsize=12)
    ax.set_ylabel("Y", fontsize=12)

    ax.set_aspect('equal')
    ax.grid()
    plt.show()



def create_runtime_folder(path):
    """
    Creates a runtime folder where useful data can be stored at runtime
    :param path: string pointing to the location where the Runtime folder must be created
    :return runtime_path: generated path of the runtime folder
    """

    # Assign a random number and check it is not already there
    exists = True

    while exists:
        rdi = random.randint(10000000, 99999999)
        runtime_path = path + os.sep + 'RunTime_' + str(rdi)
        exists = os.path.isdir(runtime_path)

    # Create the runtime directory
    os.mkdir(runtime_path)

    return runtime_path



def clear_runtime_folders(path):
    """
    Deletes all Runtime folders present in the specified path
    """

    dirs = os.listdir(path)

    for dir in dirs:
        if 'RunTime' in dir:
            try:
                shutil.rmtree(path + os.sep + dir)
            except:
                warnstr = '[WARNING]: Impossible to clear folder: ' + dir
                warnings.warn(warnstr)
