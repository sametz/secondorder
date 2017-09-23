"""In progress: excise view.py toolbars to here."""
import numpy as np
from secondorder.initialize import getWINDNMRdefault
from tkinter import *
from .widgets import VBox
from .frames import ArrayFrame


class SecondOrderBar(Frame):
    """
    A frame object similar to ToolBar that holds n frequency entry boxes, a 1-D
    array for frequencies, a 2-D array for coupling constants, and a button
    to pop up a window for entering J values as well as frequencies.
    Arguments:
        controller: controller object with a
        n: number of spins
    Dependencies:
        nmrmath.nspinspec
        initialize.getWINDNMRdefault for WINDNMR default values
        nmrplot.tkplot for displaying spectrum
    """

    def __init__(self, parent=None, controller=None, n=4, **options):
        Frame.__init__(self, parent, **options)
        self.controller = controller
        self.v_obj = np.zeros(n, dtype=object)
        self.v, self.j = getWINDNMRdefault(n)
        self.w_array = np.array([[0.5]])

        for freq in range(n):
            vbox = VBox(self, a=self.v, coord=(0, freq),
                            name='V' + str(freq + 1))
            self.v_obj[freq] = vbox
            vbox.pack(side=LEFT)

        wbox = VBox(self, a=self.w_array, coord=(0, 0), name="W")
        wbox.pack(side=LEFT)

        vj_button = Button(self, text="Enter Js",
                           command=lambda: self.vj_popup(n))
        vj_button.pack(side=LEFT, expand=N, fill=NONE)

    def vj_popup(self, n):
        tl = Toplevel()
        Label(tl, text='Second-Order Simulation').pack(side=TOP)
        datagrid = ArrayFrame(tl, self.request_plot, self.v_obj)

        # For gridlines, background set to the line color (e.g. 'black')
        datagrid.config(background='black')

        Label(datagrid, bg='gray90').grid(row=0, column=0, sticky=NSEW,
                                          padx=1, pady=1)
        for col in range(1, n + 1):
            Label(datagrid, text='V%d' % col, width=8, height=3,
                  bg='gray90').grid(
                row=0, column=col, sticky=NSEW, padx=1, pady=1)

        for row in range(1, n + 1):
            vtext = "V" + str(row)
            v = VBox(datagrid, a=self.v,
                         coord=(0, row - 1),  # V1 stored in v[0, 0], etc.
                         name=vtext, color='gray90')
            v.grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
            for col in range(1, n + 1):
                if col < row:
                    j = VBox(datagrid, a=self.j,
                                 # J12 stored in j[0, 1] (and j[1, 0]) etc
                                 coord=(col - 1, row - 1),
                                 name="J%d%d" % (col, row))
                    j.grid(row=row, column=col, sticky=NSEW, padx=1, pady=1)
                else:
                    Label(datagrid, bg='grey').grid(
                        row=row, column=col, sticky=NSEW, padx=1, pady=1)

        datagrid.pack()

    def request_plot(self):
        kwargs = {'v': self.v[0, :],
                  'j': self.j,
                  'w': self.w_array[0, 0]}
        # self.controller.update_view_plot(self.v[0, :], self.j,
        #                                  self.w_array[0, 0])
        self.controller.update_with_dict(**kwargs)
