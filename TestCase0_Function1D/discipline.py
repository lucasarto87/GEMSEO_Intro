from gemseo.core.discipline import MDODiscipline
from numpy import ones, sin, array


class Function1D(MDODiscipline):
    def __init__(self):
        super(Function1D, self).__init__()

        self.input_grammar.initialize_from_data_names(["x"])
        self.output_grammar.initialize_from_data_names(["f"])

        self.default_inputs = {"x": ones(1)}

    def _run(self):

        x = self.get_inputs_by_name("x")

        f = sin(x) + sin((10/3)*x)

        self.local_data["f"] = array(f)


#----------------------------------------------------------------------------------------
# Discipline Tester
#----------------------------------------------------------------------------------------
if __name__=='__main__':

    disc = Function1D()
    disc.execute()