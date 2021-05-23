""" Модуль логики связанной с экранами 'СПРАВОЧНИКИ'
    и всем, что связано с услугами для клиентов. """

import datetime
from typing import Union

from django.http import HttpRequest
from dateutil.relativedelta import relativedelta

from accounting_system.models import Service, Client, CashMachine, ECP, OFD, FN, TO
from accounting_system.services import constants, common_utils


# ЛОГИКА СВЯЗАННАЯ С СОХРАНЕНИЕМ УСЛУГИ


def create_service_for_client(request: HttpRequest) -> None:
    """ Функция - определитель сценария сохранения.
        Проверяет наличия id кассового оборудования, в случае его наличия - вызывает
        функцию сохранения услуги с привиязкой услуг к кассе, иначе сохранет каждую
        услугу индивидуально. """
    if request.POST.get('cash_machine_pk'):
        save_service_with_cash_machine(request)
    else:
        save_service_without_cash_machine(request)


def save_service_with_cash_machine(request: HttpRequest) -> None:
    """ Функция сохранения услуги при условии наличия кассы. """
    p: dict = request.POST
    client_pk: str = p.get('client_pk')
    client: Client = Client.objects.get(pk=client_pk)

    cash_machine_pk: str = p.get('cash_machine_pk')
    factory_number: str = p.get('factory_number')
    cash_machine: CashMachine = CashMachine.objects.get(pk=cash_machine_pk) if cash_machine_pk else None

    ecp_pk: str = p.get('ecp_pk')
    ecp: ECP = ECP.objects.get(pk=ecp_pk) if ecp_pk else None
    ecp_add_date: str = p.get('add_ecp_date') if p.get('add_ecp_date') else None
    ecp_expiration_date: datetime = get_expiration_date(ecp_pk, 'ecp', ecp_add_date) if ecp_add_date else None
    ecp_days_to_finish: int = common_utils.get_days_to_finish(ecp_expiration_date) if ecp_expiration_date else None
    ecp_status: str = common_utils.get_service_status(ecp_days_to_finish) if ecp_expiration_date else None

    ofd_pk: str = p.get('ofd_pk')
    ofd: OFD = OFD.objects.get(pk=ofd_pk) if ofd_pk else None
    ofd_add_date: str = p.get('add_ofd_date') if p.get('add_ofd_date') else None
    ofd_expiration_date: datetime = get_expiration_date(ofd_pk, 'ofd', ofd_add_date) if ofd_add_date else None
    ofd_days_to_finish: int = common_utils.get_days_to_finish(ofd_expiration_date) if ofd_expiration_date else None
    ofd_status: str = common_utils.get_service_status(ofd_days_to_finish) if ofd_expiration_date else None

    fn_pk: str = p.get('fn_pk')
    fn: FN = FN.objects.get(pk=fn_pk) if fn_pk else None
    fn_add_date: str = p.get('add_fn_date') if p.get('add_fn_date') else None
    fn_expiration_date: datetime = get_expiration_date(fn_pk, 'fn', fn_add_date) if fn_add_date else None
    fn_days_to_finish: int = common_utils.get_days_to_finish(fn_expiration_date) if fn_expiration_date else None
    fn_status: str = common_utils.get_service_status(fn_days_to_finish) if fn_expiration_date else None

    to_pk: str = p.get('to_pk')
    to: TO = TO.objects.get(pk=to_pk) if to_pk else None
    to_add_date: str = p.get('add_to_date') if p.get('add_to_date') else None
    to_expiration_date: datetime = get_expiration_date(to_pk, 'to', to_add_date) if to_add_date else None
    to_days_to_finish: int = common_utils.get_days_to_finish(to_expiration_date) if to_expiration_date else None
    to_status: str = common_utils.get_service_status(to_days_to_finish) if to_expiration_date else None

    service: Service = Service(client=client, cash_machine=cash_machine, factory_number=factory_number,
                               ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                               ecp_days_to_finish=ecp_days_to_finish, ecp_status=ecp_status,
                               ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                               ofd_days_to_finish=ofd_days_to_finish, ofd_status=ofd_status,
                               fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                               fn_days_to_finish=fn_days_to_finish, fn_status=fn_status,
                               to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date,
                               to_days_to_finish=to_days_to_finish, to_status=to_status, )
    service.save()


