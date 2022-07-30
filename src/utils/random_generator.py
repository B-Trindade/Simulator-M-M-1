from random import random
from random import seed as set_seed
import math


class RandomGenerator:
    '''Classe base para o gerador de números aleatórios'''

    def __init__(self, seed: int, rate: float):
        if seed is not None:
            set_seed(seed)
        self.rate = rate

    def next(self) -> float:
        pass


class Regular(RandomGenerator):
    '''Gera números aleatórios entre 0 e 1 normalmente'''

    def next(self) -> float:
        return random()


class Exponential(RandomGenerator):
    '''Gera números aleatórios com distribuição exponencial
    de acordo com a fórmula ln(1-rand)/-λ'''

    def next(self) -> float:
        return math.log(1-random())/-self.rate


class Deterministic(RandomGenerator):
    '''Números não aleatórios gerados deterministicamente'''

    def next(self) -> float:
        return 1/self.rate


def main():
    generator = Exponential(1, 2)
    for _ in range(10):
        print(generator.next())


if __name__ == "__main__":
    main()
