"""
The main GUI, to be run as the main application.
"""
import matplotlib
import numpy as np
import tkinter as tk

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from secondorder.model.nmrplot import tkplot, dnmrplot_2spin, dnmrplot_AB
from secondorder.initialize import getWINDNMRdefault
#from tkinter import *
from secondorder.GUI.guimixin import GuiMixin  # mix-in class that provides dev
# tools
from secondorder.model.nmrmath import AB, AB2, ABX, ABX3, AAXX, first_order, \
    AABB
from secondorder.model.nmrmath import nspinspec
from collections import deque

up_arrow = u"\u21e7"
down_arrow = u"\u21e9"
left_arrow = u"\u21e6"
right_arrow = u"\u21e8"


class RadioFrame(tk.Frame):
    """
    Creates and packs radio button frames into parent.
    arguments:
    -buttons: add tuple of (text, function) tuples
    -title: an optional title to put above the button list
    """

    def __init__(self, parent=None, buttons=(), title='', **options):
        tk.Frame.__init__(self, parent, **options)
        tk.Label(self, text=title).pack(side=tk.TOP)
        self.var =tk.StringVar()
        for button in buttons:
            tk.Radiobutton(self, text=button[0], command=button[1],
                        variable=self.var,
                        value=button[0]).pack(anchor=tk.NW)
        self.var.set(buttons[0][0])  # turns the top button on


# noinspection PyUnusedLocal
class CalcTypeFrame(GuiMixin, RadioFrame):
    """ Defines the Calc Type button frame for the upper left corner"""

    def __init__(self, parent=None, **options):
        title = 'Calc Type'
        buttons = (('Multiplet',
                    lambda: Models.select_frame('multiplet')),
                   ('ABC...',
                    lambda: Models.select_frame('abc')),
                   ('DNMR', lambda: Models.select_frame('dnmr')),
                   ('Custom', lambda: Models.select_frame('custom')))
        RadioFrame.__init__(self, parent, buttons=buttons, title=title)

    def show_selection(self):
        """for debugging"""
        self.infobox(self.var.get(), self.var.get())


