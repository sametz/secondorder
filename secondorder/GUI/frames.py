"""In progress: excise frames from view.py to here."""
from tkinter import *

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
