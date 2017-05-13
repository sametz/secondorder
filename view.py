import matplotlib as mpl
import numpy as np
import tkinter as tk

mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from tkinter import ttk


class MPLgraph(FigureCanvasTkAgg):
    """The canvas-like matplotlib object used to plot the model's function."""
    def __init__(self, figure, parent=None, **options):
        FigureCanvasTkAgg.__init__(self, figure, parent, **options)
        self.figure = figure
        self.add = figure.add_subplot(111)
        self.show()
        self.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, parent)
        self.toolbar.update()

    def plot(self, x, y):
        """Takes two arrays for x and y coordinates and plots the data."""
        self.add.plot(x, y)
        self.figure.canvas.draw()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        """Erases the plot."""
        self.add.clear()
        self.figure.canvas.draw()


class View(tk.Frame):

    def __init__(self, parent, controller, **options):
        tk.Frame.__init__(self, parent, **options)
        self.pack()

        self.parent = parent
        self.controller = controller

        # GUI entry values are stored in a {'name': float} dictionary.
        # The controller and the model use the same dict format.
        self.values = {}

        self.create_entries()
        self.create_bindings()
        self.create_canvas()

    def create_entries(self):

        self.base_entry = self.add_entry('base')
        self.base = tk.StringVar()
        self.base_entry.config(textvariable=self.base)
        self.base_entry.focus_set()

        self.exponent_entry = self.add_entry('exponent')
        self.exponent = tk.StringVar()
        self.exponent_entry.config(textvariable=self.exponent)

    def create_bindings(self):

        self.bind_class('TEntry', '<FocusIn>',
                        lambda event: self.on_focus_in(event))
        self.bind_class('TEntry', '<Return>',
                        lambda event: self.on_value_entry(event))
        self.bind_class('TEntry', '<Tab>', lambda event: self.on_tab(event))
        self.bind_class('TEntry', '<FocusOut>',
                        lambda event: self.refresh())

    def create_canvas(self):

        self.figure = mpl.figure.Figure(figsize=(5, 4), dpi=100)
        self.canvas = MPLgraph(self.figure, self.parent)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)

    def add_entry(self, text):

        ttk.Label(self, text=text).pack(side=tk.LEFT)
        # check on each keypress for numerical entry
        entry = ttk.Entry(self, validate='key')
        entry['validatecommand'] = (self.register(self.is_number_or_empty),
                                    '%P')
        entry['invalidcommand'] = 'bell'  # beep if invalid keypress
        entry.pack(side=tk.LEFT)
        return entry

    def is_number_or_empty(self, entry):
        """
        tests (e.g. on keypress) to see if entry status is acceptable (either 
        empty, or able to be converted to a float.)
        """
        return self.is_number(entry) or self.is_empty(entry)

    @staticmethod
    def is_number(entry):
        """tests (e.g. before calling model) to see if entry value is add 
        number.
        """
        try:
            float(entry)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_empty(entry):
        if not entry:
            return True
        return False

    def on_value_entry(self, event):
        """When a valid change to the entry is committed, updates the 
        dictionary of entry values, requests a plot refresh, and focuses on 
        next entry widget."""
        self.refresh()
        self.set_next_focus(event.widget.tk_focusNext())

    def refresh(self):
        """Overwrites dectionary and request plot refresh only if an entry's 
        value is changed."""
        if self.entry_is_changed():
            self.update_values()
            self.controller.update_view(self.values)
            # print('values are now: ', self.base.get(), self.exponent.get())

    def entry_is_changed(self):
        """Compares current widget entries to the dictionary of previously 
        stored values."""
        if self.current_values() != self.values:
            return True
        return False

    def current_values(self):
        """Gets current widget values and stores them in a dictionary."""
        return {'base': float(self.base.get()),
                'exponent': float(self.exponent.get())}

    def update_values(self):
        """Overwrites the dictionary of previous entry values with that for 
        the current values."""
        self.values = self.current_values()

    def set_next_focus(self, NextWidget):
        """Starting with NextWidget, traverses the order of widgets until it 
        finds the next Entry widget, then sets focus to it. Used to ignore all 
        the matplotlib widgets.
        """
        if type(NextWidget) is not ttk.Entry:
            self.set_next_focus(NextWidget.tk_focusNext())
        else:
            NextWidget.focus()

    def on_tab(self, event):
        """Required to override the Tab key's default behavior."""
        self.on_value_entry(event)
        return 'break'

    @staticmethod
    def on_focus_in(event):
        """Selects entire contents of entry widget with focus, for easy 
        editing.
        """
        event.widget.selection_range(0, tk.END)

    def set_values(self, values):
        """Used by the controller to initialize the view's entry values and 
        data.
        values: {'name': float} for default base and exponent values."""
        self.base.set(values['base'])
        self.exponent.set(values['exponent'])
        self.values = values

    def clear(self):
        self.canvas.clear()

    def plot(self, x, y):
        self.canvas.plot(x, y)




if __name__ == '__main__':
    root = tk.Tk()
    app = View(root, controller=None)
    root.mainloop()
