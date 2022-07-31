from utils.stats_collector import Client
from typing import List

class FCFSQueue:
    def __init__(self):
        self.list = []

    # Remove e retorna o primeiro elemento da lista
    def next(self) -> List:
        return self.list.pop(0)

    def length(self) -> int:
        return len(self.list)

    # Insere no final da lista (fila)
    def add(self, data: Client):
        self.list.append(data)
