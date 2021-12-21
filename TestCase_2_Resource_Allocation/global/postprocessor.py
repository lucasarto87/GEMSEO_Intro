###################################################################################################
# This is a generalized Post-Processor class for ANEMOI
#
# Author: L.Sartori
#
###################################################################################################

import matplotlib.pyplot as plt
from gemseo.algos.opt_problem import OptimizationProblem

import warnings
import numpy as np

from ipdb import set_trace as keyboard



class_name = 'GEMSEO Post-Processor'

class GEMSEOPostProcess():

    def __init__(self, cmap=None):

        self.obj_name       = 'None'    # Name of the objective function
        self.func_names     = []        # List of available functions (design variables, merit function, observables...)
        self.data           = {}        # Dictionary containing all data (as function of iteration number)

        self.numb_iter      = None      # Number of iterations
        self.opt_iter       = None      # Optimal iteration

        # Define colormap for multiple plots
        if cmap is None:
            # use default colormap
            self.colormap = [[0.0, 0.0, 0.65],
                             [0.4, 0.9, 1.0]]
        else:
            self.colormap = cmap


    def init_from_h5_file(self, file=None):
        """
        This method reads an h5 file from a GEMSEO analysis and stores the retrieved values of the optimization
        quantities (i.e. objective function, constraints, design variables, observed quantities)
        :param file: path of the h5 file to read
        :return:
        """

        # Read an h5file into an OptimizationProblem
        try:
            opt = OptimizationProblem.import_hdf(file)

        except:
            raise IOError('[' + class_name + ']: Unable to read the supplied h5 file.')

        # Retrieve name of objective functions
        self.obj_name = opt.get_objective_name()

        # Retrieve name of constraints
        # [To be completed]

        # Retrieve available functions (observables etc)
        self.func_names =  opt.database.get_all_data_names()

        # Retrieve each function's history and save to internal data
        for func in self.func_names:
            func_hist = opt.database.get_complete_history([func])[0]
            self.data[func] = func_hist

        # Compute number of iterations
        self.numb_iter = int(self.data['Iter'][-1][0]) - 1

        # Find optimal solution
        self.opt_iter = self.__find_optimal_iter(opt)



    def __find_optimal_iter(self, opt):
        """
        Find the number of the optimal iteration.
        It's kinda strange, but I couldn't find a simple way to know this info. So here's a method:
        1) recover the optimal values of the design variables
        2) Compare the optimal values to thos of each variable until a match is found

        This method could be revised in the future if smarter options appear
        """

        # Recover design values at optimal point
        x_opti = opt.get_optimum()[1]

        # Check all iterations to find which one is optimum
        iter_opti = None
        for i in range(self.numb_iter+1):
            x_iter = opt.database.get_x_by_iter(i)
            comp = x_opti == x_iter

            if comp.all():
                iter_opti = i
                break

        # If none could be find, send warning
        if not iter_opti:
            raise IOError('[' + class_name + ']: Unable to recover the optimal iteration.')


        return iter_opti



    def keys(self):
        """
        Prints a list of the available keys to plot (typically the objective, constraints and all
        the OBSERVABLE specified by the USer in the problem definition)
        :return:
        """
        print('[' + class_name + ']: Available functions:')
        for func in self.func_names:
            print('\t' + func)

        input('Press ENTER to continue')



    def print_scalar(self, lst, it1=None, it2=None):
        """
        Print a comparison of a set of scalar quantities from 2 different iterations of an optimization
        history.
        :param lst: a list containing the scalar quantities to plot
        :param it1: First iteration to plot (if None, use iteration zero)
        :param it2: Second iteration to plot (if None, use the optimum)
        :return:
        """

        if not it1:
            # Plot first iteration
            it1 = 0

        if not it2:
            # Plot optimal iteration
            it2 = self.opt_iter


        print('')
        print('[' + class_name + '] Results:')
        print('')
        for func in lst:
            func1 = self.data[func][it1][0]
            func2 = self.data[func][it2][0]

            print(func + ':' )
            print('\t \t \t Iter %d: %.4f' % (it1, func1))
            print('\t \t \t Iter %d: %.4f' % (it2, func2))
            print('')



    def plot_opti_history(self, color=None):
        """
        Plots time history of the optimization metrics.
        For the time being, only the objective function and the constraints are plotted.
        [To be xtended with the design vars]
        :param color: a list containing the RGB color definition [[0.0, 0.25, 0.75]]
        :return:
        """

        # Plot objective function
        iters   = self.data['Iter']
        obj     = self.data[self.obj_name]


        # Color override (if necessary)
        color = [[0.0, 0.0, 0.55]]

        self.__simple_plot([(iters,obj)], ['ObjFun'], cmap =color,  xtag='Iter', ytag=self.obj_name)




    def plot_comparison(self, x_key='None', y_key='None', it1=None, it2=None):
        """
        Plot a comparison of two series of data coming from 2 different iterations of an optimization
        history.
        :param x_key: key/field of the quantity to plot in the X axis
        :param y_key: key/field of the quantity to plot in the Y axis
        :param it1: First iteration to plot (if None, use iteration zero)
        :param it2: Second iteration to plot (if None, use the optimum)
        :return:
        """

        if not it1:
            # Plot first iteration
            it1 = 0

        x_1 = self.data[x_key][it1][0]
        y_1 = self.data[y_key][it1][0]

        if not it2:
            # Plot optimal iteration
            it2 = self.opt_iter

        x_2 = self.data[x_key][it2][0]
        y_2 = self.data[y_key][it2][0]

        data_2_plot     =   [(x_1, y_1), (x_2,y_2)]
        labels          =   ['Iter' + str (it1), 'Iter' + str (it2)]

        self.__simple_plot(data_2_plot, labels, xtag=x_key, ytag=y_key )


    def get_iteration(self, it=None):
        """
        This function allows to send out a dictionary containing the value of all functins at a given
        iteration (if None is specified, the optimal is assumed). This can be useful, for example, to
        comapre different solutions coming from different post-processors
        :param it: Number of iteration to extract
        :return iter_data:
        """

        if not it:
            it = self.opt_iter

        it_data = {}

        for func in self.func_names:
            it_data[func] = self.data[func][self.opt_iter]

        return it_data


    def __simple_plot(self, data, labels, cmap=None, xtag='X Data', ytag='Y Data' ):
        """
        Just a general X,Y plot with some options to specify externally.
        Inputs are defined as lists to allow multiple plots to be compared
        :param data: list of tuples containing X,Y series to plot [(x1, y1),(x2,y2)...]
        :param labels: list of legend labels corresponding to each serie ['lab1','lab2'....]
        :param cmap: 2D array containing base colors for data series (if None, use internal map)
        :param xtag: Label of the X axis
        :param ytag: Label of the Y axis
        :return:
        """

        # Retrieve colors
        if cmap is None:
            cmap = self.colormap

        # Plot series
        fig, ax = plt.subplots()

        for i in range(len(data)):
            idat = data[i]
            ax.plot(idat[0], idat[1], color=cmap[i], linewidth=3.5, label=labels[i])

        ax.set_xlabel(xtag, fontsize=12)
        ax.set_ylabel(ytag, fontsize=12)
        plt.legend(loc='best')
        ax.grid()

        plt.show()




###################################################################################################
# CLASS TESTER
###################################################################################################
if __name__ == '__main__':

    # Identify h5 file
    h5file = './../runs/history_resource_allocation_MDO.h5'

    # Initialize postprocessor
    pp = GEMSEOPostProcess()

    # Load h5 file
    pp.init_from_h5_file(file=h5file)

    # get available keys to post-process
    pp.keys()

    # Extract dictionary of optimal iteration
    opt_dict = pp.get_iteration()

    # Plot time history of the objective function/constraints
    pp.plot_opti_history()




    # Compare scalar results for initial and optimal solutions
    scalarlst = ['N_pcs_const']

    pp.print_scalar(scalarlst, it1=None, it2=None)