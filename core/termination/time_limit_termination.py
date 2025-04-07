import time


def time_limit_termination(self):
    """Завершается, когда прошло заданное время."""
    _ru_function_name = "Завершение по времени"
    _ru_fitness_threshold = "Ограничение времени"

    time_limit = self.termination_kwargs.get("time_limit")

    time_limit = float(time_limit) if time_limit else None

    start_time = self.termination_kwargs["start_time"]

    return (time.time() - start_time) >= time_limit