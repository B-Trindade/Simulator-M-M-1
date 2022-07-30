from enum import Enum


class EventType(Enum):
    Arrival = 1
    Departure = 2


class Event:
    def __init__(self, time, type: EventType):
        self.time = time
        self.event_type = type


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class Event_list:
    '''Lista duplamente encadeada, mantém a lista de eventos em ordem crescente'''

    def __init__(self):
        self.head = None
        self.length = 0

    # Insere eventos mantendo ordem crescente de tempo
    def insert(self, NewEvent: Event):
        self.length += 1
        NewNode = Node(NewEvent)

        if self.head is None:
            self.head = NewNode
            return

        node = self.head
        last = None
        while node is not None:
            if node.data.time > NewEvent.time:
                NewNode.next = node
                if node.prev is not None:
                    node.prev.next = NewNode
                    NewNode.prev = node.prev
                else:
                    self.head = NewNode
                node.prev = NewNode
                return
            last = node
            node = node.next

        NewNode.prev = last
        last.next = NewNode
        return

    def get_first(self) -> Event:
        return self.head.data

    def pop(self) -> Event:
        self.length -= 1
        val = self.head.data
        next = self.head.next
        if next is not None:
            next.prev = None

        del(self.head)
        self.head = next

        return val

    # Printa todos os elementos da lista
    def print_all(self):
        node = self.head
        while (node is not None):
            print(f"{node.data.time} - {node.data.event_type}")
            node = node.next


def exemplo():
    eventos = Event_list()
    eventos.insert_event(Event(4, "um"))
    eventos.insert_event(Event(5, "um"))
    eventos.insert_event(Event(2, "um"))
    eventos.insert_event(Event(1, "um"))
    eventos.insert_event(Event(6, "um"))
    eventos.insert_event(Event(7, "dois"))
    eventos.insert_event(Event(1.8, "dois"))

    eventos.print_all()
    print()

    while eventos.length > 0:
        print("Pop: ", eventos.pop().time)


if __name__ == "__main__":
    exemplo()
