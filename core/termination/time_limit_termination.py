import time


def time_limit_termination(self):
    """Завершается, когда прошло заданное время."""
    time_limit = self.termination_kwargs.get("time_limit")

    time_limit = float(time_limit) if time_limit else None

    start_time = self.termination_kwargs["start_time"]

    return (time.time() - start_time) >= time_limit