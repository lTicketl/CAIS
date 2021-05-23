""" Модуль логики связанной с экранами 'СОТРУДНИКИ',
    доступному только администратору. """

from typing import Any

from django.db.models import Count, Q

from accounting_system.models import Manager


def get_managers_queryset() -> Any:
    """ Запрос на получение queryset с менеджерами аннотироваными количеством
        задач в работе и количеством проваленных задач. """
    managers_queryset = Manager.objects.filter(
        is_active=True, clients__active=True, clients__services__active=True).annotate(
            count_failed_tasks=Count('clients__services', filter=Q(clients__services__ecp_status='FA')) +
            Count('clients__services', filter=Q(clients__services__ofd_status='FA')) +
            Count('clients__services', filter=Q(clients__services__fn_status='FA')) +
            Count('clients__services', filter=Q(clients__services__to_status='FA')),
            count_tasks=Count('clients__services',
                              filter=Q(clients__services__ecp_status='AL') | Q(clients__services__ecp_status='AT')) +
            Count('clients__services',
                  filter=Q(clients__services__ofd_status='AL') | Q(clients__services__ofd_status='AT')) +
            Count('clients__services',
                  filter=Q(clients__services__fn_status='AL') | Q(clients__services__fn_status='AT')) +
            Count('clients__services',
                  filter=Q(clients__services__to_status='AL') | Q(clients__services__to_status='AT'))
    )
    return managers_queryset
