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

        self.values = {}

        ttk.Label(self, text="base").pack(side=tk.LEFT)
        # check on each keypress if new result will be a number
        self.base_entry = ttk.Entry(self, validate='key')
        self.base_entry['validatecommand'] = (self.register(self.is_number_or_empty),
                                              '%P')
        # sound 'bell' if bad keypress
        self.base_entry['invalidcommand'] = 'bell'
        # self.base_entry.bind('<Return>', lambda event: self.on_return(event))
        # self.base_entry.bind('<Tab>', lambda event: self.on_tab(event))
        # self.base_entry.bind('<FocusOut>', lambda event: self.on_focus_out())
        self.base_entry.pack(side=tk.LEFT)
        self.base_entry.focus_set()

        ttk.Label(self, text="exponent").pack(side=tk.LEFT)
        self.exponent_entry = ttk.Entry(self, validate='key')
        self.exponent_entry['validatecommand'] = (self.register(
            self.is_number_or_empty), '%P')
        self.exponent_entry['invalidcommand'] = 'bell'
        # self.exponent_entry.bind('<Return>',
        #                          lambda event: self.on_return(event))
        # self.exponent_entry.bind('<Tab>',
        #                          lambda event: self.on_tab(event))
        # self.exponent_entry.bind('<FocusOut>',
        #                          lambda event: self.on_focus_out())
        self.exponent_entry.pack(side=tk.LEFT)

        self.bind_class('TEntry', '<FocusIn>',
                        lambda event: self.on_focus_in(event))
        self.bind_class('TEntry', '<Return>',
                        lambda event: self.on_return(event))
        self.bind_class('TEntry', '<Tab>', lambda event: self.on_tab(event))
        self.bind_class('TEntry', '<FocusOut>',
                        lambda event: self.on_focus_out())

        self.base = tk.StringVar()
        self.base_entry.config(textvariable=self.base)

        self.exponent = tk.StringVar()
        self.exponent_entry.config(textvariable=self.exponent)

        self.f = mpl.figure.Figure(figsize=(5, 4), dpi=100)
        self.canvas = MPLgraph(self.f, parent)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)

    def set_values(self, base, exponent):
        """Used by the controller to initialize the view's entry values and 
        data"""
        self.base.set(base)
        self.exponent.set(exponent)
        self.values['base'] = float(base)
        self.values['exponent'] = float(exponent)

    def update_values(self):
        self.values = self.current_values()

    @staticmethod
    def is_number_or_empty(entry):
        """
        tests (e.g. on keypress) to see if entry status is acceptable (either 
        empty, or able to be converted to a float.)
        """
        if not entry:
            return True  # allows previous entry to be overwritten
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def is_number(self):
        """tests (e.g. before calling model) to see if entry value is a 
        number.
        """
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def current_values(self):
        return {'base': float(self.base.get()),
                'exponent': float(self.exponent.get())}

    def entry_is_changed(self):
        if self.current_values() != self.values:
            return True
        return False

    def on_return(self, event):
        if self.entry_is_changed():
            self.update_values()
            self.controller.update_view()
            print('values are now: ', self.base.get(), self.exponent.get())
        #event.widget.tk_focusNext().focus()
        self.set_next_focus(event.widget.tk_focusNext())

    def set_next_focus(self, NextWidget):
        print(type(NextWidget))
        if type(NextWidget) is not ttk.Entry:
            self.set_next_focus(NextWidget.tk_focusNext())
        else:
            NextWidget.focus()

    def on_tab(self, event):
        self.on_return(event)
        return 'break'

    def on_focus_out(self):
        if self.entry_is_changed():
            self.update_values()
            self.controller.update_view()
            print('values are now: ', self.base.get(), self.exponent.get())

    def on_focus_in(self, event):
        event.widget.selection_range(0, tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = View(root, controller=None)
    root.mainloop()
