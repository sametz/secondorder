"""
The main GUI for secondorder.
"""
from tkinter import *

import matplotlib
import numpy as np

from secondorder.GUI.frames import ModelFrame, RadioFrame

matplotlib.use("TkAgg")  # must be invoked before the imports below
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.figure import Figure


class MPLgraph(FigureCanvasTkAgg):
    def __init__(self, figure, master=None, **options):
        FigureCanvasTkAgg.__init__(self, figure, master, **options)
        self.f = figure
        self.add = figure.add_subplot(111)
        self.add.invert_xaxis()
        self.show()
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        self.toolbar.update()

    def plot(self, x, y):
        self.add.plot(x, y)
        # apparently .draw_idle() gives faster refresh than .draw()
        self.f.canvas.draw_idle()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        self.add.clear()
        self.f.canvas.draw()


class View(Frame):
    def __init__(self, parent, controller, **options):
        Frame.__init__(self, parent, **options)
        self.parent = parent  # is this needed?
        self.controller = controller

        # If only Models gets packed in sideFrame, sideFrame may not be needed.
        # Keeping for now in case other widgets get added.
        sideFrame = Frame(self, relief=RIDGE, borderwidth=3)
        sideFrame.pack(side=LEFT, expand=NO, fill=Y)

        TopFrame = Frame(self, relief=RIDGE, borderwidth=1)
        TopFrame.pack(side=TOP, expand=NO, fill=X)
        TopFrame.grid_rowconfigure(0, weight=1)
        TopFrame.grid_columnconfigure(0, weight=1)

        self.Models = ModelFrame(parent=sideFrame,
                                 controller=self.controller,
                                 toolframe=TopFrame,
                                 relief=SUNKEN, borderwidth=1)
        self.Models.pack(side=TOP, expand=YES, fill=X, anchor=N)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = MPLgraph(self.figure, self)
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)
        Button(self, text="clear", command=lambda: self.canvas.clear()).pack(
            side=BOTTOM)

    # The methods below provide the interface to the controller

    # To avoid a circular reference, a call to the Controller cannot be made
    # until View is fully instantiated. Initializing the plot with a call to
    # Controller is postponed by placing it in the following function and
    # having the Controller call it when the View is ready.
    def initialize(self):
        self.Models.currentbar.request_plot()

    def clear(self):
        """ Erase the matplotlib canvas."""
        self.canvas.clear()

    def plot(self, x, y):
        """Plot the model's results to the matplotlib canvas.

        Arguments:
            x, y: numpy arrays of x and y coordinates
        """
        self.canvas.plot(x, y)


if __name__ == '__main__':
    # Create the main application window:
    from secondorder.controller import controller

    root = Tk()
    root.title('secondorder')  # working title only!
    Controller = controller.Controller(root)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass
