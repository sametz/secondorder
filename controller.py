import tkinter as tk
from view import View


class Controller:

    def __init__(self, root):
        self.view = View(root, self)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('secondorder')  # working title only!
    app = Controller(root)
    root.mainloop()