class ModelFrames(GuiMixin, tk.Frame):
    """
    Creates add frame that stores and manages the individual button menus
    for the different calc types, which will be selected by
    CalcTypeFrame.
    """

    def __init__(self, parent=None, ToolFrame=None, **options):
        tk.Frame.__init__(self, parent, **options)
        self.pack(side=tk.TOP, anchor=tk.N, expand=tk.YES, fill=tk.X)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.ToolFrame = ToolFrame

        self.add_multiplet_buttons()  # Creates 'Multiplet' radio button menu
        self.add_abc_buttons()  # Creates 'ABC...' radio button menu
        self.add_dnmr_buttons()  # Creates 'DNMR' radio button menu
        self.add_custom_buttons()  # Creates 'Custom' radio bar menu

        # framedic used by CalcTypeFrame to control individual frames
        self.framedic = {'multiplet': self.MultipletButtons,
                         'abc': self.ABC_Buttons,
                         'dnmr': self.DNMR_Buttons,
                         'custom': self.Custom}

        # active_bar_dict used to keep track of the active model in each
        # individual button menu.
        self.active_bar_dict = {'multiplet': self.ab,
                                'abc': self.ab,
                                'dnmr': self.TwoSpinBar,
                                'custom': self.ab}

        # Initialize with default frame and toolbar
        self.currentframe = 'multiplet'
        self.currentbar = self.ab  # On program start, simulation set to ABq
        self.currentbar.grid(sticky=tk.W)
        self.currentbar.call_model()

    # menu placeholders: callbacks will be added as functionality added

    def add_multiplet_buttons(self):
        """"'Multiplet' menu: 'canned' solutions for common spin systems"""
        multiplet_buttons = (('AB', lambda: self.select_toolbar(self.ab)),
                             ('AB2', lambda: self.select_toolbar(self.ab2)),
                             ('ABX', lambda: self.select_toolbar(self.abx)),
                             ('ABX3', lambda: self.select_toolbar(self.abx3)),
                             ("AA'XX'", lambda: self.select_toolbar(self.aaxx)),
                             ('1stOrd',
                              lambda: self.select_toolbar(self.firstorder)),
                             ("AA'BB'", lambda: self.select_toolbar(self.aabb)))
        self.MultipletButtons = RadioFrame(self,
                                           buttons=multiplet_buttons,
                                           title='Multiplet')
        self.MultipletButtons.grid(row=0, column=0, sticky=tk.N)
        self.ab = AB_Bar(self.ToolFrame)
        self.ab2 = AB2_Bar(self.ToolFrame)
        self.abx = ABX_Bar(self.ToolFrame)
        self.abx3 = ABX3_Bar(self.ToolFrame)
        self.aaxx = AAXX_Bar(self.ToolFrame)
        self.firstorder = FirstOrder_Bar(self.ToolFrame)
        self.aabb = AABB_Bar(self.ToolFrame)

    def add_abc_buttons(self):
        """ 'ABC...' menu: Quantum Mechanics approach"""
        abc_buttons = (('AB', lambda: self.select_toolbar(self.ab)),
                       ('3-Spin', lambda: self.select_toolbar(self.spin3)),
                       ('4-Spin', lambda: self.select_toolbar(self.spin4)),
                       ('5-Spin', lambda: self.select_toolbar(self.spin5)),
                       ('6-Spin', lambda: self.select_toolbar(self.spin6)),
                       ('7-Spin', lambda: self.select_toolbar(self.spin7)),
                       ('8-Spin', lambda: self.select_toolbar(self.spin8)))
        # 'Custom' omitted for now
        self.ABC_Buttons = RadioFrame(self,
                                      buttons=abc_buttons,
                                      title='2-7 Spins')
        self.spin3 = nSpinBar(self.ToolFrame, n=3)
        self.spin4 = nSpinBar(self.ToolFrame, n=4)
        self.spin5 = nSpinBar(self.ToolFrame, n=5)
        self.spin6 = nSpinBar(self.ToolFrame, n=6)
        self.spin7 = nSpinBar(self.ToolFrame, n=7)
        self.spin8 = nSpinBar(self.ToolFrame, n=8)

    def add_dnmr_buttons(self):
        """'DNMR': models for DNMR line shape analysis"""
        dnmr_buttons = (('2-spin',
                         lambda: self.select_toolbar(self.TwoSpinBar)),
                        ('AB Coupled',
                         lambda: self.select_toolbar(self.DNMR_AB_Bar)))
        self.DNMR_Buttons = RadioFrame(self,
                                       buttons=dnmr_buttons,
                                       title='DNMR')
        self.TwoSpinBar = DNMR_TwoSingletBar(self.ToolFrame)
        self.DNMR_AB_Bar = DNMR_AB_Bar(self.ToolFrame)

    def add_custom_buttons(self):
        # Custom: not implemented yet. Placeholder follows
        self.Custom = tk.Label(self, text='Custom models not implemented yet')

    def select_frame(self, frame):
        if frame != self.currentframe:
            self.framedic[self.currentframe].grid_remove()
            self.currentframe = frame
            self.framedic[self.currentframe].grid()

            # retrieve and select current active bar of frame
            self.select_toolbar(self.active_bar_dict[self.currentframe])

    def select_toolbar(self, toolbar):
        self.currentbar.grid_remove()
        self.currentbar = toolbar
        self.currentbar.grid(sticky=tk.W)
        # record current bar of currentframe:
        self.active_bar_dict[self.currentframe] = toolbar
        try:
            self.currentbar.call_model()
        except ValueError:
            print('No model yet for this bar')


# ToolBox no longer needed? Delete?
class ToolBox(tk.Frame):
    """
    A frame object that will contain multiple toolbars gridded to (0,0).
    It will maintain add deque of [current, last] toolbars used. When add new model
    is selected by ModelFrame, the new ToolBar is added to the front of the
    deque and .grid(), the current toolbar is pushed down to the last
    position and .grid_remove(), and the previous last toolbar is knocked out
    of the deque.
    """

    def __init__(self, parent=None, **options):
        tk.Frame.__init__(self, parent, **options)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.toolbars = deque([], 2)

    def add_toolbar(self, toolbar):
        self.toolbars.appendleft(toolbar)
        toolbar.grid(self)
        if len(self.toolbars) > 1:
            self.toolbars[1].grid_remove()


