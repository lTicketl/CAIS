""" Модуль с переиспользуемыми функциями в разных модулях разбитых по категориям. """

import datetime
from typing import Union
import time

from django.http import HttpRequest

from accounting_system.models import CashMachine, ECP, OFD, FN, TO
from accounting_system.services import constants


def get_days_to_finish(expiration_date: datetime) -> int:
    """ Функция получения количества дней до окончания срока действия услуги. """
    return (expiration_date - datetime.date.today()).days


def get_service_status(days_to_finish: int) -> str:
    """ Функция получения статуса услуги в виде строкового кода.
        Отслеживает значение количества дней до окончания услуги и присваивает соответсвующий код.
        Менее 0 дней - код: 'FA' (FAILED)
        Менее 10-ти дней - код: 'AL' (ALARM)
        Менее 30-ти дней - код: 'AT' (ATTENTION)
        Более 30-ти дней - код: 'OK' (OK). """
    if days_to_finish < 0:
        return 'FA'
    if days_to_finish < 10:
        return 'AL'
    elif days_to_finish < 30:
        return 'AT'
    else:
        return 'OK'


def get_service_class_instance(request: HttpRequest) -> Union[CashMachine, ECP, OFD, FN, TO]:
    """ Функция получения типа данных из ОРМ модели. """
    service_type: str = request.POST.get('service_type')
    service_class_instance: Union[CashMachine, ECP, OFD, FN, TO] = constants.SERVICE_TYPE_DICT.get(service_type)
    return service_class_instance


def timer(function):
    """ Функция - декоратор для измерения скорости
        выполнения кода в милисекундах. """
    def wrap(*args, **kwargs):
        start = time.time()
        res = function(*args, **kwargs)
        print('Время выполнения:', (time.time() - start) * 1000, 'ms')
        return res
    return wrap
