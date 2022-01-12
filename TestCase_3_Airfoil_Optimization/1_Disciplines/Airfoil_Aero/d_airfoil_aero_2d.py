
import os, sys
import numpy as np

# Add required folders
root = os.path.dirname(os.path.abspath(__file__).split('1_Disciplines')[0])
sys.path.append(root + os.sep + '1_Disciplines' + os.sep + 'Airfoil_Aero')

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
            self.xfoil_path = root +os.sep + '4_Tools' + os.sep + 'XFOIL'

        # Clear all runtime folders from XFOIl
        clear_runtime_folders(self.xfoil_path)


        # Define inputs >> Name, type and default value
        dictIn = {'NACA_M': np.array([2.0]),         # maximum airfoil camber
                  'NACA_P': np.array([4.0]),         # position of maximum camber
                  'NACA_T': np.array([15.0])}        # maximum thickness


        # Initialize input grammar and assign default values
        self.input_grammar.initialize_from_base_dict(dictIn)
        self.default_inputs = dictIn

        # Inizialize output grammar and types
        DictOut = { 'AirfoilX'  : np.array([0.0]),       # Airfoil geometry (X coordinate)
                    'AirfoilY'  : np.array([0.0]),       # Airfoil geometry (Y coordinate)
                    'Alpha'     : np.array([0.0]),       # Angles of attack
                    'CL'        : np.array([0.0]),       # Lift coefficient
                    'CD'        : np.array([0.0]),       # Drag coeffiecient
                    'E'         : np.array([0.0]),       # Aerodynamic efficiency
                    'E_max'     : 0.0}                   # Max efficiency

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
        airfoil = create_airfoil_geometry(m, p, t,plot_shape=False)

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
        dictOut = { 'AirfoilX'  : airfoil[0],
                    'AirfoilY'  : airfoil[1],
                    'Alpha'     : results['Alpha'],
                    'CL'        : results['CL'],
                    'CD'        : results['CD'],
                    'E'         : results['E'],
                    'E_max'     : results['E_max']}

        # Save the output in the discipline local store >>> Transmit output to GEMSEO
        self.local_data.update(dictOut)

        # Send status
        print('')
        print(50*'-')
        print('NACA_M:    %.2f' % dictIn['NACA_M'])
        print('NACA_P:    %.2f' % dictIn['NACA_P'])
        print('NACA_T:    %.2f' % dictIn['NACA_T'])
        print(50*'-')
        print('E_max:     %.2f' % dictOut['E_max'])
        print(50 * '-')

# ----------------------------------------------------------------------------------------
# Discipline Tester
# ----------------------------------------------------------------------------------------
if __name__ == '__main__':
    disc_airf_aero = AirfoilAero2D()

    # Run with custom inputs
    disc_airf_aero.default_inputs['NACA_M'] = np.array([0.0])
    disc_airf_aero.default_inputs['NACA_P'] = np.array([0.0])
    disc_airf_aero.default_inputs['NACA_T'] = np.array([25.0])

    disc_airf_aero.execute()