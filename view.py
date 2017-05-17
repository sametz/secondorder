"""
The main GUI, to be run as the main application.

TODO: WINDNMR defaults should probably be passed from Controller via
View.initialize()

TODO: implement line widths
"""
import matplotlib
import numpy as np

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg

from matplotlib.figure import Figure
from secondorder.model.nmrplot import tkplot
from secondorder.initialize import getWINDNMRdefault
from tkinter import *
from secondorder.model.nmrmath import AB, nspinspec

up_arrow = u"\u21e7"
down_arrow = u"\u21e9"
left_arrow = u"\u21e6"
right_arrow = u"\u21e8"


class RadioFrame(Frame):
    """
    A frame containing a radio button menu and optional title.

    TODO: since this is a class with only an __init__, this should possibly
    be a function and not a class. Refactor?
    """

    def __init__(self, parent=None, buttons=(), title='', **options):
        """arguments:
        buttons: a tuple of (text, function) tuples
        title: an optional title to put above the button list"""
        Frame.__init__(self, parent, **options)
        Label(self, text=title).pack(side=TOP)
        self.var = StringVar()
        for button in buttons:
            Radiobutton(self, text=button[0], command=button[1],
                        variable=self.var,
                        value=button[0]).pack(anchor=NW)
        self.var.set(buttons[0][0])  # turns the top button on


class ModelFrame(Frame):
    """
    Creates a frame that stores and manages the button menu for selecting the
    number of nuclei.

    TODO: Maybe this also doesn't need to be a class, but less clear. It "is
    a " frame that "has a" dict, few constants, an __init__, and one function.
    """

    def __init__(self, parent, controller, toolframe, **options):
        """

        :param parent: parent widget
        :param controller: the View's controller
        :param toolframe: the frame that the toolbars (selected by the radio
        buttons) will be packed into
        """
        Frame.__init__(self, parent, **options)
        self.pack(side=TOP, anchor=N, expand=YES, fill=X)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.controller = controller
        self.toolframe = toolframe
        self.add_abc_buttons()

        self.currentbar = self.ab  # On program start, simulation set to ABq
        self.currentbar.grid(sticky=W)

    def add_abc_buttons(self):
        """Populates ModelFrame with a RadioFrame for selecting the number of
        nuclei and the corresponding toolbar.
        """
        abc_buttons = (('2', lambda: self.select_toolbar(self.ab)),
                       ('3', lambda: self.select_toolbar(self.spin3)),
                       ('4', lambda: self.select_toolbar(self.spin4)),
                       ('5', lambda: self.select_toolbar(self.spin5)),
                       ('6', lambda: self.select_toolbar(self.spin6)),
                       ('7', lambda: self.select_toolbar(self.spin7)),
                       ('8', lambda: self.select_toolbar(self.spin8)))
        self.ABC_Buttons = RadioFrame(self,
                                      buttons=abc_buttons,
                                      title='Number of Spins')
        self.ABC_Buttons.grid(row=0, column=0, sticky=N)

        self.ab = AB_Bar(self.toolframe, controller=self.controller)
        self.spin3 = nSpinBar(self.toolframe, controller=self.controller, n=3)
        self.spin4 = nSpinBar(self.toolframe, controller=self.controller, n=4)
        self.spin5 = nSpinBar(self.toolframe, controller=self.controller, n=5)
        self.spin6 = nSpinBar(self.toolframe, controller=self.controller, n=6)
        self.spin7 = nSpinBar(self.toolframe, controller=self.controller, n=7)
        self.spin8 = nSpinBar(self.toolframe, controller=self.controller, n=8)

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


class ToolBar(Frame):
    """
    A frame object that contains entry widgets, a dictionary of
    their current contents, and a function to call the controller for an update
    """

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.vars = {}

    def request_plot(self):
        """Any class inheriting from ToolBar needs to redefine this function.
        TODO: believe there is a Python mechanism to force a required 
        function to be defined in children. Consider implementing if true."""
        print('Sending to dummy_model: ', self.vars)


