from random import random
from random import seed as set_seed
import math

# Classe base para o gerador de números aleatórios
class RandomGenerator:
    def __init__(self, seed: int, rate: float):
        set_seed(seed)
        self.rate = rate

    def next(self) -> float:
        pass

# Gera números aleatórios entre 0 e 1 normalmente
class Regular(RandomGenerator):
    def next(self) -> float:
        return random()

# Gera números aleatórios com distribuição exponencial
# de acordo com a fórmula ln(1-rand)/-λ
class Exponential(RandomGenerator):
    def next(self) -> float:
        return math.log(1-random())/-self.rate

# Números não aleatórios gerados deterministicamente
class Deterministic(RandomGenerator):
    def next(self) -> float:
        return 1/self.rate

def main():
    generator = Exponential(1, 1)
    for _ in range(0,10):
        print(generator.next())

if __name__ == "__main__":
    main()
