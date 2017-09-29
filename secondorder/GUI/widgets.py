""" In progress: Excise multipurpose widgets from view.py to here"""
from tkinter import *


class EntryFrame(Frame):
    """
    A tkinter Frame that holds a labeled entry widget with added behavior.
    Intended as a new base class that will be inherited from.
    Arguments (in addition to standard Frame options):
        name-- for widget label
    """

    # noinspection PyDefaultArgument
    def __init__(self, parent=None, name='', color='white',
                 **options):
        """
        __init__ is broken into multiple method references, to allow
        flexibility for subclasses.
        """
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=0,
                       background=color, **options)
        self.name = name
        # Is the next line needed?
        self.widgetName = self.name

        self.initialize(**options)
        self.add_label(name, color)
        self.add_entry()
        self.bind_entry()
        self.validate_entry()

    def initialize(self, **kwargs):
        self.value = StringVar()
        self.stored_value = 0.0
        self.value.set(self.stored_value)

    def add_label(self, name, color):
        Label(self, text=name, bg=color, bd=0).pack(side=TOP)

    def add_entry(self):
        self.entry = Entry(self, width=7,
                           validate='key')  # check for number on keypress)
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(textvariable=self.value)

    def bind_entry(self):
        self.entry.bind('<Return>', lambda event: self.on_return(event))
        self.entry.bind('<Tab>', lambda event: self.on_tab(event))
        self.entry.bind('<FocusOut>', lambda event: self.refresh())

    def on_return(self, event):
        self.refresh()
        self.find_next_entry(self.entry).focus()

    def refresh(self):
        if self.entry_is_changed():
            self.save_entry()
            self.master.request_plot()

    def entry_is_changed(self):
        return self.stored_value != float(self.value.get())

    def find_next_entry(self, current_entry):

        next_entry = current_entry.tk_focusNext()
        if next_entry.widgetName == 'entry':
            return next_entry
        else:
            return self.find_next_entry(next_entry)

    def validate_entry(self):
        """
        The base EntryFrame class assumes the entry contents should be numerical
        """
        # check on each keypress if new result will be a number
        self.entry['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        self.entry['invalidcommand'] = 'bell'

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

    def on_tab(self, event):
        self.refresh()
        self.find_next_entry(self.entry).focus()
        return 'break'  # override default tkinter tab behavior

    def save_entry(self):
        """
        Saves widget's entry as self.stored_value , filling the entry with
        0.00 if it was empty.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        value = float(self.value.get())
        self.stored_value = value


class NewArrayBox(EntryFrame):
    def __init__(self, parent=None,
                 # array=[], coord=(0, 0),
                 # name='', color='white',
                 **options):
        EntryFrame.__init__(self, parent,
                            # name, color,
                            **options)
        self.array = array
        self.row, self.col = coord
        self.stored_value = array[self.row, self.col]
        self.value.set(self.stored_value)

    def initialize(self,
                   array=[], coord=(0, 0),
                   **kwargs):
        self.array = array
        self.row, self.col = coord
        self.value = StringVar()
        self.stored_value = self.array[self.row, self.col]
        self.value.set(self.stored_value)

    def save_entry(self):
        """
                Records widget's status to the array, filling the entry with
                0.00 if it was empty.
                """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        value = float(self.value.get())
        self.array[self.row, self.col] = value
        if self.array.shape[0] > 1:  # if more than one row, assume J matrix
            self.array[self.col, self.row] = value  # fill cross-diagonal
                                                    # element


class NewArraySpinBox(NewArrayBox):
    def __init__(self, parent=None, from_=0.00, to=100.00, increment=1,
                **options):
        NewArrayBox.__init__(self, parent, **options)
        self.spinbox_kwargs = {'from_': from_,
                               'to': to,
                               'increment': increment}
        print('Initializing spinbox with kwargs ', self.spinbox_kwargs)

    def add_entry(self):
        print('Initializing spinbox with kwargs ', self.spinbox_kwargs)
        self.add_spinbox(**self.spinbox_kwargs)

    def add_spinbox(self, **kwargs):
        self.entry = Spinbox(self, width=7,
                             validate='key',  # check for number on keypress
                             from_=-100000, to=100000, increment=1
                             # **kwargs
                             )
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(textvariable=self.value)



class ArrayBox(Frame):
    """
    A tkinter Frame that holds a labeled entry widget with added features,
    and charged with updating a numpy array (passed into it as an argument).
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
        self.on_focus_out()
        self.find_next_entry(self.ent).focus()

    def on_tab(self, event):
        self.on_focus_out()
        self.find_next_entry(self.ent).focus()
        return 'break'  # override default tkinter tab behavior

    def find_next_entry(self, current_entry):

        next_entry = current_entry.tk_focusNext()
        if next_entry.widgetName in ['entry', 'spinbox']:
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


class ArraySpinBox(Frame):
    """
      Spinoff of ArrayBox that uses a tkinter spinbox
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

        # Can't find a way to bind to the spinbox arrow buttons, so:
        # A flag will be used to detect when mouse button is held down
        self.button_held_job = None

        # Entries will be limited to numerical
        ent = Spinbox(self, width=7,
                      from_=-100000, to=100000, increment=1,
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
        ent.bind('<ButtonPress-1>', lambda event: self.on_press())
        ent.bind('<ButtonRelease-1>', lambda event: self.on_release())

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
        self.on_focus_out()
        self.find_next_entry(self.ent).focus()

    def on_tab(self, event):
        self.on_focus_out()
        self.find_next_entry(self.ent).focus()
        return 'break'  # override default tkinter tab behavior

    def find_next_entry(self, current_entry):
        next_entry = current_entry.tk_focusNext()
        if next_entry.widgetName in ['spinbox', 'entry']:
            return next_entry
        else:
            return self.find_next_entry(next_entry)

    def on_focus_out(self):
        print('Invoked on_focus_out')
        if self.entry_is_changed():
            self.to_array()
            self.master.request_plot()

    def on_press(self):
        print('Button pressed')
        self.refresh()


    def on_release(self):
        print('Button released')
        self._root().after_cancel(self.button_held_job)
        self.on_focus_out()

    def refresh(self):
        print('Refreshing...')
        self.on_focus_out()
        self.button_held_job = self._root().after(50, self.refresh)

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


if __name__ == '__main__':
    import numpy as np
    dummy_array = np.array([[1, 42, 666, 2001]])
    root = Tk()
    root.title('test widgets')

    class TestFrame(Frame):
        def __init__(self, parent, **options):
            Frame.__init__(self, parent, **options)

        def request_plot(self):
            print('TestFrame.request_plot() called')
            print(dummy_array)

    mainwindow = TestFrame(root)
    mainwindow.pack()

    baseclass = EntryFrame(mainwindow, name='baseclass')
    baseclass.pack(side=LEFT)
    nospin = ArrayBox(mainwindow, a=dummy_array, coord=(0, 0), name='V1')
    nospin.pack(side=LEFT)
    spin = ArraySpinBox(mainwindow, a=dummy_array, coord=(0, 1), name='V42')
    spin.pack(side=LEFT)
    newarray = NewArrayBox(mainwindow, array=dummy_array, coord=(0, 2),
                           name='V666')
    newarray.pack(side=LEFT)
    newspinbox = NewArraySpinBox(mainwindow, array=dummy_array, coord=(0, 3),
                                 name='V2001')
    newspinbox.pack(side=LEFT)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

