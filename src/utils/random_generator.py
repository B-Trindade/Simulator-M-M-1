from random import random
from random import seed as set_seed
import math

class RandomGenerator:
    def __init__(self, seed, rate):
        set_seed(seed)
        self.rate = rate

    def next(self):
        pass

class Regular(RandomGenerator):
    def next(self):
        return random()

class Exponential(RandomGenerator):
    def next(self):
        return math.log(1-random())/-self.rate

class Deterministic(RandomGenerator):
    def next(self):
        return 1/self.rate

def main():
    generator = Exponential(1, 1)
    for _ in range(0,10):
        print(generator.next())

if __name__ == "__main__":
    main()
