import numpy as np


class Model:

    def power(self, x, base, exponent):
        return (x * base) ** exponent

    def powerplot(self, base, exponent):
        x = np.linspace(0, 10, 800)
        y = self.power(x, base, exponent)
        return x, y

if __name__ == '__main__':
    model = Model().powerplot(1, 10)
    print(model)