def save_service_without_cash_machine(request: HttpRequest) -> None:
    """ Функция сохранения услуги БЕЗ кассы. """
    client_pk: str = request.POST.get('client_pk')
    if ecp_pk := request.POST.get('ecp_pk'):
        ecp_add_date: str = request.POST.get('add_ecp_date')
        save_ecp_service(client_pk, ecp_pk, ecp_add_date)
    if ofd_pk := request.POST.get('ofd_pk'):
        ofd_add_date: str = request.POST.get('add_ofd_date')
        save_ofd_service(client_pk, ofd_pk, ofd_add_date)
    if fn_pk := request.POST.get('fn_pk'):
        fn_add_date: str = request.POST.get('add_fn_date')
        save_fn_service(client_pk, fn_pk, fn_add_date)
    if to_pk := request.POST.get('to_pk'):
        to_add_date: str = request.POST.get('add_to_date')
        save_to_service(client_pk, to_pk, to_add_date)


def save_ecp_service(client_pk: str, ecp_pk: str, ecp_add_date: str) -> None:
    """ Сохранение услуги ЭЦП как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    ecp: ECP = ECP.objects.get(pk=ecp_pk)
    ecp_expiration_date: datetime = get_expiration_date(ecp_pk, 'ecp', ecp_add_date)
    ecp_days_to_finish: int = common_utils.get_days_to_finish(ecp_expiration_date)
    ecp_status: str = common_utils.get_service_status(ecp_days_to_finish)
    save_service(client=client, ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                 ecp_days_to_finish=ecp_days_to_finish, ecp_status=ecp_status)


def save_ofd_service(client_pk: str, ofd_pk: str, ofd_add_date: str) -> None:
    """ Сохранение услуги ОФД как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    ofd: OFD = OFD.objects.get(pk=ofd_pk)
    ofd_expiration_date: datetime = get_expiration_date(ofd_pk, 'ofd', ofd_add_date)
    ofd_days_to_finish: int = common_utils.get_days_to_finish(ofd_expiration_date)
    ofd_status: str = common_utils.get_service_status(ofd_days_to_finish)
    save_service(client=client, ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                 ofd_days_to_finish=ofd_days_to_finish, ofd_status=ofd_status)


def save_fn_service(client_pk: str, fn_pk: str, fn_add_date: str) -> None:
    """ Сохранение услуги ФН как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    fn: FN = FN.objects.get(pk=fn_pk)
    fn_expiration_date: datetime = get_expiration_date(fn_pk, 'fn', fn_add_date)
    fn_days_to_finish: int = common_utils.get_days_to_finish(fn_expiration_date)
    fn_status: str = common_utils.get_service_status(fn_days_to_finish)
    save_service(client=client, fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                 fn_days_to_finish=fn_days_to_finish, fn_status=fn_status)


def save_to_service(client_pk: str, to_pk: str, to_add_date: str):
    """ Сохранение услуги ТО как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    to: TO = TO.objects.get(pk=to_pk)
    to_expiration_date: datetime = get_expiration_date(to_pk, 'to', to_add_date)
    to_days_to_finish: int = common_utils.get_days_to_finish(to_expiration_date)
    to_status: str = common_utils.get_service_status(to_days_to_finish)
    save_service(client=client, to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date,
                 to_days_to_finish=to_days_to_finish, to_status=to_status)


def save_service(client=None, cash_machine=None, factory_number=None,
                 ecp=None, ecp_add_date=None, ecp_expiration_date=None, ecp_days_to_finish=None, ecp_status=None,
                 ofd=None, ofd_add_date=None, ofd_expiration_date=None, ofd_days_to_finish=None, ofd_status=None,
                 fn=None, fn_add_date=None, fn_expiration_date=None, fn_days_to_finish=None, fn_status=None,
                 to=None, to_add_date=None, to_expiration_date=None, to_days_to_finish=None, to_status=None) -> None:
    """ Сохранение услуги, принимает входные данные от одной из функций
        (save_ecp_service, save_ofd_service, save_fn_service, save_to_service)
        сохраняет как отдельную услугу заполняя пустые поля значениями None. """
    service = Service(client=client, cash_machine=cash_machine, factory_number=factory_number,
                      ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                      ecp_days_to_finish=ecp_days_to_finish, ecp_status=ecp_status,
                      ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                      ofd_days_to_finish=ofd_days_to_finish, ofd_status=ofd_status,
                      fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                      fn_days_to_finish=fn_days_to_finish, fn_status=fn_status,
                      to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date,
                      to_days_to_finish=to_days_to_finish, to_status=to_status)
    service.save()


