""" In progress: Excise multipurpose widgets from view.py to here"""
from tkinter import *


class VBox(Frame):
    """
    Test widget to see if ArrayBox concept can be simplified
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
        self.ent = ent  # hack used for identifying next entry box on tab

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab(event))
        ent.bind('<FocusOut>', lambda event: self.on_focus_out())

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

    def on_tab(self, event):
        self.on_focus_out()
        self.find_next_entry(self.ent).focus()
        return 'break'  # override default tkinter tab behavior

    def find_next_entry(self, current_entry):

        next_entry = current_entry.tk_focusNext()
        if next_entry.widgetName == 'entry':
            return next_entry
        else:
            return self.find_next_entry(next_entry)

    def on_focus_out(self):
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
        value = float(self.value.get())
        self.a[self.row, self.col] = value
        if self.a.shape[0] > 1:  # if more than one row, assume J matrix
            self.a[self.col, self.row] = value  # fill cross-diagonal element
        else:  # otherwise, assume value is a V
            print(self.master.v_obj[self.col])
            self.master.v_obj[self.col].value.set(value)


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
        value = float(self.value.get())
        self.a[self.row, self.col] = value
        if self.a.shape[0] > 1:  # if more than one row, assume J matrix
            self.a[self.col, self.row] = value  # fill cross-diagonal element
        else:  # otherwise, assume value is a V
            print(self.master.v_obj[self.col])
            self.master.v_obj[self.col].value.set(value)


if __name__ == '__main__':
    root = Tk()

    class View(Frame):
        def __init__(self, parent, **options):
            Frame.__init__(self, parent, **options)
            self.testvar = 0.5

            TestBox = VarBox(self, self.testvar)


