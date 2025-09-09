#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\utils\performance_logger.py
# JUMLAH BARIS : 25
#######################################################################

import time
from functools import wraps
def log_performance(log_message: str):
    """
    A decorator that logs the execution time of a function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            log_entry = f"PERF-GUI: {log_message} - Execution Time: {duration_ms:.2f} ms"
            print(log_entry) # Simple print for GUI-side logging
            return result
        return wrapper
    return decorator
