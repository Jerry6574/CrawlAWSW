import multiprocessing as mp
from functools import partial


def mp_func(func, iterable, sec_arg=None, has_return=True):
    pool = mp.Pool()
    if sec_arg is not None:
        if has_return:
            return pool.map(partial(func, sec_arg), iterable)
        else:
            pool.map(partial(func, sec_arg), iterable)
    else:
        if has_return:
            return pool.map(func, iterable)
        else:
            pool.map(func, iterable)

