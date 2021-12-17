from gemseo.core.discipline import MDODiscipline
from numpy import array, ones
from math import exp


class SellarSystem(MDODiscipline):
    def __init__(self):
        super(SellarSystem, self).__init__()

        # Initialize the grammars to define inputs and outputs
        self.input_grammar.initialize_from_data_names(["x", "z", "y_1", "y_2"])
        self.output_grammar.initialize_from_data_names(["obj", "c_1", "c_2"])

        # Default inputs define what data to use when the inputs are not
        # provided to the execute method
        self.default_inputs = {
            "x": ones(1),
            "z": array([4.0, 3.0]),
            "y_1": ones(1),
            "y_2": ones(1),
        }

    def _run(self):
        # The run method defines what happens at execution
        # ie how outputs are computed from inputs
        x, z, y_1, y_2 = self.get_inputs_by_name(["x", "z", "y_1", "y_2"])
        # The ouputs are stored here
        self.local_data["obj"] = array([x[0] ** 2 + z[1] + y_1[0] ** 2 + exp(-y_2[0])])
        self.local_data["c_1"] = array([3.16 - y_1[0] ** 2])
        self.local_data["c_2"] = array([y_2[0] - 24.0])

#----------------------------------------------------------------------------------------
# Discipline Tester
#----------------------------------------------------------------------------------------
if __name__=='__main__':

    disc_system = SellarSystem()
    disc_system.execute()

