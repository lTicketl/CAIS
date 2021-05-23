import time


def timer(function):
    """ Функция - декоратор для измерения скорости
        выполнения кода в милисекундах. """
    def wrap(*args, **kwargs):
        start = time.time()
        res = function(*args, **kwargs)
        print('Время выполнения:', (time.time() - start) * 1000, 'ms')
        return res
    return wrap
