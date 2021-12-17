from __future__ import division, unicode_literals

from math import exp

from matplotlib import pyplot as plt
from numpy import array, ones

from gemseo.algos.design_space import DesignSpace
from gemseo.api import configure_logger, create_scenario
from gemseo.core.discipline import MDODiscipline

configure_logger()

from disciplines.d_sellar1 import Sellar1
from disciplines.d_sellar2 import Sellar2
from disciplines.d_system import SellarSystem

# Create the disciplines
disciplines = [Sellar1(), Sellar2(), SellarSystem()]

# Define the design space
design_space = DesignSpace()

design_space.add_variable("x", 1, l_b=0.0, u_b=10.0, value=ones(1))
design_space.add_variable("z", 2, l_b=(-10, 0.0), u_b=(10.0, 10.0), value=array([4.0, 3.0]))
design_space.add_variable("y_1", 1, l_b=-100.0, u_b=100.0, value=ones(1))
design_space.add_variable("y_2", 1, l_b=-100.0, u_b=100.0, value=ones(1))

# Create scenario
scenario = create_scenario(disciplines, formulation="IDF", objective_name="obj", design_space=design_space)

# Add constraints
scenario.add_constraint("c_1", "ineq")
scenario.add_constraint("c_2", "ineq")

# Run scenario
scenario.set_differentiation_method("finite_differences", 1e-6)
scenario.execute(input_data={"max_iter": 10, "algo": "SLSQP"})

# Post-Process
scenario.post_process("OptHistoryView", save=False, show=False)
plt.show()