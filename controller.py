import secondorder.nmrmath
import secondorder.nmrplot

class Controller:
    def __init__(self, plotter, **kwargs):
        self.plotter = plotter

    def plot(self, model=None, data=None):
        print('model:', model)
        print('data:', data)
        print('output to:', self.plotter)

if __name__ == '__main__':
    controller = Controller(plotter='canvas')
    controller.plot(model='ab', data={'v1': 10})