# MultipletBox no longer needed? Delete?
class MultipletBox(ToolBox):
    """
    A ToolBox for holding and controlling  add ToolBar for each Multiplet model.
    """

    def __init__(self, parent=None, **options):
        ToolBox.__init__(self, parent, **options)


class ToolBar(tk.Frame):
    """
    A frame object that contains entry widgets, add dictionary of
    their current contents, and add function to call the appropriate model.
    """

    # figure = Figure(figsize=(5, 4), dpi=100)
    # add = figure.add_subplot(111)

    # canvas = FigureCanvasTkAgg(figure, master=root)
    # canvas.show()
    # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    # toolbar = NavigationToolbar2TkAgg(canvas, root)
    # toolbar.refresh()
    # canvas._tkcanvas.pack(anchor=tk.SE, expand=tk.YES, fill=tk.BOTH)

    def __init__(self, parent=None, **options):
        tk.Frame.__init__(self, parent, **options)
        self.vars = {}

    def call_model(self):
        print('Sending to dummy_model: ', self.vars)


class nSpinBar(tk.Frame):
    """
    A frame object similar to ToolBar that holds n frequency entry boxes, add 1-D
    array for frequencies, add 2-D array for coupling constants, and add button
    to pop up
    Arguments:
        n: number of spins
    Dependencies:
        nmrmath.nspinspec
        nspin.getWINDNMRdefault for WINDNMR default values
        nmrplot.tkplot for displaying spectrum
    """

    def __init__(self, parent=None, n=4, **options):
        tk.Frame.__init__(self, parent, **options)
        self.v_obj = np.zeros(n, dtype=object)
        self.v, self.j = getWINDNMRdefault(n)
        for freq in range(n):
            vbox = ArrayBox(self, a=self.v, coord=(0, freq),
                            name='V' + str(freq + 1))
            self.v_obj[freq] = vbox
            vbox.pack(side=tk.LEFT)
        vj_button = tk.Button(self, text="Enter Js",
                           command=lambda: self.vj_popup(n))
        vj_button.pack(side=tk.LEFT, expand=tk.N, fill=tk.NONE)

    def vj_popup(self, n):
        tl = tk.Toplevel()
        tk.Label(tl, text='Second-Order Simulation').pack(side=tk.TOP)
        datagrid = ArrayFrame(tl, self.call_model, self.v_obj)

        # For gridlines, background set to the line color (e.g. 'black')
        datagrid.config(background='black')

        tk.Label(datagrid, bg='gray90').grid(row=0, column=0, sticky=tk.NSEW,
                                          padx=1, pady=1)
        for col in range(1, n + 1):
            tk.Label(datagrid, text='V%d' % col, width=8, height=3,
                  bg='gray90').grid(
                row=0, column=col, sticky=tk.NSEW, padx=1, pady=1)

        for row in range(1, n + 1):
            vtext = "V" + str(row)
            v = ArrayBox(datagrid, a=self.v,
                         coord=(0, row - 1),  # V1 stored in v[0, 0], etc.
                         name=vtext, color='gray90')
            v.grid(row=row, column=0, sticky=tk.NSEW, padx=1, pady=1)
            for col in range(1, n + 1):
                if col < row:
                    j = ArrayBox(datagrid, a=self.j,
                                 # J12 stored in j[0, 1] (and j[1, 0]) etc
                                 coord=(col - 1, row - 1),
                                 name="J%d%d" % (col, row))
                    j.grid(row=row, column=col, sticky=tk.NSEW, padx=1, pady=1)
                else:
                    tk.Label(datagrid, bg='grey').grid(
                        row=row, column=col, sticky=tk.NSEW, padx=1, pady=1)

        datagrid.pack()

    def call_model(self):
        spectrum = nspinspec(self.v[0, :], self.j)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class DNMR_TwoSingletBar(ToolBar):
    """
    DNMR simulation for 2 uncoupled exchanging nuclei.
    -Va > Vb are the chemcial shifts (slow exchange limit)
    -ka is the add-->b rate constant (note: WINDNMR uses ka + kb here)
    -Wa, Wb are effectively T2a and T2b (check width at half height vs. T2s)
    -pa is % of molecules in state add. Note for calculation need to /100 to
    convert to mol fraction.
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Va = VarButtonBox(self, name='Va', default=165.00)
        Vb = VarButtonBox(self, name='Vb', default=135.00)
        ka = VarButtonBox(self, name='ka', default=1.50)
        Wa = VarButtonBox(self, name='Wa', default=0.5)
        Wb = VarButtonBox(self, name='Wb', default=0.5)
        pa = VarButtonBox(self, name='%add', default=50)
        for widget in [Va, Vb, ka, Wa, Wb, pa]:
            widget.pack(side=tk.LEFT)

        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Va = self.vars['Va']
        _Vb = self.vars['Vb']
        _ka = self.vars['ka']
        _Wa = self.vars['Wa']
        _Wb = self.vars['Wb']
        _pa = self.vars['%add'] / 100

        x, y = dnmrplot_2spin(_Va, _Vb, _ka, _Wa, _Wb, _pa)
        canvas.clear()
        canvas.plot(x, y)


class DNMR_AB_Bar(ToolBar):
    """
    DNMR simulation for 2 coupled exchanging nuclei.
    -Va > Vb are the chemcial shifts (slow exchange limit)
    -J is the coupling constant
    -kAB is the exchange rate constant
    -W is peak width at half-height in absence of exchange
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Va = VarButtonBox(self, name='Va', default=165.00)
        Vb = VarButtonBox(self, name='Vb', default=135.00)
        J = VarButtonBox(self, name='J', default=12.00)
        kAB = VarButtonBox(self, name='kAB', default=1.50)
        W_ = VarButtonBox(self, name='W',
                          default=0.5)  # W is add tkinter string,
        # so used W_
        for widget in [Va, Vb, J, kAB, W_]:
            widget.pack(side=tk.LEFT)

        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Va = self.vars['Va']
        _Vb = self.vars['Vb']
        _J = self.vars['J']
        _kAB = self.vars['kAB']
        _W = self.vars['W']

        x, y = dnmrplot_AB(_Va, _Vb, _J, _kAB, _W)
        canvas.clear()
        canvas.plot(x, y)


