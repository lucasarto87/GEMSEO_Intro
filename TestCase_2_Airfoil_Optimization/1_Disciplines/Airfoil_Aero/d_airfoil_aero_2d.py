
import os, sys
import numpy as np

# Add project folders
root = os.path.dirname(os.path.abspath(__file__).split('TestCase_2_Airfoil_Optimization')[0])


from gemseo.core.discipline import MDODiscipline
from f_airfoil_aero_2d import create_airfoil_geometry, \
    create_XFOIL_input_files, clear_runtime_folders, run_XFOIL, read_XFOIL_results

from ipdb import set_trace as keyboard

class AirfoilAero2D(MDODiscipline):

    def __init__(self, xfoil_path=None):
        super(AirfoilAero2D, self).__init__()

        # Path to XFOIL main directory (if none supplied, use default location)
        if  xfoil_path:
            self.xfoil_path = xfoil_path
        else:
            self.xfoil_path = root +os.sep + 'TestCase_2_Airfoil_Optimization' + os.sep + '4_Tools' + os.sep + 'XFOIL'

        # Clear all runtime folders from XFOIl
        clear_runtime_folders(self.xfoil_path)


        # Define inputs >> Name, type and default value
        dictIn = {'NACA_M': 2.0,         # maximum airfoil camber
                  'NACA_P': 4.0,         # position of maximum camber
                  'NACA_T': 15.0}        # maximum thickness


        # Initialize input grammar and assign default values
        self.input_grammar.initialize_from_base_dict(dictIn)
        self.default_inputs = dictIn

        # Inizialize output grammar and types
        DictOut = { 'Alpha' : np.array([0.0, 0.0]),
                    'CL'    : np.array([0.0, 0.0]),
                    'CD'    : np.array([0.0, 0.0]),
                    'E_max' : 0.0}

        self.output_grammar.initialize_from_base_dict(DictOut)



    def _run(self):

        # Recover actualized inputs >> from GEMSEO
        #------------------------------------------------------------------------------------
        dictIn = self.get_input_data()

        m = dictIn['NACA_M']
        p = dictIn['NACA_P']
        t = dictIn['NACA_T']


        # Create the airfoil geometry and run an XFOIL simulation
        # ------------------------------------------------------------------------------------

        # Generate an airfoil geometry
        airfoil = create_airfoil_geometry(m, p, t)

        # Create input files for XFOIL
        runtime_id = create_XFOIL_input_files(self.xfoil_path, airfoil)

        try:
            # Run XFOIL
            run_XFOIL(self.xfoil_path, runtime_id)

            # Read XFOIL results
            results = read_XFOIL_results(self.xfoil_path, runtime_id)

        except:
            raise ValueError('FATAL CRASH OF THE DISCIPLINE OCCURRED.')


        # Send actualized outputs >> to GEMSEO
        # ------------------------------------------------------------------------------------
        dictOut = { 'Alpha' : results['Alpha'],
                    'CL'    : results['CL'],
                    'CD'    : results['CD'],
                    'E_max' : results['E_max']}

        # Save the output in the discipline local store >>> Transmit output to GEMSEO
        self.local_data.update(dictOut)



# ----------------------------------------------------------------------------------------
# Discipline Tester
# ----------------------------------------------------------------------------------------
if __name__ == '__main__':
    disc_airf_aero = AirfoilAero2D()
    disc_airf_aero.execute()