def get_expiration_date(service_pk: str, service_type: str, add_date: str) -> datetime:
    """ Функция получения даты окончания действия услуги. """
    service: Union[ECP, OFD, FN, TO] = constants.SERVICE_TYPE_DICT[service_type].objects.get(pk=service_pk)
    validity: int = service.validity
    day: int = int(add_date[8:10])
    month: int = int(add_date[5:7])
    year: int = int(add_date[0:4])
    datetime_add_date: datetime = datetime.date(year, month, day)
    return datetime_add_date + relativedelta(months=validity)


# ЛОГИКА СВЯЗАННАЯ С ИЗМЕНЕНИЕМ УСЛУГИ


def make_changes_to_the_service(request: HttpRequest) -> None:
    """ Функция внесения изменений в существующую услугу для клиента. """
    p: dict = request.POST
    cash_machine_pk: str = p.get('cash_machine_pk')
    ecp_pk: str = p.get('ecp_pk')
    ofd_pk: str = p.get('ofd_pk')
    fn_pk: str = p.get('fn_pk')
    to_pk: str = p.get('to_pk')
    service = Service.objects.get(pk=p.get('service_pk'))

    service.cash_machine = CashMachine.objects.get(pk=cash_machine_pk) if cash_machine_pk else None
    service.factory_number = p.get('factory_number')

    service.ecp = ECP.objects.get(pk=ecp_pk) if ecp_pk else None
    service.ecp_add_date = p.get('add_ecp_date') if p.get('add_ecp_date') else None
    service.ecp_expiration_date = get_expiration_date(
        ecp_pk, 'ecp', service.ecp_add_date) if service.ecp_add_date else None
    service.ecp_days_to_finish = common_utils.get_days_to_finish(
        service.ecp_expiration_date) if service.ecp_expiration_date else None
    service.ecp_status = common_utils.get_service_status(
        service.ecp_days_to_finish) if service.ecp_expiration_date else None

    service.ofd = OFD.objects.get(pk=ofd_pk) if ofd_pk else None
    service.ofd_add_date = p.get('add_ofd_date') if p.get('add_ofd_date') else None
    service.ofd_expiration_date = get_expiration_date(
        ofd_pk, 'ofd', service.ofd_add_date) if service.ofd_add_date else None
    service.ofd_days_to_finish = common_utils.get_days_to_finish(
        service.ofd_expiration_date) if service.ofd_expiration_date else None
    service.ofd_status = common_utils.get_service_status(
        service.ofd_days_to_finish) if service.ofd_expiration_date else None

    service.fn = FN.objects.get(pk=fn_pk) if fn_pk else None
    service.fn_add_date = p.get('add_fn_date') if p.get('add_fn_date') else None
    service.fn_expiration_date = get_expiration_date(
        fn_pk, 'fn', service.fn_add_date) if service.fn_add_date else None
    service.fn_days_to_finish = common_utils.get_days_to_finish(
        service.fn_expiration_date) if service.fn_expiration_date else None
    service.fn_status = common_utils.get_service_status(
        service.fn_days_to_finish) if service.fn_expiration_date else None

    service.to = TO.objects.get(pk=to_pk) if to_pk else None
    service.to_add_date = p.get('add_to_date') if p.get('add_to_date') else None
    service.to_expiration_date = get_expiration_date(
        to_pk, 'to', service.to_add_date) if service.to_add_date else None
    service.to_days_to_finish = common_utils.get_days_to_finish(
        service.to_expiration_date) if service.to_expiration_date else None
    service.to_status = common_utils.get_service_status(
        service.to_days_to_finish) if service.to_expiration_date else None
    service.save()