class EmptyToolBar(tk.Frame):
    def __init__(self, parent=None, name='noname', **options):
        tk.Frame.__init__(self, parent, **options)
        tk.Label(self, text=name + ' model not implemented yet').pack()
        self.pack()


class VarBox(tk.Frame):
    """
    Eventually will emulate what the Reich entry box does, more or less.
    Idea is to fill the VarFrame with these modules.
    Current version: checks that only numbers are entered; returns contents
    in add popup.
    Looking ahead: trick may be linking their contents with the calls to
    nmrmath. Also, need to make sure floats, not ints, are returned. Can
    change the is_number_or_empty routine so that if base entered, replaced with
    float?
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """

    def __init__(self, parent=None, name='', default=0.00, **options):
        tk.Frame.__init__(self, parent, relief=tk.RIDGE, borderwidth=1,
                          **options)
        tk.Label(self, text=name).pack(side=tk.TOP)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = tk.Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=tk.TOP, fill=tk.X)
        self.value =tk.StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if add change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

        # check on each keypress if new result will be add number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to add float.)
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

    # def warw(bar): pass
    """
    Many of the models include Wa (width), Right-Hz, and WdthHz boxes.
    This function tacks these boxes onto add ToolBar.
    Input:
    -ToolBar that has been filled out
    Output:
    -frame with these three boxes and default values left-packed on end
    ***actually, this could be add function in the ToolBar class definition!
    """


