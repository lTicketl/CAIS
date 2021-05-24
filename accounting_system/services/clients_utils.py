from typing import Any
from django.http import HttpRequest
from accounting_system.models import TsRequest, Manager, ServiceInfo


def get_clients_queryset():
    clients_queryset = Manager.objects.filter(is_staff=False)
    return clients_queryset


def get_workers_queryset():
    workers_queryset = Manager.objects.filter(is_staff=True)
    return workers_queryset


def get_ts_queryset():
    ts_queryset = TsRequest.objects.filter()
    return ts_queryset


def get_ots_queryset():
    ots_queryset = TsRequest.objects.filter(ts_active=True)
    return ots_queryset


def get_cts_queryset():
    cts_queryset = TsRequest.objects.filter(ts_active=False)
    return cts_queryset


def get_service_info_queryset() -> Any:
    service_queryset = ServiceInfo.objects.filter(active=True)
    return service_queryset


def get_filtered_clients(request: HttpRequest) -> Any:
    """ Функция поиска клиентов по id. """
    client_pk: str = request.POST.get('search_input')
    pk = int(client_pk)
    clients_queryset = Manager.objects.filter(pk=pk)
    return clients_queryset
