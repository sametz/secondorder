"""
The main GUI for secondorder.
"""
from tkinter import *

import matplotlib
import numpy as np

from secondorder.GUI.frames import RadioFrame
from secondorder.GUI.toolbars import SecondOrderSpinBar

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
        self.controller = controller

        self.SideFrame = Frame(self, relief=RIDGE, borderwidth=3)
        self.SideFrame.pack(side=LEFT, expand=NO, fill=Y)

        self.TopFrame = Frame(self, relief=RIDGE, borderwidth=1)
        self.TopFrame.pack(side=TOP, expand=NO, fill=X)
        self.TopFrame.grid_rowconfigure(0, weight=1)
        self.TopFrame.grid_columnconfigure(0, weight=1)

        spinbar_kwargs = {'controller': self.controller,
                          'realtime': True}
        self.initialize_spinbars(**spinbar_kwargs)
        self.add_abc_buttons()
        self.add_plot()

    def initialize_spinbars(self, **kwargs):
        self.spin2 = SecondOrderSpinBar(self.TopFrame, n=2, **kwargs)
        self.spin3 = SecondOrderSpinBar(self.TopFrame, n=3, **kwargs)
        self.spin4 = SecondOrderSpinBar(self.TopFrame, n=4, **kwargs)
        self.spin5 = SecondOrderSpinBar(self.TopFrame, n=5, **kwargs)
        self.spin6 = SecondOrderSpinBar(self.TopFrame, n=6, **kwargs)
        self.spin7 = SecondOrderSpinBar(self.TopFrame, n=7, **kwargs)
        self.spin8 = SecondOrderSpinBar(self.TopFrame, n=8, **kwargs)

        self.currentbar = self.spin2
        self.currentbar.grid(sticky=W)

    def add_abc_buttons(self):
        """Populates ModelFrame with a RadioFrame for selecting the number of
                nuclei and the corresponding toolbar.
                """
        abc_buttons = (('2', lambda: self.select_toolbar(self.spin2)),
                       ('3', lambda: self.select_toolbar(self.spin3)),
                       ('4', lambda: self.select_toolbar(self.spin4)),
                       ('5', lambda: self.select_toolbar(self.spin5)),
                       ('6', lambda: self.select_toolbar(self.spin6)),
                       ('7', lambda: self.select_toolbar(self.spin7)),
                       ('8', lambda: self.select_toolbar(self.spin8)))
        self.ABC_Buttons = RadioFrame(self.SideFrame,
                                      buttons=abc_buttons,
                                      title='Number of Spins')
        self.ABC_Buttons.grid(row=0, column=0, sticky=N)

    def add_plot(self):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = MPLgraph(self.figure, self)
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)
        Button(self, text="clear", command=lambda: self.canvas.clear()).pack(
            side=BOTTOM)

    def select_toolbar(self, toolbar):
        """When called by a RadioButton, hides the old toolbar, shows the new
        toolbar, and requests that the plot be refreshed."

        :param toolbar: the toolbar (nSpinBar or AB_Bar object) that was
        selected by the RadioButton
        """
        self.currentbar.grid_remove()
        self.currentbar = toolbar
        self.currentbar.grid(sticky=W)

        try:
            self.currentbar.request_plot()
        except ValueError:
            print('No model yet for this bar')

    # The methods below provide the interface to the controller

    # To avoid a circular reference, a call to the Controller cannot be made
    # until View is fully instantiated. Initializing the plot with a call to
    # Controller is postponed by placing it in the following function and
    # having the Controller call it when the View is ready.
    def initialize(self):
        self.currentbar.request_plot()

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
