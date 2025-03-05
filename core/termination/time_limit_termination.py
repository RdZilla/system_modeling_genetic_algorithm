import time


def time_limit_termination(self):
    """Завершается, когда прошло заданное время."""
    start_time = self.termination_kwargs.get("start_time")
    time_limit = self.termination_kwargs.get("time_limit")

    return (time.time() - start_time) >= time_limit