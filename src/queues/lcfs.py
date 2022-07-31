from utils.stats_collector import Client
from typing import List

class LCFSQueue:
    def __init__(self):
        self.list = []

    # Remove e retorna o último elemento da lista
    def next(self) -> List:
        return self.list.pop()

    def length(self) -> int:
        return len(self.list)

    # Insere no início da lista (pilha)
    def add(self, data: Client):
        self.list.append(data)
