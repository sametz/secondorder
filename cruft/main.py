"""
The main GUI, to be run as the main application.

TODO: implement line widths
"""
import matplotlib
import numpy as np

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg
# implement the default mpl key bindings
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
    Creates and packs radio button frames into parent.
    arguments:
    -buttons: a tuple of (text, function) tuples
    -title: an optional title to put above the button list
    """

    def __init__(self, parent=None, buttons=(), title='', **options):
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
    """

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack(side=TOP, anchor=N, expand=YES, fill=X)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.add_abc_buttons()
        self.active_bar_dict = {'abc': self.ab}
        self.currentframe = 'abc'
        self.currentbar = self.ab  # On program start, simulation set to ABq
        self.currentbar.grid(sticky=W)
        self.currentbar.call_model()

    def add_abc_buttons(self):
        """Populates the frame with a RadioFrame for selecting the number of 
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

        self.ab = AB_Bar(TopFrame)
        self.spin3 = nSpinBar(TopFrame, n=3)
        self.spin4 = nSpinBar(TopFrame, n=4)
        self.spin5 = nSpinBar(TopFrame, n=5)
        self.spin6 = nSpinBar(TopFrame, n=6)
        self.spin7 = nSpinBar(TopFrame, n=7)
        self.spin8 = nSpinBar(TopFrame, n=8)

    def select_toolbar(self, toolbar):
        self.currentbar.grid_remove()
        self.currentbar = toolbar
        self.currentbar.grid(sticky=W)
        # record current bar of currentframe:
        self.active_bar_dict[self.currentframe] = toolbar
        try:
            self.currentbar.call_model()
        except ValueError:
            print('No model yet for this bar')


class ToolBar(Frame):
    """
    A frame object that contains entry widgets, a dictionary of
    their current contents, and a function to call the appropriate model.
    """

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.vars = {}

    def call_model(self):
        print('Sending to dummy_model: ', self.vars)


class nSpinBar(Frame):
    """
    A frame object similar to ToolBar that holds n frequency entry boxes, a 1-D
    array for frequencies, a 2-D array for coupling constants, and a button
    to pop up
    Arguments:
        n: number of spins
    Dependencies:
        nmrmath.nspinspec
        initialize.getWINDNMRdefault for WINDNMR default values
        nmrplot.tkplot for displaying spectrum
    """

    def __init__(self, parent=None, n=4, **options):
        Frame.__init__(self, parent, **options)
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
        datagrid = ArrayFrame(tl, self.call_model, self.v_obj)

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

    def call_model(self):
        spectrum = nspinspec(self.v[0, :], self.j)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class VarBox(Frame):
    """
    Custom entry widget with a check for numerical input.
    Idea is to fill the VarFrame with these modules.
    Current version: checks that only numbers are entered; returns contents
    in a popup.
    Looking ahead: trick may be linking their contents with the calls to
    nmrmath. Also, need to make sure floats, not ints, are returned. Can
    change the is_number_or_empty routine so that if base entered, replaced with
    float?
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
            self.master.call_model()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        if self.entry_is_changed():
            self.to_dict()
            self.master.call_model()

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
            self.master.call_model()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        """Records change to entry, and calls model"""
        if self.entry_is_changed():
            self.to_dict()
            self.master.call_model()

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
    call_model requests up to the provided func, and passing changes to V
    entries to the toolbar.
    Arguments:
        func: the actual function the ArrayBox calls to refresh model.
        v.obj: the array of frequency ArrayBox widgets in the upper tool bar
    """

    def __init__(self, parent, func, v_obj, **options):
        Frame.__init__(self, parent, **options)
        self.call_model = func
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
            self.master.call_model()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        if self.entry_is_changed():
            self.to_array()
            self.master.call_model()

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

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab = VarBox(self, name='Jab', default=12.00)
        Vab = VarBox(self, name='Vab', default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = AB(_Jab, _Vab, _Vcentr)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


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


# Create the main application window:
root = Tk()
root.title('secondorder')  # working title only!

# Create the basic GUI structure: sidebar, topbar, and display area
# First, pack a sidebar frame to contain widgets
sideFrame = Frame(root, relief=RIDGE, borderwidth=3)
sideFrame.pack(side=LEFT, expand=NO, fill=Y)

# Next, pack the top frame where function variables will be entered
TopFrame = Frame(root, relief=RIDGE, borderwidth=1)
TopFrame.pack(side=TOP, expand=NO, fill=X)
TopFrame.grid_rowconfigure(0, weight=1)
TopFrame.grid_columnconfigure(0, weight=1)

# Remaining lower right area will be for a Canvas or matplotlib spectrum frame
# Because we want the spectrum clipped first, will pack it last
f = Figure(figsize=(5, 4), dpi=100)
canvas = MPLgraph(f, root)

# Create sidebar widget:
Models = ModelFrame(sideFrame, relief=SUNKEN, borderwidth=1)
Models.pack(side=TOP, expand=YES, fill=X, anchor=N)

# Now we can pack the canvas (want it to be clipped first)
canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

Button(root, text="clear", command=lambda: canvas.clear()).pack(side=BOTTOM)

# workaround fix for Tk problems and mac mouse/trackpad:
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass