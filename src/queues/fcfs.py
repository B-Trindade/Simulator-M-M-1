class FCFSQueue:
    def __init__(self):
        self.list = []

    # Remove e retorna o primeiro elemento da lista
    def next(self):
        return self.list.pop(0)

    def length(self):
        return len(self.list)

    # Insere no final da lista (fila)
    def add(self, data):
        self.list.append(data)
        return
