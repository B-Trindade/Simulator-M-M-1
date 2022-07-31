from utils import random_generator
from utils.event_list import EventList, Event, EventType
from utils.stats_collector import Client, StatsCollector
from queues.fcfs import FCFSQueue
from queues.lcfs import LCFSQueue
from sys import argv, exit
from os import environ


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
        print(f"seed: {self.seed}\n")

        self.time = 0

        self.event_list = EventList()
        self.stats_collector = StatsCollector()

        self.queue = FCFSQueue() if self.queue_type.lower() == "fcfs" else LCFSQueue()

        self.arrival_generator = random_generator.Exponential(
            self.seed, self.rho)
        self.departure_generator = random_generator.Exponential(self.seed, 1)

    def next_arrival(self):
        return self.time + self.arrival_generator.next()

    def next_departure(self):
        return self.time + self.departure_generator.next()

    def add_event(self, event_type: EventType):
        '''Calcula o tempo do próximo evento e insere na fila de eventos'''
        if event_type == EventType.Arrival:
            self.event_list.insert(Event(self.next_arrival(), event_type))
        else:
            self.event_list.insert(Event(self.next_departure(), event_type))

    def run(self):
        departures = 0
        id = 0
        # Calcula a primeira chegada antes do loop
        self.add_event(EventType.Arrival)
        current_client = None   # current_client indica o cliente atualmente em execução

        while departures < self.num_customers:
            # Pega o próximo evento da lista de eventos
            next_event = self.event_list.pop()

            # Avança o tempo até o próximo evento
            time_diff = (next_event.time - self.time)
            self.time += time_diff

            # Trata eventos de chegada
            if next_event.event_type == EventType.Arrival:
                id += 1

                # Se a fila estiver vazia, chegada vai direto para execução
                if current_client is None:
                    if(environ.get("DEBUG") == "true"):
                        print(
                            f"Entrou o id {id} no tempo {round(self.time, 3)} - FILA DE ESPERA VAZIA")

                    # Calcula a saída do cliente que acabou de chegar
                    self.add_event(EventType.Departure)
                    current_client = Client(id, self.time)
                    # Tempo de espera = 0 pois já entrou direto em execução
                    current_client.set_wait_time(0)

                # Se não, insere na fila de espera para ser executado no futuro
                else:
                    if(environ.get("DEBUG") == "true"):
                        print(
                            f"Entrou o id {id} no tempo {round(self.time, 3)} - Encontrou {self.queue.length()} pessoas na fila de espera")
                    self.queue.add(Client(id, self.time))

                # Se o event sendo tratado é uma chegada, calcula o tempo da próxima chegada
                self.add_event(EventType.Arrival)

            # Trata eventos de saída
            if next_event.event_type == EventType.Departure:
                departures += 1
                leaving_client = current_client
                leaving_client.set_exit_time(self.time)

                # Para cálculos da média de Ns, vemos como ficará a fila de espera
                # após a saída do cliente atual:
                # Fila vazia → utilização 0
                # Fila não-vazia → utilização 1
                # NOTA: Este valor equivale a rho (ρ)
                self.stats_collector.update_utilization(self.queue.length())

                if(environ.get("DEBUG") == "true"):
                    print(
                        f"Saiu o id {leaving_client.id} no tempo {round(leaving_client.exit_time, 3)}")
                    print(f"Entry - {round(leaving_client.entry_time, 3)}")
                    print(f"Wait - {round(leaving_client.wait_time, 3)}")
                    print(f"Exit - {round(leaving_client.exit_time, 3)}")

                # Caso onde ainda há clientes na fila de espera para serem processados após a saída
                if self.queue.length() > 0:
                    current_client = self.queue.next()
                    current_client.set_wait_time(
                        self.time - current_client.entry_time)

                    # Calcula o tempo da próxima saída
                    self.add_event(EventType.Departure)
                    if(environ.get("DEBUG") == "true"):
                        print(
                            f"Cliente {current_client.id} entrou em execução no tempo {round(self.time, 3)}\n")

                # Caso onde após saída, o sistema fica vazio
                else:
                    current_client = None
                    if(environ.get("DEBUG") == "true"):
                        print()

                # Coleção de dados de saída
                # Coleta o tamanho da fila de espera e o tempo de espera do
                # cliente que acabou de sair
                self.stats_collector.update_departures(
                    leaving_client, self.queue.length())

        return self.stats_collector


if __name__ == "__main__":
    a = Simulator(argv)
    stats = a.run()
    print(f"E[W]: {round(stats.get_average_wait(), 3)}")
    print(f"E[Nq]: {round(stats.get_average_queue_size(), 3)}")
    print(f"E[Ns]: {round(stats.get_average_utilization(), 3)}\n")

    print("Little:")
    print(f"E[Nq] = λE[W]")
    print(
        f"{round(stats.get_average_queue_size(), 3)} = {argv[3]}*{round(stats.get_average_wait(), 3)}")
    print(
        f"{round(stats.get_average_queue_size(), 3)} = {round(float(argv[3])*stats.get_average_wait(), 3)}")