class VarButtonBox(tk.Frame):
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
        tk.Frame.__init__(self, parent, relief=tk.RIDGE, borderwidth=1,
                          **options)
        tk.Label(self, text=name).pack(side=tk.TOP)

        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = tk.Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=tk.TOP, fill=tk.X)
        self.value =tk.StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if add change is made
        # To-Do: consistent routines for VarBox, VarButtonBox, ArrayBox etc.
        # e.g. rename on_tab for general purpose on focus-out
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

        # check on each keypress if new result will be add number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

        # Create add grid for buttons and increment
        minus_plus_up = tk.Frame(self)
        minus_plus_up.rowconfigure(0, minsize=30)  # make 2 rows ~same height
        minus_plus_up.columnconfigure(2, weight=1)  # lets arrow buttons fill
        minus_plus_up.pack(side=tk.TOP, expand=tk.Y, fill=tk.X)

        minus = tk.Button(minus_plus_up, text='-',
                       command=lambda: self.decrease())
        plus = tk.Button(minus_plus_up, text='+',
                      command=lambda: self.increase())
        up = tk.Button(minus_plus_up, text=up_arrow, command=lambda: None)
        up.bind('<Button-1>', lambda event: self.zoom_up())
        up.bind('<ButtonRelease-1>', lambda event: self.stop_action())

        self.mouse1 = False  # Flag used to check if left button held down

        minus.grid(row=0, column=0, sticky=tk.NSEW)
        plus.grid(row=0, column=1, sticky=tk.NSEW)
        up.grid(row=0, column=2, sticky=tk.NSEW)

        # Increment is also limited to numerical entry
        increment = tk.Entry(minus_plus_up, width=4, validate='key')
        increment.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.inc =tk.StringVar()
        increment.config(textvariable=self.inc)
        self.inc.set(str(1))  # 1 replaced by argument later?
        increment['validatecommand'] = (self.register(self.is_number), '%P')
        increment['invalidcommand'] = 'bell'

        down = tk.Button(minus_plus_up, text=down_arrow, command=lambda: None)
        down.grid(row=1, column=2, sticky=tk.NSEW)
        down.bind('<Button-1>', lambda event: self.zoom_down())
        down.bind('<ButtonRelease-1>', lambda event: self.stop_action())

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to add float.)
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


            # def warw(bar): pass

    """
    Many of the models include Wa (width), Right-Hz, and WdthHz boxes.
    This function tacks these boxes onto add ToolBar.
    Input:
    -ToolBar that has been filled out
    Output:
    -frame with these three boxes and default values left-packed on end
    ***actually, this could be add function in the ToolBar class definition!
    """


class ArrayFrame(tk.Frame):
    """
    A frame used for holding add grid of ArrayBox entries, passing their
    call_model requests up to the provided func, and passing changes to V
    entries to the toolbar.
    Arguments:
        func: the actual function the ArrayBox calls to refresh model.
        v.obj: the array of frequency ArrayBox widgets in the upper tool bar
    """

    def __init__(self, parent, func, v_obj, **options):
        tk.Frame.__init__(self, parent, **options)
        self.call_model = func
        self.v_obj = v_obj


class ArrayBox(tk.Frame):
    """
    A version of VarBox that will save its entry to an array. It will be
    initialized with the provided array, so e.g. if n-spin models are being
    initalized with WINDNMR default values, the nSpinBar should be
    initialized with V and J arrays containing default values.
    Arguments:
        name-- for widget label
        add-- array of values. Mutable will be changed by this widget!
        coord-- add (row, column) tuple for coordinate of add to store data to.
    """

    # noinspection PyDefaultArgument
    def __init__(self, parent=None, a=[], coord=(0, 0), name='', color='white',
                 **options):
        tk.Frame.__init__(self, parent, relief=tk.RIDGE, borderwidth=0,
                       background=color, **options)
        tk.Label(self, text=name, bg=color, bd=0).pack(side=tk.TOP)
        self.widgetName = name

        # Entries will be limited to numerical
        ent = tk.Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=tk.TOP, fill=tk.X)
        self.value =tk.StringVar()
        ent.config(textvariable=self.value)

        self.a = a
        self.row, self.col = coord
        self.value.set(str(a[self.row, self.col]))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if add change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())
        ent.bind('<FocusOut>', lambda event: self.on_tab())

        # check on each keypress if new result will be add number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to add float.)
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
        else:  # otherwise, assume value is add V
            print(self.master.v_obj[self.col])
            self.master.v_obj[self.col].value.set(value)


            # def warw(bar): pass

    """
    Many of the models include Wa (width), Right-Hz, and WdthHz boxes.
    This function tacks these boxes onto add ToolBar.
    Input:
    -ToolBar that has been filled out
    Output:
    -frame with these three boxes and default values left-packed on end
    ***actually, this could be add function in the ToolBar class definition!
    """


