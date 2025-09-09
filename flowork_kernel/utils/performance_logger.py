#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\utils\performance_logger.py
# JUMLAH BARIS : 31
#######################################################################

import time
from functools import wraps
def log_performance(log_message: str):
    """
    A decorator that logs the execution time of a function.
    It accesses the api_client logger through the 'self' argument of the decorated method.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0] if args else None
            logger = print # Default to print
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            log_entry = f"PERF-GUI: {log_message} - Execution Time: {duration_ms:.2f} ms" # English Hardcode
            if logger:
                logger(log_entry)
            else:
                print(log_entry) # Fallback
            return result
        return wrapper
    return decorator
