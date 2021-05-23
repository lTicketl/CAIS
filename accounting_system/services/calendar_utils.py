""" Модуль логики связанной с экраном 'КАЛЕНДАРЬ'. """

from typing import List

from django.db.models import F

from accounting_system.models import Manager, Service


def get_event_list(manager: Manager) -> List[dict]:
    event_list: List[dict] = []
    if manager.is_staff:
        services_queryset = Service.objects.filter(active=True, client__active=True).annotate(
            client_name=F('client__organization_name'), ecp_name=F('ecp__name'),
            ofd_name=F('ofd__model'), fn_name=F('fn__name'), to_name=F('to__name'))
    else:
        services_queryset = Service.objects.filter(active=True, client__active=True,
            client__manager=manager.pk).annotate(client_name=F('client__organization_name'),
            ecp_name=F('ecp__name'), ofd_name=F('ofd__model'), fn_name=F('fn__name'), to_name=F('to__name'))

    for service in services_queryset:
        if service.ecp_expiration_date:
            event_list.append({'date': str(service.ecp_expiration_date) + ' 00:00:00',
                               'title': service.client_name, 'description': service.ecp_name})
        if service.ofd_expiration_date:
            event_list.append({'date': str(service.ofd_expiration_date) + ' 00:00:00',
                               'title': service.client_name, 'description': service.ofd_name})
        if service.fn_expiration_date:
            event_list.append({'date': str(service.fn_expiration_date) + ' 00:00:00',
                               'title': service.client_name, 'description': service.fn_name})
        if service.to_expiration_date:
            event_list.append({'date': str(service.to_expiration_date) + ' 00:00:00',
                               'title': service.client_name, 'description': service.to_name})
    return event_list
