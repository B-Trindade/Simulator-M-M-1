class LCFSQueue:
    def __init__(self):
        self.list = []

    # Remove e retorna o último elemento da lista
    def next(self):
        return self.list.pop()

    def length(self):
        return len(self.list)

    # Insere no início da lista (pilha)
    def add(self, data):
        self.list.append(data)
        return
