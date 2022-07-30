from datetime import datetime
from utils import random_generator
from utils.event_list import Event_list, Event, EventType
from queues.fcfs import FCFSQueue
from queues.lcfs import LCFSQueue
from sys import argv, exit

class Client:
    def __init__(self, id, entry_time):
        self.id = id
        self.entry_time = entry_time
        self.wait_time = 0
        self.exit_time = 0

    def set_entry_time(self, num: float):
        self.entry_time = num
        
    def set_wait_time(self, num: float):
        self.wait_time = num

    def set_exit_time(self, num: float):
        self.exit_time = num


class Simulator:
    def __init__(self, argv):
        if len(argv)-1 not in (3, 4):
            print("Número errado de argumentos :(")
            exit(1)

        self.queue_type = argv[1]
        self.num_customers = int(argv[2])
        self.rho = float(argv[3])
        self.seed = int(argv[4]) if len(argv)-1 >= 4 else None

        print(f"Queue type: {self.queue_type}")
        print(f"Num fregueses: {self.num_customers}")
        print(f"Rho: {self.rho}")
        print(f"seed: {self.seed}")

        self.time = 0
        self.event_list = Event_list()
        self.queue = FCFSQueue() if self.queue_type.lower() == "fcfs" else LCFSQueue()
        self.arrival_generator = random_generator.Exponential(
            self.seed, self.rho)
        self.departure_generator = random_generator.Exponential(self.seed, 1)

    def next_arrival(self):
        return self.time + self.arrival_generator.next()

    def next_departure(self):
        return self.time + self.departure_generator.next()

    def add_event(self, event_type: EventType):
        if event_type == EventType.Arrival:
            self.event_list.insert(Event(self.next_arrival(), event_type))
        else:
            self.event_list.insert(Event(self.next_departure(), event_type))

    def run(self):
        departures = 0
        id = 0
        self.add_event(EventType.Arrival)

        while departures < self.num_customers:
            next_event = self.event_list.pop()

            # Avança o tempo até o próximo evento
            time_diff = (next_event.time - self.time)
            self.time += time_diff

            self.record_statistics(next_event)  # TODO SALVAR AS ESTATÍSTICAS

            # Trata eventos de chegada
            if next_event.event_type == EventType.Arrival:
                id += 1
                print(f"Entrou o id {id} no tempo {round(self.time, 3)}")

                # Se a fila estiver vazia, chegada vai direto para execução
                if not self.queue.length():
                    self.add_event(EventType.Departure)

                # Insere na fila
                self.queue.add(Client(id, self.time))
                # self.queue.add(id)

                # Se o event sendo tratado é uma chegada, calcula o tempo da próxima chegada
                self.add_event(EventType.Arrival)

            # Trata eventos de saída
            if next_event.event_type == EventType.Departure:
                departures += 1
                # Calcula o tempo da próxima saída
                # departure_id = self.queue.next().id
                leaving_client = self.queue.next()
                leaving_client.set_exit_time(self.time)
                print(f"Saiu o id {leaving_client.id} no tempo {round(leaving_client.exit_time, 3)}")

                if self.queue.length() > 0:
                    self.add_event(EventType.Departure)

    def record_statistics(self, event: Event):
        pass


if __name__ == "__main__":
    a = Simulator(argv)
    a.run()
