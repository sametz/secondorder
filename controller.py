"""
The controller is to be executed as the main app in this MVC pattern. It 
calls on a model and a viewer and passes commands and data between them.

This demonstration assumes a tkinter view, and knowledge of its structure. It
might be a useful exercise to try and design a controller that accepts 
different GUIs, or even different models.
"""

import tkinter as tk
from view import View
import model


class Controller:
    """ 
    A controller that requires Model() and View() objects with compatible 
    interfaces.
    """

    def __init__(self, root):
        """Controller must be instantiated with a tkinter.Tk() object.
        """
        self.view = View(root, self)
        self.default_values = {'base': 1, 'exponent': 2}
        self.initialize_view()

    def initialize_view(self):
        self.view.set_values(self.default_values)
        self.update_view(self.default_values)

    def update_view(self, values):
        """"""
        self.get_plot_data(values)
        self.update_view_plot()

    def get_plot_data(self, values):
        self.plot_data = model.powerplot(**values)

    def update_view_plot(self):
        self.view.canvas.clear()
        self.view.canvas.plot(*self.plot_data)


if __name__ == '__main__':
    root = tk.Tk()
    app = Controller(root)
    root.mainloop()
