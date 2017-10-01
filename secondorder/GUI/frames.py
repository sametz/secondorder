"""In progress: excise frames from view.py to here."""
from tkinter import *
from secondorder.GUI.toolbars import SecondOrderBar as nSpinBar
from .toolbars import SecondOrderSpinBar


class RadioFrame(Frame):
    """
    A frame containing a radio button menu and optional title.

    TODO: since this is a class with only an __init__, this should possibly
    be a function and not a class. Refactor?
    """

    def __init__(self, parent=None, buttons=(), title='', **options):
        """arguments:
        -buttons: a tuple of (text, function) tuples
        -title: an optional title to put above the button list"""
        Frame.__init__(self, parent, **options)
        Label(self, text=title).pack(side=TOP)
        self.var = StringVar()
        for button in buttons:
            Radiobutton(self, text=button[0], command=button[1],
                        variable=self.var,
                        value=button[0]).pack(anchor=NW)
        self.var.set(buttons[0][0])  # turns the top button on


# TODO: code in next class seems repetetive. Refactor?
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

        self.currentbar = self.spin2  # initialize with 2-spin system (AB)
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
        self.ABC_Buttons = RadioFrame(self,
                                      buttons=abc_buttons,
                                      title='Number of Spins')
        self.ABC_Buttons.grid(row=0, column=0, sticky=N)

        # To test toolbar/widget refactoring, spin2 will be altered
        # self.spin2 = nSpinBar(self.toolframe, controller=self.controller, n=2)
        self.spin2 = SecondOrderSpinBar(self.toolframe,
                                        controller=self.controller,
                                        realtime=True,
                                        n=2)

        self.spin3 = nSpinBar(self.toolframe, controller=self.controller, n=3)
        self.spin4 = nSpinBar(self.toolframe, controller=self.controller, n=4)
        self.spin5 = nSpinBar(self.toolframe, controller=self.controller, n=5)
        self.spin6 = nSpinBar(self.toolframe, controller=self.controller, n=6)
        self.spin7 = nSpinBar(self.toolframe, controller=self.controller, n=7)
        self.spin8 = SecondOrderSpinBar(self.toolframe,
                                     controller=self.controller, n=8)

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


class ArrayFrame(Frame):
    # Scheduled for deletion
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
