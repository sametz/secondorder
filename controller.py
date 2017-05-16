import tkinter as tk
from secondorder.model.nmrmath import AB, nspinspec
from secondorder.model.nmrplot import tkplot
from view import View


class Controller:

    def __init__(self, root):
        self.view = View(root, self)
        self.view.pack(expand=tk.YES, fill=tk.BOTH)

    def update_view_plot(self, simulation, data):
        """Queries the model for a simulation using data, then tells the view
        to plot the results.

        Arguments:
            simulation: 'AB' (non-quantum mechanical AB quartet calculation
                        for 2 spins), or
                        'QM' (quantum-mechanical treatment for >= 3 spins)
            data: //
        """
        if simulation == 'AB':
            plotdata = tkplot(AB(data))
            View.clear()
            View.plot(plotdata)
        elif simulation == 'QM':
            plotdata = tkplot(nspinspec(data))
            View.clear()
            View.plot(plotdata)
        else:
            print('Simulation not recognized.')

if __name__ == '__main__':
    print('start')
    root = tk.Tk()
    print('end')

    root.title('secondorder')  # working title only!
    app = Controller(root)

    root.mainloop()