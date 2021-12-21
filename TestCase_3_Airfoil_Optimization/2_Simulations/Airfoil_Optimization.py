###################################################################################################
# This is a simulation template for GEMSEO 3.2.1
#
# Author: L.Sartori
#
###################################################################################################

import os, sys

# Add project paths
root = os.path.dirname(os.path.abspath(__file__).split('2_Simulations')[0])
sys.path.append(root)
sys.path.append(root + os.sep +  '0_Global')
sys.path.append(root + os.sep +  '1_Disciplines')
sys.path.append(root + os.sep +  '3_Tools')
sys.path.append(root + os.sep +  '4_Results')

# Import GEMSEO
from gemseo.api import create_design_space, create_scenario, configure_logger
from gemseo.algos.opt_problem import OptimizationProblem

# Import general libraries
import numpy as np

# Import disciplines
from Airfoil_Aero.d_airfoil_aero_2d import AirfoilAero2D

from ipdb import set_trace as keyboard

# Initialize logger
logger = configure_logger()

if __name__ == '__main__':
    """
    ---------------------------------------------------------------------------------------
    Run an aerodynamic optimization of a NACA 4-digits airfoil to maximize efficiency
    ---------------------------------------------------------------------------------------
    [Merit function]: Max efficiecny

    [Disciplines]: AirfoilAero2D

    [Design variables]: the 3 parameters of the NACA 4-digits family:
        
        NACA_P = amount of maximum camber
        NACA_M = position of maximum camber
        NACA_T = amount of thickness

    [Constraints]: None

    [Architecture]: Single-level Monodisciplinary optimization
    ---------------------------------------------------------------------------------------
    REMARKS:
    ---------------------------------------------------------------------------------------                 
    """

    # Define run identificator
    output  = 'NACA_4_Aero_Opti'

    # Initialize the disciplines
    airfoil_aero = AirfoilAero2D()

    disciplines = [airfoil_aero]


    # Define the design space
    #--------------------------------------------------------------------------------------
    ds = create_design_space()

    ds.add_variable('NACA_M', 1, l_b=np.array([0.0]), u_b=np.array([9.9]), value=np.array([0.0]))
    ds.add_variable('NACA_P', 1, l_b=np.array([2.0]), u_b=np.array([6.0]), value=np.array([5.0]))
    ds.add_variable('NACA_T', 1, l_b=np.array([10.0]), u_b=np.array([40.0]), value=np.array([25.0]))


    # Define the objective function
    # --------------------------------------------------------------------------------------
    obj = 'E_max'

    # Create scenario
    # --------------------------------------------------------------------------------------
    scenario = create_scenario( disciplines,
                                formulation='DisciplinaryOpt',
                                objective_name=obj,
                                maximize_objective=True,
                                design_space=ds,
                                scenario_type='MDO')

    # Add observables
    # --------------------------------------------------------------------------------------
    # This allows to keep trace of additional quantities in the optimization history
    scenario.formulation.add_observable('AirfoilX')
    scenario.formulation.add_observable('AirfoilY')
    scenario.formulation.add_observable('Alpha')
    scenario.formulation.add_observable('CL')
    scenario.formulation.add_observable('CD')
    scenario.formulation.add_observable('E')


    # Run scenario
    # --------------------------------------------------------------------------------------
    # DOE Options
    # opts = {'algo':'DiagonalDOE', 'n_samples': 3}

    # Optimization options >> COBYLA search method
    opts = {"max_iter": 100, "algo": "NLOPT_COBYLA"}

    # Optimization options >> Classic SQP with gradient approximation
    #opts = {"max_iter": 30, "algo": "SLSQP"}
    #scenario.set_differentiation_method(method='finite_differences', step=1e-02)

    scenario.execute(opts)
    scenario.print_execution_metrics()


    # Post-processing
    # --------------------------------------------------------------------------------------
    scenario.post_process("OptHistoryView", save=False, show=True)

    # Save h5 history file
    h5file = root + os.sep + '3_Results' + os.sep +  'history_' + output + '.h5'
    scenario.save_optimization_history(h5file, file_format="hdf5")