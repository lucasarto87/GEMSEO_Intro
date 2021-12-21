import os, sys
import numpy as np

# Add required folders
root = os.path.dirname(os.path.abspath(__file__).split('disciplines')[0])
sys.path.append(root + os.sep + 'disciplines' + os.sep + 'TPC')
sys.path.append(root + os.sep + 'global' )

from gemseo.core.discipline import MDODiscipline

from f_total_cost import compute_production_cost
from utilities import read_resources_specs

from ipdb import set_trace as keyboard

class TPC(MDODiscipline):

    def __init__(self, N_hours=8, resource_file=None):

        super(TPC, self).__init__()

        # Define internal quantitites
        if not resource_file:
            resource_file = root + os.sep + 'global' + os.sep + 'resources.txt'

        self.resource_file = resource_file
        self.N_hours = N_hours

        # Define inputs >> Name, type and default value
        dictIn = {'p1': np.array([0.0]),         # Percent of work assigned to Resource 1
                  'p2': np.array([0.0]),         # Percent of work assigned to Resource 2
                  'p3': np.array([0.0])}         # Percent of work assigned to Resource 3


        # Initialize input grammar and assign default values
        self.input_grammar.initialize_from_base_dict(dictIn)
        self.default_inputs = dictIn

        # Inizialize output grammar and types
        DictOut = { 'C_TOT'        : np.array([0.0]),       # Total cost
                     }

        self.output_grammar.initialize_from_base_dict(DictOut)


    def _run(self):
        # Recover actualized inputs >> from GEMSEO
        # ------------------------------------------------------------------------------------
        dictIn = self.get_input_data()

        # retrieve allocation array
        p = [dictIn['p1'], dictIn['p2'], dictIn['p3']]


        # retrieve Resource information
        resources = read_resources_specs(self.resource_file)

        # Compute total daily production
        cost_data = compute_production_cost(self.N_hours, p , resources)

        # Send output
        dictOut = {'C_TOT'      :  cost_data['C_TOT']}


        print('TOT COST =  %.4f' % dictOut['C_TOT'])
        print(50 * '-')

        # Save the output in the discipline local store >>> Transmit output to GEMSEO
        self.local_data.update(dictOut)

# ----------------------------------------------------------------------------------------
# Discipline Tester
# ----------------------------------------------------------------------------------------
if __name__ == '__main__':
    disc_cost = TPC()
    disc_cost.execute()
