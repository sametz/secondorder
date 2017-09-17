from tkinter import *


""" To Do: Excise multipurpose widgets from view.py to here"""


if __name__ == '__main__':
    root = Tk()

    class View(Frame):
        def __init__(self, parent, **options):
            Frame.__init__(self, parent, **options)
            self.testvar = 0.5

            TestBox = VarBox(self, self.testvar)


