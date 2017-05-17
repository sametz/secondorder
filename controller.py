"""
The controller can be executed as the main secondorder app. 

Assumes a tkinter view.

Contains:

* Controller    Class that handles data and requests to/from the model and 
                the view.
"""
import tkinter as tk
from secondorder.model.nmrmath import AB, nspinspec
from secondorder.model.nmrplot import tkplot
from view import View


class Controller:
    """Instantiates secondorder's view, and passes data and requests to/from 
    the model and the view.
    
    The controller assumes the view offers the following methods:
    
    * initialize()--Initializes the view. Currrently, just "OKs" the View 
    to call Controller.update_view_plot after view's instantiation. 
    
    * clear()--clears the view's plot.
    
    * plot(x, y)--accept a tuple of x, y numpy arrays and plot the data.
    
    The controller provides the following methods:
    
    * update_view_plot: accepts a tuple of simulation name (string) and 
    variables; calls the appropriate model simulation with the variables; 
    and tells the view to plot the data the model returns.
    """
    def __init__(self, root):
        """Instantiates the view as a child of root, and then initializes it.
        
        Argument:
            root: a tkinter.Tk() object
        """

        self.view = View(root, self)
        self.view.pack(expand=tk.YES, fill=tk.BOTH)
        self.view.initialize()

    def update_view_plot(self, simulation, data):
        """Queries the model for a simulation using data, then tells the view
        to plot the results.

        Arguments:
            simulation: 'AB' (non-quantum mechanical AB quartet calculation
                        for 2 spins), or
                        'QM' (quantum-mechanical treatment for >= 3 spins)
            data: for now assumes the View sends data of the exact type and 
            format required by the model. This may not be proper MVC 
            separation of concerns, however.
        """
        if simulation == 'AB':
            plotdata = tkplot(AB(*data))
            self.view.clear()
            self.view.plot(*plotdata)
        elif simulation == 'QM':
            plotdata = tkplot(nspinspec(*data))
            self.view.clear()
            self.view.plot(*plotdata)
        else:
            print('Simulation not recognized.')

if __name__ == '__main__':
    root = tk.Tk()
    root.title('secondorder')  # working title only!
    app = Controller(root)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass
