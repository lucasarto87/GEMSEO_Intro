from __future__ import division, unicode_literals

from numpy import array

from gemseo.algos.design_space import DesignSpace
from gemseo.api import configure_logger, create_scenario

configure_logger()

from discipline import Function1D


# Create the disciplines
disciplines = [Function1D()]

# Define the design space
design_space = DesignSpace()

design_space.add_variable("x", 1, l_b=2.5, u_b=7.0, value=array([2.5]))

# Create scenario
scenario = create_scenario(disciplines,
                           formulation="IDF",
                           objective_name="f",
                           design_space=design_space)


# Run scenario
scenario.execute(input_data={"max_iter": 100, "algo": "NLOPT_COBYLA"})

# Post-Process
scenario.post_process("OptHistoryView", save=False, show=True)
