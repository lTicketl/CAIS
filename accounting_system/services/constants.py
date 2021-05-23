""" Модуль для хранения констант. """

from typing import List

from accounting_system.models import CashMachine, ECP, OFD, FN, TO


CLIENT_PAGE_LIMIT = 8

SERVICE_TYPE_DICT: dict = {'kkt': CashMachine, 'ecp': ECP, 'ofd': OFD, 'fn': FN, 'to': TO}

UPDATE_FIELD_LIST: List[str] = ['ecp_days_to_finish', 'ecp_status', 'ofd_days_to_finish', 'ofd_status',
                                'fn_days_to_finish', 'fn_status', 'to_days_to_finish', 'to_status']
