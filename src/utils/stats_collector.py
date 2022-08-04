
class Client:
    def __init__(self, id: int, entry_time: float, batch: int):
        self.id = id
        self.batch_id = batch
        self.entry_time = entry_time
        self.wait_time = 0
        self.exit_time = 0

    def set_entry_time(self, num: float) -> None:
        self.entry_time = num

    def set_wait_time(self, num: float) -> None:
        self.wait_time = num

    def set_exit_time(self, num: float) -> None:
        self.exit_time = num

class StatsCollector:
    def __init__(self):
        self.total_wait = 0
        self.total_wait_squared = 0
        self.total_queue_size = 0
        self.total_queue_size_squared = 0
        self.total_samples = 0

    def update_departures(self, client: Client, queue_size: int) -> None:
        self.total_wait += client.wait_time
        self.total_wait_squared += client.wait_time**2

        self.total_queue_size += queue_size
        self.total_queue_size_squared += queue_size**2

        self.total_samples += 1

    def get_average_wait(self) -> float:
        return self.total_wait/self.total_samples

    def get_variance_wait(self) -> float:
        return self.total_wait_squared/(self.total_samples-1) - self.total_wait**2/(self.total_samples*(self.total_samples-1))

    def get_average_queue_size(self) -> float:
        return self.total_queue_size/self.total_samples

    def get_variance_queue_size(self) -> float:
        return self.total_queue_size_squared/(self.total_samples-1) - self.total_queue_size**2/(self.total_samples*(self.total_samples-1))
