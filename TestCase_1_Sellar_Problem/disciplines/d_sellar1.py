from gemseo.core.discipline import MDODiscipline
from numpy import array, ones


class Sellar1(MDODiscipline):
    def __init__(self):
        super(Sellar1, self).__init__()
        self.input_grammar.initialize_from_data_names(["x", "z", "y_2"])
        self.output_grammar.initialize_from_data_names(["y_1"])
        self.default_inputs = {
            "x": ones(1),
            "z": array([4.0, 3.0]),
            "y_1": ones(1),
            "y_2": ones(1),
        }

    def _run(self):
        x, z, y_2 = self.get_inputs_by_name(["x", "z", "y_2"])
        self.local_data["y_1"] = array(
            [(z[0] ** 2 + z[1] + x[0] - 0.2 * y_2[0]) ** 0.5]
        )

#----------------------------------------------------------------------------------------
# Discipline Tester
#----------------------------------------------------------------------------------------
if __name__=='__main__':

    disc_1 = Sellar1()
    disc_1.execute()