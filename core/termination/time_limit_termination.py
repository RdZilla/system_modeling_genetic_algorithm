import time


def time_limit_termination(start_time, time_limit):
    """Завершается, когда прошло заданное время."""
    return (time.time() - start_time) >= time_limit