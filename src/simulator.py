from enum import Enum
from utils.random_generator import Exponential
from utils.event_list import EventList, Event, EventType
from utils.stats_collector import Client, StatsCollector
from queues.fcfs import FCFSQueue
from queues.lcfs import LCFSQueue
from sys import argv, exit
from os import environ
from typing import List, Tuple
from datetime import datetime


class Phase(Enum):
    Transient = 0
    Stable = 1


class Simulator:
    def __init__(self, argv: List):
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
        self.current_client = None   # current_client indica o cliente atualmente em execução

        self.event_list = EventList()
        self.stats_collector = StatsCollector()

        self.queue = FCFSQueue() if self.queue_type.lower() == "fcfs" else LCFSQueue()

        self.arrival_generator = Exponential(
            self.seed, self.rho)
        self.departure_generator = Exponential(self.seed, 1)

    def next_arrival(self) -> float:
        return self.time + self.arrival_generator.next()

    def next_departure(self) -> float:
        return self.time + self.departure_generator.next()

    def add_event(self, event_type: EventType) -> None:
        '''Calcula o tempo do próximo evento e insere na fila de eventos'''
        if event_type == EventType.Arrival:
            self.event_list.insert(Event(self.next_arrival(), event_type))
        else:
            self.event_list.insert(Event(self.next_departure(), event_type))

    def run(self, client, batch: int = 0) -> Tuple[StatsCollector, int, Client]:
        self.stats_collector = StatsCollector()
        self.time = 0
        stable_departures = 0
        total_departures = 0
        id = 0

        state = Phase.Stable
        # Médias relativas à fase transiente
        total_departure_time = 0
        avg_departure_time_samples = 0
        avg_departure_times = []

        # Calcula a primeira chegada antes do loop
        if batch == 0:
            state = Phase.Transient
            self.add_event(EventType.Arrival)
        # current_client indica o cliente atualmente em execução
        self.current_client = client

        while stable_departures < self.num_customers:
            # Pega o próximo evento da lista de eventos
            next_event = self.event_list.pop()

            # Avança o tempo até o próximo evento
            time_diff = (next_event.time - self.time)
            self.time += time_diff

            # Trata eventos de chegada
            if next_event.event_type == EventType.Arrival:
                id += 1

                # Se a fila estiver vazia, chegada vai direto para execução
                if self.current_client is None:
                    if(environ.get("DEBUG") == "true"):
                        print(
                            f"Entrou o id {id} no tempo {round(self.time, 3)} - FILA DE ESPERA VAZIA")

                    # Calcula a saída do cliente que acabou de chegar
                    self.add_event(EventType.Departure)
                    self.current_client = Client(id, self.time, batch)
                    # Tempo de espera = 0 pois já entrou direto em execução
                    self.current_client.set_wait_time(0)

                # Se não, insere na fila de espera para ser executado no futuro
                else:
                    if(environ.get("DEBUG") == "true"):
                        print(
                            f"Entrou o id {id} no tempo {round(self.time, 3)} - Encontrou {self.queue.length()} pessoas na fila de espera")
                    self.queue.add(Client(id, self.time, batch))

                # Se o event sendo tratado é uma chegada, calcula o tempo da próxima chegada
                self.add_event(EventType.Arrival)

            # Trata eventos de saída
            if next_event.event_type == EventType.Departure:
                leaving_client = self.current_client
                leaving_client.set_exit_time(self.time)

                total_departures += 1

                # Para cálculos da média de Ns, vemos como ficará a fila de espera
                # após a saída do cliente atual:
                # Fila vazia → utilização 0
                # Fila não-vazia → utilização 1
                # NOTA: Este valor equivale a rho (ρ)
                if leaving_client.batch_id == batch and state == Phase.Stable:
                    stable_departures += 1
                    self.stats_collector.update_utilization(
                        self.queue.length())

                if environ.get("DEBUG") == "true":
                    print(
                        f"Saiu o id {leaving_client.id} no tempo {round(leaving_client.exit_time, 3)}")
                    print(f"Entry - {round(leaving_client.entry_time, 3)}")
                    print(f"Wait - {round(leaving_client.wait_time, 3)}")
                    print(f"Exit - {round(leaving_client.exit_time, 3)}")

                # Caso onde ainda há clientes na fila de espera para serem processados após a saída
                if self.queue.length() > 0:
                    self.current_client = self.queue.next()
                    self.current_client.set_wait_time(
                        self.time - self.current_client.entry_time)

                    # Calcula o tempo da próxima saída
                    self.add_event(EventType.Departure)
                    if(environ.get("DEBUG") == "true"):
                        print(
                            f"Cliente {self.current_client.id} entrou em execução no tempo {round(self.time, 3)}\n")

                # Caso onde após saída, o sistema fica vazio
                else:
                    self.current_client = None
                    if(environ.get("DEBUG") == "true"):
                        print()

                # Coleção de dados de saída
                # Coleta o tamanho da fila de espera e o tempo de espera do
                # cliente que acabou de sair
                if leaving_client.batch_id == batch and state == Phase.Stable:
                    self.stats_collector.update_departures(
                        leaving_client, self.queue.length())

                # Durante a fase transiente, é repetidamente calculada a média do tempo de espera
                # das últimas 10 mil saídas. Após termos as últimas 10 médias salvas,
                # calculamos a diferença entre a média das duas médias mais recentes com as
                # médias restantes. Se a diferença der menor que 1%, a fase transiente é encerrada.
                # Se não, continuamos o cálculo a cada média nova calculada, mantendo sempre as 10 últimas.
                if state == Phase.Transient:
                    total_departure_time += leaving_client.wait_time
                    avg_departure_time_samples += 1

                    if avg_departure_time_samples == 10000:
                        last_averages = [total_departure_time/avg_departure_time_samples] + (
                            [avg_departure_times.pop()] if len(avg_departure_times) > 0 else [])
                        avg_departure = sum(last_averages)/len(last_averages)
                        if len(avg_departure_times) >= 9 and avg_departure >= 0.99*sum(avg_departure_times)/(len(avg_departure_times)) and avg_departure <= 1.01*sum(avg_departure_times)/(len(avg_departure_times)):
                            # if total_departures >= 100000:
                            state = Phase.Stable
                            print(
                                f"Fase transiente acabou após {total_departures} saídas\n")
                        else:
                            avg_departure_times.extend(last_averages[::-1])
                            if len(avg_departure_times) > 10:
                                avg_departure_times.pop(0)

                        total_departure_time = 0
                        avg_departure_time_samples = 0

        return self.stats_collector, batch+1, self.current_client


