""" Модуль логики связанной с экраном отображения задач
    для администратора, или менеджера. """

from typing import List

from accounting_system.models import Manager, Service
from accounting_system.services import constants, common_utils


def get_tasks_list(user: Manager, manager_pk_for_filter: str) -> List[Service]:
    """ Функция получения списка услуг, с подходящим к окончанию,
        или истекшим сроком действия услуги.
        Проверяет на отсутсвие статуса 'ОК' в каждой из подуслуг,
        в случае его отсутсвия - добавляет услугу в список task_list. """
    task_list: list = []
    if user.is_staff:
        if manager_pk_for_filter:
            service_queryset = Service.objects.filter(active=True, client__active=True,
                                                      client__manager=manager_pk_for_filter)
        else:
            service_queryset = Service.objects.filter(active=True, client__active=True)
        for service in service_queryset:
            if check_service_overdue(service):
                task_list.append(service)
    else:
        manager_clients_queryset = user.get_clients()
        for client in manager_clients_queryset:
            for service in client.get_services():
                if check_service_overdue(service):
                    task_list.append(service)
    return task_list


def check_service_overdue(service: Service) -> bool:
    """ Функция проверки статуса услуги.
        В случае несовпадения со статусом 'OK' возвращет True. """
    if service.ecp_status and service.ecp_status != 'OK':
        return True
    if service.ofd_status and service.ofd_status != 'OK':
        return True
    if service.fn_status and service.fn_status != 'OK':
        return True
    if service.to_status and service.to_status != 'OK':
        return True
    return False


def update_tasks_status() -> None:
    """ Функция апдейта статусов услуг при входе менеджера в систему. """
    service_queryset = Service.objects.filter(active=True)
    service_objects_list = [update_task(service) for service in service_queryset]
    Service.objects.bulk_update(service_objects_list, constants.UPDATE_FIELD_LIST)


def update_task(service: Service) -> Service:
    """ Функция пересчета и обновления дней до окончания услуги и статуса услуги. """
    if service.ecp_expiration_date:
        service.ecp_days_to_finish = common_utils.get_days_to_finish(service.ecp_expiration_date)
        service.ecp_status = common_utils.get_service_status(service.ecp_days_to_finish)
    if service.ofd_expiration_date:
        service.ofd_days_to_finish = common_utils.get_days_to_finish(service.ofd_expiration_date)
        service.ofd_status = common_utils.get_service_status(service.ofd_days_to_finish)
    if service.fn_expiration_date:
        service.fn_days_to_finish = common_utils.get_days_to_finish(service.fn_expiration_date)
        service.fn_status = common_utils.get_service_status(service.fn_days_to_finish)
    if service.to_expiration_date:
        service.to_days_to_finish = common_utils.get_days_to_finish(service.to_expiration_date)
        service.to_status = common_utils.get_service_status(service.to_days_to_finish)
    return service