class nSpinBar(Frame):
    """
    A frame object similar to ToolBar that holds n frequency entry boxes, a 1-D
    array for frequencies, a 2-D array for coupling constants, and a button
    to pop up
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
        for freq in range(n):
            vbox = ArrayBox(self, a=self.v, coord=(0, freq),
                            name='V' + str(freq + 1))
            self.v_obj[freq] = vbox
            vbox.pack(side=LEFT)
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
            v = ArrayBox(datagrid, a=self.v,
                         coord=(0, row - 1),  # V1 stored in v[0, 0], etc.
                         name=vtext, color='gray90')
            v.grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
            for col in range(1, n + 1):
                if col < row:
                    j = ArrayBox(datagrid, a=self.j,
                                 # J12 stored in j[0, 1] (and j[1, 0]) etc
                                 coord=(col - 1, row - 1),
                                 name="J%d%d" % (col, row))
                    j.grid(row=row, column=col, sticky=NSEW, padx=1, pady=1)
                else:
                    Label(datagrid, bg='grey').grid(
                        row=row, column=col, sticky=NSEW, padx=1, pady=1)

        datagrid.pack()

    def request_plot(self):
        self.controller.update_view_plot('QM', (self.v[0, :], self.j))


class VarBox(Frame):
    """
    Custom entry widget with a check for numerical input.
    Idea is to fill the VarFrame with these modules.
    Current version: checks that only numbers are entered; returns contents
    in a popup.
    Looking ahead: trick may be linking their contents with the calls to
    nmrmath. Also, need to make sure floats, not ints, are returned. Can
    change the is_number_or_empty routine so that if base entered, replaced
    with float?
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """

    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

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
        return self.master.vars[self.widgetName] != float(self.value.get())

    def on_return(self, event):
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()

    def to_dict(self):
        """
        Records widget's contents to the container's dictionary of
        values, filling the entry with 0.00 if it was empty.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())


