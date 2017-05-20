"""The main routine for the secondorder app, to be run from the command line."""


import tkinter as tk

from secondorder.controller.controller import Controller

root = tk.Tk()
root.title('secondorder')
app = Controller(root)

# workaround fix for Tk problems and mac mouse/trackpad:
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass
