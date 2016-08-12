import time
from functools import wraps, partial

def attach_wrapper(obj, func=None):
    if func is None:
        return partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func

def time_cost(f):
    '''Decorator that calculate time cost'''
    verbose = True
    @wraps(f)
    def time_cost_wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        if verbose:
            print("time cost for {} is {}".format(f.__name__, end-start))
        return result

    @attach_wrapper(time_cost_wrapper)
    def set_verbose():
        nonlocal verbose
        verbose = True

    @attach_wrapper(time_cost_wrapper)
    def clr_verbose():
        nonlocal verbose
        verbose = False

    return time_cost_wrapper
