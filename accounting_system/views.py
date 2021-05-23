from typing import Union

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .forms import (WorkerChangeForm, CustomUserCreationForm, CustomClientCreationForm, ManagerChangeForm, CashMachineCreationForm,
                    FNCreationForm, TOCreationForm, ECPCreationForm, OFDCreationForm)
from .models import ServiceInfo, Tsrequest, ClientInfo, Manager, Client, CashMachine, ECP, OFD, FN, TO, Service
from .services import (constants, clients_utils, managers_utils, tasks_utils,
                       calendar_utils, services_utils, common_utils)


# AUTH


# @receiver(user_logged_in)
# def signal_user_logged_in(sender, user: Manager, request: HttpRequest, **kwargs) -> None:
#     """ Контроллер пересчета и обновления статусов и колчества дней до кончания услуги.
#         Вызывается при логине любого из менеджеров. """
#     tasks_utils.update_tasks_status()


@login_required
def auth(request: HttpRequest) -> HttpResponse:
    """ Контроллер авторизации пользователей. """
    return render(request, 'accounting_system/auth.html', {'form': AuthenticationForm})


@login_required
def main_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/main_page.html', {'form': AuthenticationForm})


@login_required
def cl_acc(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/client_account.html', {'form': AuthenticationForm})


def reg(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/reg.html')


@login_required()
def success_pay(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/success_pay.html')


@login_required()
def tech_support_form(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/tech_support.html')


@login_required()
def tech_support(request: HttpRequest) -> HttpResponse:
    ts_client = request.POST.get('ts_pk')
    user: Manager = get_object_or_404(Manager, pk=ts_client)
    ts_request = Tsrequest(ts_client=user, ts_problem=request.POST.get('ts'))
    ts_request.save()
    return render(request, 'accounting_system/clients/success_ts.html')


@login_required()
def success_ts(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/client_account.html')


def client_info(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/client_info.html')


def success_sc(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/success_sc.html')


def logout_view(request: HttpRequest) -> HttpResponse:
    """ Контроллер выхода из системы. """
    logout(request)
    return redirect('login')


def reg_client(request: HttpRequest) -> HttpResponse:

    if request.method == 'POST':
        form: CustomClientCreationForm = CustomClientCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['cl_username']
            new_user.set_password(form.cleaned_data['cl_password'])
            new_user.save()
            new_user.groups.add(Group.objects.get(name='Clients'))
            return redirect('auth')
    else:
        form = CustomClientCreationForm()
    context: dict = {'page': 'auth', 'form': form, 'user': request.user}
    return render(request, 'accounting_system/reg.html', context)
    # if request.user.is_authenticated:
    #     return redirect('auth')
    #
    # form = CustomClientCreationForm(request.POST or None)
    # if form.is_valid():
    #     new_user = form.save(commit=False)
    #     new_user.email = form.cleaned_data['cl_mail']
    #     new_user.set_password(form.cleaned_data['cl_password'])
    #     new_user.save()
    #     new_user.groups.add(Group.objects.get(name='Clients'))
    # context: dict = {'page': 'auth'}
    # return render(request, 'accounting_system/reg.html', context)

# CLIENTS


def add_client_info(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления клиента.
        Дополнительно передает список из ИНН всех активных клиентов,
        для последующей валидации входных данных фронтендом на дублирование. """
    if request.method == 'POST':
        ClientInfo.save_client_info(request.POST)
        return redirect('clients')
    managers = Manager.objects.filter(is_active=True)
    inn_list: list = clients_utils.get_inn_list_from_active_clients()
    context: dict = {'page': 'clients', 'user': request.user, 'managers': managers, 'inn_list': str(inn_list)}
    return render(request, 'accounting_system/reg.html', context)


@login_required
def change_user_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных пользователя. """
    change_user_pk: str = request.POST.get('user_pk')
    user: Manager = get_object_or_404(Manager, pk=change_user_pk)
    form: ManagerChangeForm = ManagerChangeForm(instance=user)
    context: dict = {'page': 'cl_acc', 'form': form, 'user': request.user, 'change_account': user}
    return render(request, 'accounting_system/clients/change_account.html', context)


@login_required
@require_POST
def change_user(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных менеджера. """
    user_pk_for_change: int = request.POST.get('user_pk_for_change')
    user: Manager = get_object_or_404(Manager, pk=user_pk_for_change)
    form: ManagerChangeForm = ManagerChangeForm(request.POST, instance=user)
    if form.is_valid():
        form.save()
        return redirect('cl_acc')


@login_required
def change_worker_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных менеджера. """
    change_worker_pk: str = request.POST.get('worker_pk')
    user: Manager = get_object_or_404(Manager, pk=change_worker_pk)
    form: WorkerChangeForm = WorkerChangeForm(instance=user)
    context: dict = {'page': 'cl_acc', 'form': form, 'user': request.user, 'change_account': user}
    return render(request, 'accounting_system/managers/change_worker.html', context)


@login_required
@require_POST
def change_worker(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных менеджера. """
    worker_pk_for_change: int = request.POST.get('worker_pk_for_change')
    user: Manager = get_object_or_404(Manager, pk=worker_pk_for_change)
    form: WorkerChangeForm = WorkerChangeForm(request.POST, instance=user)
    if form.is_valid():
        form.save()
        return redirect('cl_acc')


@login_required
def pay_form(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/pay.html')


@login_required
def pay(request: HttpRequest) -> HttpResponse:
    manager_pk = request.POST.get('pay_pk')
    payer: Manager = get_object_or_404(Manager, pk=manager_pk)
    cur_sum = payer.get_account()
    add_sum = int(request.POST.get('pay'))
    new_sum = cur_sum + add_sum
    payer.account = new_sum
    payer.save()
    return render(request, 'accounting_system/clients/success_pay.html')


@login_required
def clients(request: HttpRequest) -> HttpResponse:
    clients_queryset = clients_utils.get_clients_queryset
    context: dict = {'page': 'clients', 'user': request.user,
                     'clients': clients_queryset}
    return render(request, 'accounting_system/clients/clients.html', context)



@login_required
def filter_clients(request: HttpRequest) -> HttpResponse:
    client_pk: str = request.POST.get('search_input')
    pk = int(client_pk)
    clients_queryset = Manager.objects.filter(pk=pk)
    context: dict = {'page': 'clients', 'user': request.user, 'clients': clients_queryset}
    return render(request, 'accounting_system/clients/clients.html', context)


@login_required
def ts(request: HttpRequest) -> HttpResponse:
    ts_queryset = clients_utils.get_ts_queryset
    context: dict = {'page': 'staff', 'user': request.user,
                     'tss': ts_queryset}
    return render(request, 'accounting_system/managers/staff.html', context)


@login_required
def filter_ts(request: HttpRequest) -> HttpResponse:
    ts_pk: str = request.POST.get('search_input')
    pk = int(ts_pk)
    ts_queryset = Tsrequest.objects.filter(pk=pk)
    context: dict = {'page': 'staff', 'user': request.user, 'tss': ts_queryset}
    return render(request, 'accounting_system/managers/staff.html', context)


@login_required
def ts_anal(request: HttpRequest) -> HttpResponse:
    ts_queryset = clients_utils.get_ts_queryset()
    ots_queryset = clients_utils.get_ots_queryset()
    cts_queryset = clients_utils.get_cts_queryset()
    ts = len(ts_queryset)
    ots = len(ots_queryset)
    cts = len(cts_queryset)
    context: dict = {'page': 'staff', 'user': request.user,
                     'tss': ts_queryset, 'ts': ts, 'ots': ots, 'cts': cts}
    return render(request, 'accounting_system/tasks/ts_anal.html', context)


@login_required
def add_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления клиента.
        Дополнительно передает список из ИНН всех активных клиентов,
        для последующей валидации входных данных фронтендом на дублирование. """
    if request.method == 'POST':
        Client.save_client(request.POST)
        return redirect('clients')
    managers = Manager.objects.filter(is_active=True)
    inn_list: list = clients_utils.get_inn_list_from_active_clients()
    context: dict = {'page': 'clients', 'user': request.user, 'managers': managers, 'inn_list': str(inn_list)}
    return render(request, 'accounting_system/clients/add_client.html', context)


@login_required
def delete_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления клиента """
    if client_pk := request.POST.get('client_pk_for_delete'):
        client: Client = get_object_or_404(Client, pk=client_pk)
        client.kill()
        return redirect('clients')
    client_pk: str = request.POST.get('client_pk')
    client: Client = get_object_or_404(Client, pk=client_pk)
    context: dict = {'page': 'clients', 'client': client, 'user': request.user}
    return render(request, 'accounting_system/clients/delete_client.html', context)


@login_required
def client_profile(request: HttpRequest) -> HttpResponse:
    """ Контроллер профиля клиента. Отображает список услуг присвоенных клиенту. """
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    context: dict = {'page': 'clients', 'user': request.user, 'client': client}
    return render(request, 'accounting_system/clients/client_profile.html', context)


@login_required
def ts_profile(request: HttpRequest) -> HttpResponse:
    ts_pk = request.POST.get('ts_pk')
    ts: Tsrequest = get_object_or_404(Tsrequest, pk=ts_pk)
    context: dict = {'page': 'staff', 'user': request.user, 'ts': ts}
    return render(request, 'accounting_system/managers/ts_profile.html', context)


@login_required
def close_ts(request: HttpRequest) -> HttpResponse:
    ts_pk = request.POST.get('ts_pk')
    ts: Tsrequest = get_object_or_404(Tsrequest, pk=ts_pk)
    ts.ts_active = False
    ts.ts_close_date = timezone.now()
    ts.save()
    context: dict = {'page': 'staff', 'user': request.user, 'ts': ts}
    return render(request, 'accounting_system/managers/ts_profile.html', context)


def change_client_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер генерации формы для редактирования данных о клиенте. """
    managers = Manager.objects.filter(is_active=True)
    client = get_object_or_404(Client, pk=request.POST.get('client_pk'))
    context: dict = {'page': 'clients', 'user': request.user, 'managers': managers, 'client': client}
    return render(request, 'accounting_system/clients/change_client.html', context)


def change_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер сохранения изменений данных клиента. """
    clients_utils.save_client_changes(request)
    context = clients_utils.get_client_profile_context(request)
    return render(request, 'accounting_system/clients/client_profile.html', context)


# STAFF


@login_required
def staff(request: HttpRequest) -> HttpResponse:
    """ Контроллер со списком пользователей зарегестрированных в системе. """
    managers = managers_utils.get_managers_queryset().order_by('pk')
    context: dict = {'page': 'staff', 'managers': managers, 'user': request.user}
    return render(request, 'accounting_system/managers/staff.html', context)


def add_manager(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления нового менеджера в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: CustomUserCreationForm = CustomUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return redirect('staff')
    else:
        form = CustomUserCreationForm()
    context: dict = {'page': 'staff', 'form': form, 'user': request.user}
    return render(request, 'accounting_system/reg.html', context)


def add_new_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления нового клиента в систему. """
    if request.method == 'POST':
        form: CustomClientCreationForm = CustomClientCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logout_view')
    else:
        form = CustomClientCreationForm()
    context: dict = {'page': 'logout_view', 'form': form, 'user': request.user}
    return render(request, 'accounting_system/reg.html', context)


@login_required
@staff_member_required
def change_manager_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных менеджера.
        Доступен только администратору и суперпользователю. """
    change_manager_pk: str = request.POST.get('manager_pk')
    manager: Manager = get_object_or_404(Manager, pk=change_manager_pk)
    form: ManagerChangeForm = ManagerChangeForm(instance=manager)
    context: dict = {'page': 'staff', 'form': form, 'user': request.user, 'change_manager': manager}
    return render(request, 'accounting_system/managers/change_manager.html', context)


@login_required
@require_POST
@staff_member_required
def change_manager(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных менеджера.
        Доступен только администратору и суперпользователю. """
    manager_pk_for_change: str = request.POST.get('manager_pk_for_change')
    manager: Manager = get_object_or_404(Manager, pk=manager_pk_for_change)
    form: ManagerChangeForm = ManagerChangeForm(request.POST, instance=manager)
    if form.is_valid():
        form.save()
        return redirect('staff')


@login_required
@staff_member_required
def delete_manager(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления менеджера.
        Доступен только администратору и суперпользователю. """
    if manager_pk := request.POST.get('manager_pk_for_delete'):
        manager: Manager = get_object_or_404(Manager, pk=manager_pk)
        manager.kill()
        return redirect('staff')
    manager_pk: str = request.POST.get('manager_pk')
    manager: Manager = get_object_or_404(Manager, pk=manager_pk)
    context: dict = {'page': 'staff', 'user': request.user, 'manager': manager}
    return render(request, 'accounting_system/managers/delete_manager.html', context)


# TASKS


@login_required
def tasks(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы с задачами пользователя.
        Для менеджера выводит список его задач.
        Для администратора выводит список задач всех менеджеров в системе,
        включая и его собственные.
        Если в запросе присутсвует manager_pk, то отдает задачи только для
        менеджера переданного в manager_pk. """
    manager_pk: str = request.POST.get('manager_pk')
    managers = Manager.objects.filter(is_active=True)
    tasks_list: list = tasks_utils.get_tasks_list(request.user, manager_pk)
    context: dict = {'page': 'tasks', 'user': request.user, 'tasks': tasks_list,
                     'managers': managers, 'manager_pk_for_filter': int(manager_pk) if manager_pk else None}
    return render(request, 'accounting_system/tasks/tasks.html', context)


# CALENDAR


@login_required
def calendar(request: HttpRequest) -> HttpResponse:
    """ Контроллер интерактивного календаря.
        Формирует календарь с датами окончаний сроков действия услуг в виде событий.
        Для администраторов выводит все сроки.
        Для менеджеров - только сроки окончания услуг принадлежащих им клиентов. """
    event_list = calendar_utils.get_event_list(request.user)
    context: dict = {'page': 'calendar', 'user': request.user, 'event_list': event_list}
    return render(request, 'accounting_system/calendar/calendar.html', context)


# SERVICE
@login_required()
def tel(request: HttpRequest) -> HttpResponse:
    tel_pk = request.POST.get('tel_pk')
    tel: ServiceInfo = get_object_or_404(ServiceInfo, pk=tel_pk)
    tel_name = tel.service_name
    tel_description = tel.service_description
    tel_cost = tel.service_cost
    context: dict = {'page': 'main_page', 'tel_name': tel_name, 'tel_description': tel_description, 'tel_cost': tel_cost}
    return render(request, 'accounting_system/services/tel.html', context)


@login_required()
def tel_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 1
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.tel != True:
        client.tel = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/tel_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def tel_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('tel_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 1
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.tel = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def m_lines(request: HttpRequest) -> HttpResponse:
    ml_pk = request.POST.get('ml_pk')
    ml: ServiceInfo = get_object_or_404(ServiceInfo, pk=ml_pk)
    ml_name = ml.service_name
    ml_description = ml.service_description
    ml_cost = ml.service_cost
    context: dict = {'page': 'main_page', 'ml_name': ml_name, 'ml_description': ml_description,
                     'ml_cost': ml_cost}
    return render(request, 'accounting_system/services/m_lines.html', context)


@login_required()
def ml_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 2
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.ml != True:
        client.ml = 'True'
        client.sub_cost = sub_cost + service_cost
        client.save()
        return render(request, 'accounting_system/services/ml_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def ml_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('ml_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 2
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.ml = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def internet(request: HttpRequest) -> HttpResponse:
    internet_pk = request.POST.get('internet_pk')
    internet: ServiceInfo = get_object_or_404(ServiceInfo, pk=internet_pk)
    internet_name = internet.service_name
    internet_description = internet.service_description
    internet_cost = internet.service_cost
    context: dict = {'page': 'main_page', 'internet_name': internet_name, 'internet_description': internet_description,
                     'internet_cost': internet_cost}
    return render(request, 'accounting_system/services/internet.html', context)


@login_required()
def internet_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 3
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.internet != True:
        client.internet = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/internet_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def internet_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('internet_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 3
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.internet = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def online_security(request: HttpRequest) -> HttpResponse:
    security_pk = request.POST.get('security_pk')
    security: ServiceInfo = get_object_or_404(ServiceInfo, pk=security_pk)
    security_name = security.service_name
    security_description = security.service_description
    security_cost = security.service_cost
    context: dict = {'page': 'main_page', 'security_name': security_name, 'security_description': security_description,
                     'security_cost': security_cost}
    return render(request, 'accounting_system/services/online_security.html', context)


@login_required()
def online_security_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 4
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.security != True:
        client.security = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/online_security_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def online_security_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('security_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 4
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.security = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def backup(request: HttpRequest) -> HttpResponse:
    backup_pk = request.POST.get('backup_pk')
    backup: ServiceInfo = get_object_or_404(ServiceInfo, pk=backup_pk)
    backup_name = backup.service_name
    backup_description = backup.service_description
    backup_cost = backup.service_cost
    context: dict = {'page': 'main_page', 'backup_name': backup_name, 'backup_description': backup_description,
                     'backup_cost': backup_cost}
    return render(request, 'accounting_system/services/backup.html', context)


@login_required()
def backup_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 5
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.backup != True:
        client.backup = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/backup_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def backup_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('backup_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 5
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.backup = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def protect(request: HttpRequest) -> HttpResponse:
    protect_pk = request.POST.get('protect_pk')
    protect: ServiceInfo = get_object_or_404(ServiceInfo, pk=protect_pk)
    protect_name = protect.service_name
    protect_description = protect.service_description
    protect_cost = protect.service_cost
    context: dict = {'page': 'main_page', 'protect_name': protect_name, 'protect_description': protect_description,
                     'protect_cost': protect_cost}
    return render(request, 'accounting_system/services/protect.html', context)


@login_required()
def protect_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 6
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.protect != True:
        client.protect = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/protect_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def protect_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('protect_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 6
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.protect = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def support(request: HttpRequest) -> HttpResponse:
    support_pk = request.POST.get('support_pk')
    support: ServiceInfo = get_object_or_404(ServiceInfo, pk=support_pk)
    support_name = support.service_name
    support_description = support.service_description
    support_cost = support.service_cost
    context: dict = {'page': 'main_page', 'support_name': support_name, 'support_description': support_description,
                     'support_cost': support_cost}
    return render(request, 'accounting_system/services/support.html', context)


@login_required()
def support_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 7
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.support != True:
        client.support = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/support_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def support_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('support_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 7
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.support = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def streaming_tv(request: HttpRequest) -> HttpResponse:
    s_tv_pk = request.POST.get('s_tv_pk')
    s_tv: ServiceInfo = get_object_or_404(ServiceInfo, pk=s_tv_pk)
    s_tv_name = s_tv.service_name
    s_tv_description = s_tv.service_description
    s_tv_cost = s_tv.service_cost
    context: dict = {'page': 'main_page', 's_tv_name': s_tv_name, 's_tv_description': s_tv_description,
                     's_tv_cost': s_tv_cost}
    return render(request, 'accounting_system/services/streaming_tv.html', context)


@login_required()
def streaming_tv_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 8
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.s_tv != True:
        client.s_tv = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/streaming_tv_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def streaming_tv_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('s_tv_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 8
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.s_tv = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required()
def streaming_movies(request: HttpRequest) -> HttpResponse:
    s_mov_pk = request.POST.get('sm_pk')
    s_mov: ServiceInfo = get_object_or_404(ServiceInfo, pk=s_mov_pk)
    s_mov_name = s_mov.service_name
    s_mov_description = s_mov.service_description
    s_mov_cost = s_mov.service_cost
    context: dict = {'page': 'main_page', 's_mov_name': s_mov_name, 's_mov_description': s_mov_description,
                     's_mov_cost': s_mov_cost}
    return render(request, 'accounting_system/services/streaming_movies.html', context)


@login_required()
def streaming_movies_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 9
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if client.s_mov != True:
        client.s_mov = 'True'
        client.sub_cost = service_cost + sub_cost
        client.save()
        return render(request, 'accounting_system/services/streaming_movies_sc.html')
    else:
        return render(request, 'accounting_system/services/sc.html')


@login_required()
def streaming_movies_dc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('s_mov_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 9
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    client.s_mov = 'False'
    client.sub_cost = sub_cost - service_cost
    client.save()
    return render(request, 'accounting_system/services/dc.html')


@login_required
@staff_member_required
def service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы с услкгами. Формирует список доступных категорий услуг.
        Доступен только администратору и суперпользователю. """
    context: dict = {'page': 'service', 'user': request.user}
    return render(request, 'accounting_system/services/service.html', context)


@login_required
@require_POST
def add_service_for_client_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы с формой добавления услуги для клиента. """
    client_pk: str = request.POST.get('client_pk')
    kkt_list = CashMachine.objects.filter(active=True)
    ecp_list = ECP.objects.filter(active=True)
    ofd_list = OFD.objects.filter(active=True)
    fn_list = FN.objects.filter(active=True)
    to_list = TO.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'client_pk': client_pk,
                     'kkt_list': kkt_list, 'ecp_list': ecp_list, 'ofd_list': ofd_list,
                     'fn_list': fn_list, 'to_list': to_list}
    return render(request, 'accounting_system/services/add_service_for_client.html', context)


@login_required
@require_POST
def add_service_for_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления услуги для клиента. Использует логику из модуля utils.py. """
    services_utils.create_service_for_client(request)
    return redirect('clients')


@login_required
@require_POST
@staff_member_required
def delete_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления услуги из системы.
        Доступен только администратору и суперпользователю. """
    back_path: str = request.POST.get('back_path')
    service_pk: str = request.POST.get('service_pk')
    service_class_instance: Union[ECP, OFD, FN, TO] = common_utils.get_service_class_instance(request)
    service_object: Union[ECP, OFD, FN, TO] = get_object_or_404(service_class_instance, pk=service_pk)
    service_object.kill()
    return redirect(back_path)


@login_required
@require_POST
def delete_service_from_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления улуги присвоенной клиенту. """
    client_pk: str = request.POST.get('client_pk')
    if service_pk := request.POST.get('service_pk_for_delete'):
        service_object: Service = get_object_or_404(Service, pk=service_pk)
        service_object.kill()
        context = clients_utils.get_client_profile_context(request)
        return render(request, 'accounting_system/clients/client_profile.html', context)
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'clients', 'user': request.user, 'service_pk': service_pk, 'client_pk': client_pk}
    return render(request, 'accounting_system/services/delete_service_from_client.html', context)


def change_service_for_client_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения услуги присвоенной клиенту """
    client_pk: str = request.POST.get('client_pk')
    service_pk: str = request.POST.get('service_pk')
    service_object: Service = get_object_or_404(Service, pk=service_pk)
    kkt_list = CashMachine.objects.filter(active=True)
    ecp_list = ECP.objects.filter(active=True)
    ofd_list = OFD.objects.filter(active=True)
    fn_list = FN.objects.filter(active=True)
    to_list = TO.objects.filter(active=True)
    context: dict = {'page': 'clients', 'user': request.user, 'service': service_object, 'kkt_list': kkt_list,
                     'ecp_list': ecp_list, 'ofd_list': ofd_list, 'fn_list': fn_list, 'to_list': to_list,
                     'client_pk': client_pk}
    return render(request, 'accounting_system/services/change_service_for_client_form.html', context)


def save_service_changes(request: HttpRequest) -> HttpResponse:
    """ Контроллер сохранения изменений в услуге. """
    services_utils.make_changes_to_the_service(request)
    context = clients_utils.get_client_profile_context(request)
    return render(request, 'accounting_system/clients/client_profile.html', context)


# KKT


@login_required
@staff_member_required
def kkt_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком кассовой техники внесенной в систему.
        Доступен только администратору и суперпользователю. """
    kkt_list = CashMachine.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'kkt_list': kkt_list}
    return render(request, 'accounting_system/services/kkt_service.html', context)


@login_required
@staff_member_required
def add_kkt(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления кассового аппарата в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: CashMachineCreationForm = CashMachineCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kkt-service')
    form: CashMachineCreationForm = CashMachineCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_kkt.html', context)


@login_required
@staff_member_required
def delete_kkt(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления кассового аппарата из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user,
                     'service_pk': service_pk, 'service_type': 'kkt', 'back_path': 'kkt-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# FN


@login_required
@staff_member_required
def fn_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком фискальных накопителей внесенных в систему.
        Доступен только администратору и суперпользователю. """
    fn_list = FN.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'fn_list': fn_list}
    return render(request, 'accounting_system/services/fn_service.html', context)


@login_required
@staff_member_required
def add_fn(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления фискального накопителя в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: FNCreationForm = FNCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fn-service')
    form: FNCreationForm = FNCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_fn.html', context)


@login_required
@staff_member_required
def delete_fn(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления фискального накопителя из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'fn', 'back_path': 'fn-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# TO


@login_required
@staff_member_required
def to_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком типов договоров технического
        обслуживания ККТ, внесенных в систему.
        Доступен только администратору и суперпользователю. """
    to_list = TO.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'to_list': to_list}
    return render(request, 'accounting_system/services/to_service.html', context)


@login_required
@staff_member_required
def add_to(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления договора технического обслуживания в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: TOCreationForm = TOCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('to-service')
    form: TOCreationForm = TOCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_to.html', context)


@login_required
@staff_member_required
def delete_to(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления договора технического обслуживания из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'to', 'back_path': 'to-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# ECP


@login_required
@staff_member_required
def ecp_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком ЭЦП внесенных в систему.
        Доступен только администратору и суперпользователю. """
    ecp_list = ECP.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'ecp_list': ecp_list}
    return render(request, 'accounting_system/services/ecp_service.html', context)


@login_required
@staff_member_required
def add_ecp(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления ЭЦП в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: ECPCreationForm = ECPCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ecp-service')
    form: ECPCreationForm = ECPCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_ecp.html', context)


@login_required
@staff_member_required
def delete_ecp(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления ЭЦП из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'ecp', 'back_path': 'ecp-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# OFD


@login_required
@staff_member_required
def ofd_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком доступных ОФД внесенных в систему.
        Доступен только администратору и суперпользователю. """
    ofd_list = OFD.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'ofd_list': ofd_list}
    return render(request, 'accounting_system/services/ofd_service.html', context)


@login_required
@staff_member_required
def add_ofd(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления ОФД в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: OFDCreationForm = OFDCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ofd-service')
    form: OFDCreationForm = OFDCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_ofd.html', context)


@login_required
@staff_member_required
def delete_ofd(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления ОФД из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'ofd', 'back_path': 'ofd-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)
