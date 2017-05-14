"""
view.View is A tkinter GUI with two entry boxes that accept numbers (labeled 
"base" and "exponent") and a matplotlib canvas. The interface to the 
controller is provided by the methods .set_values, .clear, and .plot, 
which allow View's entry values and matplotlib plot to be updated.

TODO: The view currently allows the controller to be called when widgets are 
left empty, which results in a ValueError when the model is called. A 
workaround such as filling empty entry widgets with 0. is required.
"""

import matplotlib as mpl
import numpy as np
import tkinter as tk

mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from tkinter import ttk


class MPLgraph(FigureCanvasTkAgg):
    """The canvas-like matplotlib object used by view.View."""
    def __init__(self, figure, parent=None, **options):
        """Requires argument:
        figure: a matplotlib.figure.Figure object
        """
        FigureCanvasTkAgg.__init__(self, figure, parent, **options)
        self.figure = figure
        self.add = figure.add_subplot(111)
        self.show()
        self.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, parent)
        self.toolbar.update()

    def plot(self, x, y):
        """Take two arrays for x and y coordinates and plot the data."""
        self.add.plot(x, y)
        self.figure.canvas.draw()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        """Erase the plot."""
        self.add.clear()
        self.figure.canvas.draw()


class View(tk.Frame):
    """A tkinter GUI with two entry boxes that accept numbers (labeled 
    "base" and "exponent") and a matplotlib canvas. The interface to the 
    controller is provided by the methods .set_values, .clear, and .plot, 
    which allow View's entry values and matplotlib plot to be updated.
    
    TODO: The view currently allows the controller to be called when widgets are 
    left empty, which results in a ValueError when the model is called. A 
    workaround such as filling empty entry widgets with 0. is required.
    """
    def __init__(self, parent, controller, **options):
        """Create the necessary widgets, and dict self.values for 
        storing the state of the entry widgets in the format:
            {'base': b, 'exponent': e}
        where b and e are floats.
        
        Requires arguments:
        parent: parent widget
        controller: a controller object that provides a .update_view method, 
        which accepts self.values as an argument.
        """
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

    def add_entry(self, text):
        """Create a label with text=text, and an entry with numerical entry 
        validation; pack them; and return the entry object for future 
        reference.
        """
        ttk.Label(self, text=text).pack(side=tk.LEFT)

        # check on each keypress for numerical entry
        entry = ttk.Entry(self, validate='key')
        entry['validatecommand'] = (self.register(self.is_number_or_empty),
                                    '%P')
        entry['invalidcommand'] = 'bell'  # beep if invalid keypress
        entry.pack(side=tk.LEFT)
        return entry

    def is_number_or_empty(self, entry):
        """Test (e.g. on keypress) to see if entry status is acceptable (either 
        empty, or able to be converted to a float.)
        """
        return self.is_number(entry) or self.is_empty(entry)

    @staticmethod
    def is_number(entry):
        """Test to see if entry value is a number."""
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

    def create_bindings(self):
        self.bind_class('TEntry', '<FocusIn>',
                        lambda event: self.on_focus_in(event))
        self.bind_class('TEntry', '<Return>',
                        lambda event: self.on_value_entry(event))
        self.bind_class('TEntry', '<Tab>', lambda event: self.on_tab(event))
        self.bind_class('TEntry', '<FocusOut>',
                        lambda event: self.refresh(event))

    @staticmethod
    def on_focus_in(event):
        """Select the entire contents of entry widget with focus, for easy 
        editing.
        """
        event.widget.selection_range(0, tk.END)

    def on_value_entry(self, event):
        """When a valid change to the entry is committed, update the 
        dictionary of entry values, request a plot refresh, and set focus on 
        next entry widget."""
        self.refresh(event)
        self.set_next_focus(event.widget.tk_focusNext())

    def refresh(self, event):
        """Overwrite dictionary and request plot refresh, but only if an 
        entry's value is changed.
        """
        if self.entry_is_changed():
            self.update_values()
            self.controller.update_view(self.values)
            # print('values are now: ', self.base.get(), self.exponent.get())

    def entry_is_changed(self):
        """Compare current widget entries to the dictionary of previously 
        stored values.
        """
        if self.current_values() != self.values:
            return True
        return False

    def current_values(self):
        """Get current widget values and store them in a dictionary."""
        return {'base': float(self.base.get()),
                'exponent': float(self.exponent.get())}

    def update_values(self):
        """Overwrite the dictionary of previous entry values with that for 
        the current values."""
        self.values = self.current_values()

    def set_next_focus(self, NextWidget):
        """Starting with NextWidget, traverse the order of widgets until the 
        next Entry widget is found, then set focus to it. Used to ignore all 
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

    def create_canvas(self):
        self.figure = mpl.figure.Figure(figsize=(5, 4), dpi=100)
        self.canvas = MPLgraph(self.figure, self.parent)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)

    ### The three methods below provide the interface to the controller
    def set_values(self, values):
        """Used by the controller to initialize the view's entry values and 
        data.
        values: {'name': float} for default base and exponent values."""
        self.base.set(values['base'])
        self.exponent.set(values['exponent'])
        self.values = values

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
    root = tk.Tk()
    app = View(root, controller=None)
    root.mainloop()