if __name__ == "__main__":
    inicio = datetime.now()
    a = Simulator(argv)
    next_batch = 0
    max_batches = 100

    total_wait = 0
    total_queue = 0

    file_name = f"results_{'-'.join(argv[1:])}".replace('.', ',')
    with open(f"{file_name}.csv", "w") as file:
        client = None
        file.write("Batch, E[W], E[Nq], E[Ns]\n")
        while next_batch < max_batches:
            stats, next_batch, client = a.run(client, batch=next_batch)
            # print(f"\n\nCURRENT BATCH: {next_batch}")
            # print(f"E[W]: {round(stats.get_average_wait(), 3)}")
            # print(f"E[Nq]: {round(stats.get_average_queue_size(), 3)}")
            # print(f"E[Ns]: {round(stats.get_average_utilization(), 3)}\n")

            # print("Little:")
            # print(f"E[Nq] = λE[W]")
            # print(
            #     f"{round(stats.get_average_queue_size(), 3)} = {argv[3]}*{round(stats.get_average_wait(), 3)}")
            # print(
            #     f"{round(stats.get_average_queue_size(), 3)} = {round(float(argv[3])*stats.get_average_wait(), 3)}\n")
            total_wait += stats.get_average_wait()
            total_queue += stats.get_average_queue_size()
            file.write(
                f"{next_batch},{stats.get_average_wait()},"
                f"{stats.get_average_queue_size()},{stats.get_average_utilization()}\n"
            )

    print("Médias das rodadas:")
    print(f"E[W] = {round(total_wait/max_batches, 3)}")
    print(f"E[Nq] = {round(total_queue/max_batches, 3)}\n")

    print("Little:")
    print(f"E[Nq] = λE[W]")
    print(
        f"{round(total_queue/max_batches, 3)} = {argv[3]}*{round(total_wait/max_batches, 3)}")
    print(
        f"{round(total_queue/max_batches, 3)} = {round(float(argv[3])*(total_wait/max_batches), 3)}\n")

    print(f'{(datetime.now() - inicio).total_seconds()}s')