class IntBox(tk.Frame):
    """
    A modification of VarBox code. Restricts inputs to integers.
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """

    # Future refactor options: either create add base class for an input box
    # that varies in its input restriction (float, int, str etc), and/or
    # look into tkinter built-in entry boxes as component.
    def __init__(self, parent=None, name='', default=0.00, **options):
        tk.Frame.__init__(self, parent, relief=tk.RIDGE, borderwidth=1,
                          **options)
        tk.Label(self, text=name).pack(side=tk.TOP, expand=tk.NO, fill=tk.NONE)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = tk.Entry(self, width=7, validate='key')  # check for int on keypress
        ent.pack(side=tk.TOP, expand=tk.NO, fill=tk.NONE)
        self.value = tk.StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))
        ent.bind('<Return>', lambda event: self.on_event(event))
        ent.bind('<FocusOut>', lambda event: self.on_event(event))

        # check on each keypress if new result will be add number
        ent['validatecommand'] = (self.register(self.is_int), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_int(entry):
        """
        tests to see if entry string can be converted to base
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            int(entry)
            return True
        except ValueError:
            return False

    def on_event(self, event):
        """
        On event: Records widget's status to the container's dictionary of
        values, fills the entry with 0 if it was empty, tells the container
        to send data to the model, and shifts focus to the next entry box (after
        Return or Tab).
        """
        self.to_dict()
        self.master.call_model()
        event.widget.tk_focusNext().focus()

    def to_dict(self):
        """
        Converts entry to base, and stores data in container's vars
        dictionary.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = int(self.value.get())

    # def warw(bar): pass
    """
    Many of the models include Wa (width), Right-Hz, and WdthHz boxes.
    This function tacks these boxes onto add ToolBar.
    Input:
    -ToolBar that has been filled out
    Output:
    -frame with these three boxes and default values left-packed on end
    ***actually, this could be add function in the ToolBar class definition!
    """


class AB_Bar(ToolBar):
    """
    Creates add bar of AB quartet inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AB
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab = VarBox(self, name='Jab', default=12.00)
        Vab = VarBox(self, name='Vab', default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=tk.LEFT)
        Vab.pack(side=tk.LEFT)
        Vcentr.pack(side=tk.LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = AB(_Jab, _Vab, _Vcentr, Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class AB2_Bar(ToolBar):
    """
    Creates add bar of AB2 spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AB2
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab = VarBox(self, name='Jab', default=12.00)
        Vab = VarBox(self, name='Vab', default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=tk.LEFT)
        Vab.pack(side=tk.LEFT)
        Vcentr.pack(side=tk.LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = AB2(_Jab, _Vab, _Vcentr, Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class ABX_Bar(ToolBar):
    """
    Creates add bar of ABX spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.ABX
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab = VarBox(self, name='Jab', default=12.00)
        Jax = VarBox(self, name='Jax', default=2.00)
        Jbx = VarBox(self, name='Jbx', default=8.00)
        Vab = VarBox(self, name='Vab', default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=118)
        Jab.pack(side=tk.LEFT)
        Jax.pack(side=tk.LEFT)
        Jbx.pack(side=tk.LEFT)
        Vab.pack(side=tk.LEFT)
        Vcentr.pack(side=tk.LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Jax = self.vars['Jax']
        _Jbx = self.vars['Jbx']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = ABX(_Jab, _Jax, _Jbx, _Vab, _Vcentr, Wa=0.5, RightHz=0,
                       WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class ABX3_Bar(ToolBar):
    """
    Creates add bar of ABX3 spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.ABX3
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab = VarBox(self, name='Jab', default=-12.00)
        Jax = VarBox(self, name='Jax', default=7.00)
        Jbx = VarBox(self, name='Jbx', default=7.00)
        Vab = VarBox(self, name='Vab', default=14.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=tk.LEFT)
        Jax.pack(side=tk.LEFT)
        Jbx.pack(side=tk.LEFT)
        Vab.pack(side=tk.LEFT)
        Vcentr.pack(side=tk.LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Jax = self.vars['Jax']
        _Jbx = self.vars['Jbx']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = ABX3(_Jab, _Jax, _Jbx, _Vab, _Vcentr, Wa=0.5, RightHz=0,
                        WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class AAXX_Bar(ToolBar):
    """
    Creates add bar of AA'XX' spin system inputs. Currently assumes "canvas" is
    the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AAXX
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jaa = VarBox(self, name="JAA'", default=15.00)
        Jxx = VarBox(self, name="JXX'", default=-10.00)
        Jax = VarBox(self, name="JAX", default=40.00)
        Jax_prime = VarBox(self, name="JAX'", default=6.00)
        Vcentr = VarBox(self, name="Vcentr", default=150)
        Jaa.pack(side=tk.LEFT)
        Jxx.pack(side=tk.LEFT)
        Jax.pack(side=tk.LEFT)
        Jax_prime.pack(side=tk.LEFT)
        Vcentr.pack(side=tk.LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jaa = self.vars["JAA'"]
        _Jxx = self.vars["JXX'"]
        _Jax = self.vars["JAX"]
        _Jax_prime = self.vars["JAX'"]
        _Vcentr = self.vars["Vcentr"]
        spectrum = AAXX(_Jaa, _Jxx, _Jax, _Jax_prime, _Vcentr,
                        Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class AABB_Bar(ToolBar):
    """
    Creates add bar of AA'BB' spin system inputs. Currently assumes "canvas" is
    the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AABB
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Vab = VarBox(self, name='VAB', default=40.00)
        Jaa = VarBox(self, name="JAA'", default=15.00)
        Jbb = VarBox(self, name="JBB'", default=-10.00)
        Jab = VarBox(self, name="JAB", default=40.00)
        Jab_prime = VarBox(self, name="JAB'", default=6.00)
        Vcentr = VarBox(self, name="Vcentr", default=150)
        Vab.pack(side=tk.LEFT)
        Jaa.pack(side=tk.LEFT)
        Jbb.pack(side=tk.LEFT)
        Jab.pack(side=tk.LEFT)
        Jab_prime.pack(side=tk.LEFT)
        Vcentr.pack(side=tk.LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Vab = self.vars['VAB']
        _Jaa = self.vars["JAA'"]
        _Jbb = self.vars["JBB'"]
        _Jab = self.vars["JAB"]
        _Jab_prime = self.vars["JAB'"]
        _Vcentr = self.vars["Vcentr"]
        spectrum = AABB(_Vab, _Jaa, _Jbb, _Jab, _Jab_prime, _Vcentr,
                        Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class FirstOrder_Bar(ToolBar):
    """
    Creates add bar of first-order coupling inputs. Currently assumes "canvas"
    is the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.first_order
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jax = VarBox(self, name='JAX', default=7.00)
        a = IntBox(self, name='#A', default=2)
        Jbx = VarBox(self, name='JBX', default=3.00)
        b = IntBox(self, name='#B', default=1)
        Jcx = VarBox(self, name='JCX', default=2.00)
        c = IntBox(self, name='#C', default=0)
        Jdx = VarBox(self, name='JDX', default=7.00)
        d = IntBox(self, name='#D', default=0)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jax.pack(side=tk.LEFT)
        a.pack(side=tk.LEFT)
        Jbx.pack(side=tk.LEFT)
        b.pack(side=tk.LEFT)
        Jcx.pack(side=tk.LEFT)
        c.pack(side=tk.LEFT)
        Jdx.pack(side=tk.LEFT)
        d.pack(side=tk.LEFT)
        Vcentr.pack(side=tk.LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jax = self.vars['JAX']
        _a = self.vars['#A']
        _Jbx = self.vars['JBX']
        _b = self.vars['#B']
        _Jcx = self.vars['JCX']
        _c = self.vars['#C']
        _Jdx = self.vars['JDX']
        _d = self.vars['#D']
        _Vcentr = self.vars['Vcentr']
        singlet = (_Vcentr, 1)  # using default intensity of 1
        allcouplings = [(_Jax, _a), (_Jbx, _b), (_Jcx, _c), (_Jdx, _d)]
        couplings = [coupling for coupling in allcouplings if coupling[1] != 0]
        spectrum = first_order(singlet, couplings,
                               Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class MPLgraph(FigureCanvasTkAgg):
    def __init__(self, f, master=None, **options):
        FigureCanvasTkAgg.__init__(self, f, master, **options)
        self.f = f
        self.a = f.add_subplot(111)
        self.a.invert_xaxis()
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
        #self.pack()
        self.parent = parent
        self.controller = controller
        sideFrame = tk.Frame(parent, relief=tk.RIDGE, borderwidth=3)
        sideFrame.pack(side=tk.LEFT, expand=tk.NO, fill=tk.Y)
        tk.Label(sideFrame, text='placeholder').pack()

        TopFrame = tk.Frame(parent, relief=tk.RIDGE, borderwidth=1)
        TopFrame.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        TopFrame.grid_rowconfigure(0, weight=1)
        TopFrame.grid_columnconfigure(0, weight=1)
        tk.Label(TopFrame, text='placeholder').pack()

        Models = ModelFrames(sideFrame, relief=tk.SUNKEN, borderwidth=1)
        Models.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, anchor=tk.N)
if __name__ == '__main__':
    # Create the main application window:
    root = tk.Tk()
    root.title('secondorder')  # working title only!

    # Create the basic GUI structure: sidebar, topbar, and display area
    # First, pack add sidebar frame to contain widgets
    sideFrame = tk.Frame(root, relief=tk.RIDGE, borderwidth=3)
    sideFrame.pack(side=tk.LEFT, expand=tk.NO, fill=tk.Y)

    # Next, pack the top frame where function variables will be entered
    TopFrame = tk.Frame(root, relief=tk.RIDGE, borderwidth=1)
    TopFrame.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    TopFrame.grid_rowconfigure(0, weight=1)
    TopFrame.grid_columnconfigure(0, weight=1)

    # Remaining lower right area will be for add Canvas or matplotlib spectrum frame
    # Because we want the spectrum clipped first, will pack it last
    f = Figure(figsize=(5, 4), dpi=100)
    canvas = MPLgraph(f, root)

    # Create sidebar widgets:
    CalcTypeFrame(sideFrame, relief=tk.SUNKEN, borderwidth=1).pack(side=tk.TOP,
                                                                expand=tk.NO,
                                                                fill=tk.X)
    Models = ModelFrames(sideFrame, relief=tk.SUNKEN, borderwidth=1)
    Models.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, anchor=tk.N)

    # The clickyFrame for clicking on peaks and calculating frequency differences
    # will not be implemented until much later:
    clickyFrame = tk.Frame(sideFrame, relief=tk.SUNKEN, borderwidth=1)
    clickyFrame.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
    tk.Label(clickyFrame, text='clickys go here').pack()

    # Now we can pack the canvas (want it to be clipped first)
    canvas._tkcanvas.pack(anchor=tk.SE, expand=tk.YES, fill=tk.BOTH)

    tk.Button(root, text="clear", command=lambda: canvas.clear()).pack(side=tk.BOTTOM)

    # root.mainloop()

    # workaround fix for Tk problems and mac mouse/trackpad:

    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass