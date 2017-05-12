import matplotlib as mpl
import numpy as np
import tkinter as tk

mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from tkinter import ttk


class MPLgraph(FigureCanvasTkAgg):
    def __init__(self, f, master=None, **options):
        FigureCanvasTkAgg.__init__(self, f, master, **options)
        self.f = f
        self.a = f.add_subplot(111)
        # self.a.invert_xaxis()
        self.show()
        self.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        self.toolbar.update()

    def plot(self, x, y):
        self.a.plot(x, y)
        self.f.canvas.draw()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        self.a.clear()
        self.f.canvas.draw()


class View(tk.Frame):

    def __init__(self, parent, controller, **options):
        tk.Frame.__init__(self, parent, **options)
        self.pack()

        self.controller = controller

        ttk.Label(self, text="base").pack(side=tk.LEFT)
        self.integer_entry = ttk.Entry(self, validate='key')
        self.integer_entry.pack(side=tk.LEFT)
        ttk.Label(self, text="exponent").pack(side=tk.LEFT)
        self.exponent_entry = ttk.Entry(self, validate='key')
        self.exponent_entry.pack(side=tk.LEFT)

        self.integer = tk.StringVar()
        self.exponent = tk.StringVar()
        self.integer_entry.config(textvariable=self.integer)
        self.exponent_entry.config(textvariable=self.exponent)
        self.integer_entry.focus_set()

        self.integer_entry.bind('<Return>', lambda event: self.on_return(event))
        self.integer_entry.bind('<Tab>', lambda event: self.on_tab())
        self.integer_entry.bind('<FocusOut>', lambda event: self.on_tab())
        self.exponent_entry.bind('<Return>',
                                 lambda event: self.on_return(event))
        self.exponent_entry.bind('<Tab>', lambda event: self.on_tab())
        self.exponent_entry.bind('<FocusOut>', lambda event: self.on_tab())

        # check on each keypress if new result will be a number
        self.integer_entry['validatecommand'] = (self.register(self.is_number),
                                             '%P')
        self.exponent_entry['validatecommand'] = (self.register(
            self.is_number), '%P')
        # sound 'bell' if bad keypress
        self.integer_entry['invalidcommand'] = 'bell'
        self.exponent_entry['invalidcommand'] = 'bell'

        self.f = mpl.figure.Figure(figsize=(5, 4), dpi=100)
        self.canvas = MPLgraph(self.f, parent)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to a float.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def entry_is_changed(self):
        return True  # placeholder

    def on_return(self, event):
        if self.entry_is_changed():
            self.controller.update_view()
            print('values are now: ', self.integer.get(), self.exponent.get())
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        if self.entry_is_changed():
            self.controller.update_view()
            print('values are now: ', self.integer.get(), self.exponent.get())


if __name__ == '__main__':
    root = tk.Tk()
    app = View(root, controller=None)
    root.mainloop()
