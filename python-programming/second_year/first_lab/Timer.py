import traceback
from time import perf_counter


class Timer:
    def __init__(self, name: str, logger=print):
        self.name = name
        self.logger = logger
        self.timer = None

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter()
        self.timer = self.end - self.start
        self.logger(f"Time of task {self.name}: {self.timer}")

        if exc_type is not None:
            self.logger(
                f"ooops, u stupid \n {''.join(traceback.format_exception(exc_type, exc_val, exc_tb))}"
            )
