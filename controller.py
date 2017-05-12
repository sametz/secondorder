import tkinter as tk
from view import View
from model import Model


class Controller:
    def __init__(self, root):
        self.model = Model()
        self.view = View(root, self)
        self.view.integer.set('1')
        self.view.exponent.set('2')
        self.update_view()

    def update_view(self):
        self.update_view_data()
        self.get_model_data(self.integer, self.exponent)
        self.update_view_plot()

    def update_view_data(self):
        self.integer = float(self.view.integer.get())
        self.exponent = float(self.view.exponent.get())

    def get_model_data(self, base, exponent):
        self.model_data = self.model.powerplot(base, exponent)

    def update_view_plot(self):
        self.view.canvas.clear()
        self.view.canvas.plot(*self.model_data)


if __name__ == '__main__':
    root = tk.Tk()
    app = Controller(root)
    root.mainloop()