class VarButtonBox(Frame):
    """
    A deluxe VarBox that is closer to WINDNMR-style entry boxes.
    ent = entry that holds the value used for calculations
    increment = the amount added to or subtracted from ent by the buttons
    minus and plus buttons subtract/add once;
    up and down buttons repeat as long as button held down.
    Arguments:
    -text: appears above the entry box
    -default: default value in entry
    """

    # To do: use inheritance to avoid repeating code for different widgets
    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP)

        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        # To-Do: consistent routines for VarBox, VarButtonBox, ArrayBox etc.
        # e.g. rename on_tab for general purpose on focus-out
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

        # Create a grid for buttons and increment
        minus_plus_up = Frame(self)
        minus_plus_up.rowconfigure(0, minsize=30)  # make 2 rows ~same height
        minus_plus_up.columnconfigure(2, weight=1)  # lets arrow buttons fill
        minus_plus_up.pack(side=TOP, expand=Y, fill=X)

        minus = Button(minus_plus_up, text='-',
                       command=lambda: self.decrease())
        plus = Button(minus_plus_up, text='+',
                      command=lambda: self.increase())
        up = Button(minus_plus_up, text=up_arrow, command=lambda: None)
        up.bind('<Button-1>', lambda event: self.zoom_up())
        up.bind('<ButtonRelease-1>', lambda event: self.stop_action())

        self.mouse1 = False  # Flag used to check if left button held down

        minus.grid(row=0, column=0, sticky=NSEW)
        plus.grid(row=0, column=1, sticky=NSEW)
        up.grid(row=0, column=2, sticky=NSEW)

        # Increment is also limited to numerical entry
        increment = Entry(minus_plus_up, width=4, validate='key')
        increment.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        self.inc = StringVar()
        increment.config(textvariable=self.inc)
        self.inc.set(str(1))  # 1 replaced by argument later?
        increment['validatecommand'] = (self.register(self.is_number), '%P')
        increment['invalidcommand'] = 'bell'

        down = Button(minus_plus_up, text=down_arrow, command=lambda: None)
        down.grid(row=1, column=2, sticky=NSEW)
        down.bind('<Button-1>', lambda event: self.zoom_down())
        down.bind('<ButtonRelease-1>', lambda event: self.stop_action())

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
        """True if current entry doesn't match stored entry"""
        return self.master.vars[self.widgetName] != float(self.value.get())

    def on_return(self, event):
        """Records change to entry, calls model, and focuses on next widget"""
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        """Records change to entry, and calls model"""
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()

    def to_dict(self):
        """
        Records widget's contents to the container's dictionary of
        values, filling the entry with 0.00 if it was empty.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())

    def stop_action(self):
        """ButtonRelease esets self.mouse1 flag to False"""
        self.mouse1 = False

    def increase(self):
        """Increases ent by inc"""
        current = float(self.value.get())
        increment = float(self.inc.get())
        self.value.set(str(current + increment))
        self.on_tab()

    def decrease(self):
        """Decreases ent by inc"""
        current = float(self.value.get())
        decrement = float(self.inc.get())
        self.value.set(str(current - decrement))
        self.on_tab()

    def zoom_up(self):
        """Increases ent by int as long as button-1 held down"""
        increment = float(self.inc.get())
        self.mouse1 = True
        self.change_value(increment)

    def zoom_down(self):
        """Decreases ent by int as long as button-1 held down"""
        decrement = - float(self.inc.get())
        self.mouse1 = True
        self.change_value(decrement)

    def change_value(self, increment):
        """Adds increment to the value in ent"""
        if self.mouse1:
            self.value.set(str(float(self.value.get()) + increment))
            self.on_tab()  # store value, call model

            # Delay is set to 10, but really depends on model call time
            self.after(10, lambda: self.change_value(increment))


class ArrayFrame(Frame):
    """
    A frame used for holding a grid of ArrayBox entries, passing their
    request_plot requests up to the provided func, and passing changes to V
    entries to the toolbar.
    Arguments:
        func: the actual function the ArrayBox calls to refresh model.
        v.obj: the array of frequency ArrayBox widgets in the upper tool bar
    """

    def __init__(self, parent, func, v_obj, **options):
        Frame.__init__(self, parent, **options)
        self.request_plot = func
        self.v_obj = v_obj


class ArrayBox(Frame):
    """
    A version of VarBox that will save its entry to an array. It will be
    initialized with the provided array, so e.g. if n-spin models are being
    initalized with WINDNMR default values, the nSpinBar should be
    initialized with V and J arrays containing default values.
    Arguments:
        name-- for widget label
        a-- array of values. Mutable will be changed by this widget!
        coord-- a (row, column) tuple for coordinate of a to store data to.
    """

    # noinspection PyDefaultArgument
    def __init__(self, parent=None, a=[], coord=(0, 0), name='', color='white',
                 **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=0,
                       background=color, **options)
        Label(self, text=name, bg=color, bd=0).pack(side=TOP)
        self.widgetName = name

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)

        self.a = a
        self.row, self.col = coord
        self.value.set(str(a[self.row, self.col]))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())
        ent.bind('<FocusOut>', lambda event: self.on_tab())

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

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
        return self.a[self.row, self.col] != float(self.value.get())

    def on_return(self, event):
        if self.entry_is_changed():
            self.to_array()
            self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        if self.entry_is_changed():
            self.to_array()
            self.master.request_plot()

    def to_array(self):
        """
        Records widget's status to the array, filling the entry with
        0.00 if it was empty.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        value = float(self.value.get())
        self.a[self.row, self.col] = value
        if self.a.shape[0] > 1:  # if more than one row, assume J matrix
            self.a[self.col, self.row] = value  # fill cross-diagonal element
        else:  # otherwise, assume value is a V
            print(self.master.v_obj[self.col])
            self.master.v_obj[self.col].value.set(value)


class AB_Bar(ToolBar):
    """
    Creates a bar of AB quartet inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AB
    """

    def __init__(self, parent, controller, **options):
        ToolBar.__init__(self, parent, **options)
        self.controller = controller
        Jab = VarBox(self, name='Jab', default=12.00)
        Vab = VarBox(self, name='Vab', default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def request_plot(self):
        pass
        _Jab = self.vars['Jab']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        self.controller.update_view_plot('AB', (_Jab, _Vab, _Vcentr))
        # x, y = tkplot(spectrum)
        # canvas.clear()
        # canvas.plot(x, y)


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
        self.f.canvas.draw()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        self.add.clear()
        self.f.canvas.draw()


class View(Frame):
    def __init__(self, parent, controller, **options):
        Frame.__init__(self, parent, **options)
        self.parent = parent
        self.controller = controller

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
        Label(sideFrame, text='placeholder').pack()
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
    import controller
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
