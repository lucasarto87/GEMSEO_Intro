import os, sys
import numpy as np

# Add required folders
root = os.path.dirname(os.path.abspath(__file__).split('disciplines')[0])
sys.path.append(root + os.sep + 'disciplines' + os.sep + 'TDP')
sys.path.append(root + os.sep + 'global' )

from gemseo.core.discipline import MDODiscipline

from f_total_production import compute_daily_production
from utilities import read_resources_specs

from ipdb import set_trace as keyboard

class TDP(MDODiscipline):

    def __init__(self,
                 N_pcs_target=100,
                 N_hours=8,
                 resource_file=None):

        super(TDP, self).__init__()

        # Define internal quantitites
        if not resource_file:
            resource_file = root + os.sep + 'global' + os.sep + 'resources.txt'

        self.resource_file = resource_file
        self.N_pcs_target = N_pcs_target
        self.N_hours = N_hours

        # Define inputs >> Name, type and default value
        dictIn = {'p1': np.array([0.0]),         # Percent of work assigned to Resource 1
                  'p2': np.array([0.0]),         # Percent of work assigned to Resource 2
                  'p3': np.array([0.0])}        # Percent of work assigned to Resource 3


        # Initialize input grammar and assign default values
        self.input_grammar.initialize_from_base_dict(dictIn)
        self.default_inputs = dictIn

        # Inizialize output grammar and types
        DictOut = { 'N_pcs'        : np.array([0.0]),       # Total number of components produced
                    'N_pcs_const'  : np.array([0.0]),       # Total number of components produced (constraint)
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
        prod_data = compute_daily_production(self.N_hours, p , resources)


        # Compute production constraint
        n_pcs_tot = prod_data['N_pcs_TOT']
        const_prod = -(n_pcs_tot - self.N_pcs_target) / self.N_pcs_target


        # Send output
        dictOut = {'N_pcs'      : np.array([n_pcs_tot]),
                   'N_pcs_const': np.array([const_prod])}

        # Save the output in the discipline local store >>> Transmit output to GEMSEO
        self.local_data.update(dictOut)

        print(50*'-')
        print('TOT PROD =  %.4f' % dictOut['N_pcs'])
        print('c_PROD   =  %.4f' % dictOut['N_pcs_const'])


# ----------------------------------------------------------------------------------------
# Discipline Tester
# ----------------------------------------------------------------------------------------
if __name__ == '__main__':
    disc_tdp = TDP()
    disc_tdp.execute()