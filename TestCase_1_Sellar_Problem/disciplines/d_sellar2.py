from gemseo.core.discipline import MDODiscipline
from numpy import array, ones

class Sellar2(MDODiscipline):
    def __init__(self):
        super(Sellar2, self).__init__()
        self.input_grammar.initialize_from_data_names(["z", "y_1"])
        self.output_grammar.initialize_from_data_names(["y_2"])
        self.default_inputs = {
            "x": ones(1),
            "z": array([4.0, 3.0]),
            "y_1": ones(1),
            "y_2": ones(1),
        }

    def _run(self):
        z, y_1 = self.get_inputs_by_name(["z", "y_1"])
        self.local_data["y_2"] = array([abs(y_1[0]) + z[0] + z[1]])


# ----------------------------------------------------------------------------------------
# Discipline Tester
# ----------------------------------------------------------------------------------------
if __name__ == '__main__':
    disc_2 = Sellar2()
    disc_2.execute()