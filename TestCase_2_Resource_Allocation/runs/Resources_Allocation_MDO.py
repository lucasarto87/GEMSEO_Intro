###################################################################################################
# This is a simulation template for GEMSEO 3.2.1
#
# Author: L.Sartori
#
###################################################################################################

import os, sys

# Add project paths
root = os.path.dirname(os.path.abspath(__file__).split('runs')[0])
sys.path.append(root)
sys.path.append(root + os.sep + 'global')
sys.path.append(root + os.sep + 'disciplines')
sys.path.append(root + os.sep + 'runs')


# Import GEMSEO
from gemseo.api import create_design_space, create_scenario, configure_logger
from gemseo.algos.opt_problem import OptimizationProblem

# Import general libraries
import numpy as np

# Import disciplines
from TDP.d_total_production import TDP
from TPC.d_total_cost import TPC

from ipdb import set_trace as keyboard

# Initialize logger
logger = configure_logger()

if __name__ == '__main__':
    """
    ---------------------------------------------------------------------------------------
    
    ---------------------------------------------------------------------------------------
    [Merit function]: Total production cost

    [Disciplines]: total_daily_production, total_production_costs

    [Design variables]: the 3 parameters of the resources allocation

    [Constraints]: Minimum production > 100 pieces

    [Architecture]: Single-level Monodisciplinary optimization
    ---------------------------------------------------------------------------------------
    REMARKS:
    - Each resource can have an allocation between 0 and 1 (full charge)
    ---------------------------------------------------------------------------------------                 
    """

    # Define run identifier
    output = 'resource_allocation_MDO'

    # Initialize the disciplines
    prod  = TDP(N_pcs_target=78)
    costs = TPC()

    disciplines = [prod, costs]


    # Define the design space
    # --------------------------------------------------------------------------------------
    ds = create_design_space()

    ds.add_variable('p1', 1, l_b=np.array([0.0]), u_b=np.array([1.0]), value=np.array([0.5]))
    ds.add_variable('p2', 1, l_b=np.array([0.0]), u_b=np.array([1.0]), value=np.array([0.5]))
    ds.add_variable('p3', 1, l_b=np.array([0.0]), u_b=np.array([1.0]), value=np.array([0.5]))

    # Define the objective function
    # --------------------------------------------------------------------------------------
    obj = 'C_TOT'

    # Create scenario
    # --------------------------------------------------------------------------------------
    scenario = create_scenario(disciplines,
                               formulation='MDF',
                               objective_name=obj,
                               maximize_objective=False,
                               design_space=ds,
                               scenario_type='MDO',     # scenario_type='MDO',
                               )

    # Add constraints
    # --------------------------------------------------------------------------------------
    scenario.add_constraint("N_pcs_const", "ineq")


    # Add observables
    # --------------------------------------------------------------------------------------
    # This allows to keep trace of additional quantities in the optimization history
    #scenario.formulation.add_observable('AirfoilX')

    # Run scenario
    # --------------------------------------------------------------------------------------
    # DOE Options
    #opts = {'algo':'DiagonalDOE', 'n_samples': 10}

    # Optimization options >> COBYLA search method
    opts = {"max_iter": 500, "algo": "NLOPT_COBYLA"}

    # Optimization options >> Classic SQP with gradient approximation
    #opts = {"max_iter": 30, "algo": "SLSQP"}
    #scenario.set_differentiation_method(method='finite_differences', step=1e-02)

    scenario.execute(opts)
    scenario.print_execution_metrics()

    # Post-processing
    # --------------------------------------------------------------------------------------
    scenario.post_process("OptHistoryView", save=False, show=True)

    # Save h5 history file
    h5file = root + os.sep + 'runs' + os.sep + 'history_' + output + '.h5'
    scenario.save_optimization_history(h5file, file_format="hdf5")
