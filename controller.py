"""
The controller is to be executed as the main app in this MVC pattern. It 
calls on a model and a viewer and passes commands and data between them.

This demonstration assumes a tkinter view, and knowledge of its structure. It
might be a useful exercise to try and design a controller that accepts 
different GUIs, or even different models.
"""

import tkinter as tk
from view import View
from model import Model


class Controller:
    """ 
    A controller that requires Model() and View() objects with compatible 
    interfaces.
    
    
    """

    def __init__(self, root):
        """Controller must be instantiated with a tkinter.Tk() object (root).
        """
        self.model = Model()
        self.view = View(root, self)
        self.view.base.set('1')
        self.view.exponent.set('2')
        self.update_view()

    def update_view(self):
        self.update_view_data()
        self.get_model_data(self.integer, self.exponent)
        self.update_view_plot()

    def update_view_data(self):
        self.integer = float(self.view.base.get())
        self.exponent = float(self.view.exponent.get())

    def get_model_data(self, base, exponent):
        self.model_data = self.model.powerplot(base, exponent)

    def update_view_plot(self):
        self.view.canvas.clear()
        self.view.canvas.plot(*self.model_data)


if __name__ == '__main__':
    root = tk.Tk()
    app = Controller(root)
    root.mainloop()
