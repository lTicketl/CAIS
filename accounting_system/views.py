from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.db.models import Sum
from django.utils import timezone

from .forms import (CustomUserCreationForm, WorkerChangeForm, ManagerChangeForm)
from .models import ServiceInfo, TsRequest, Manager
from .services import (clients_utils)


@login_required
def auth(request: HttpRequest) -> HttpResponse:
    """ Контроллер авторизации пользователей. """
    return render(request, 'accounting_system/auth.html', {'form': AuthenticationForm})


def add_manager(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления нового менеджера в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: CustomUserCreationForm = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = CustomUserCreationForm()
    context: dict = {'page': 'staff', 'form': form, 'user': request.user}
    return render(request, 'accounting_system/reg.html', context)


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
    ts_request = TsRequest(ts_client=user, ts_problem=request.POST.get('ts'))
    ts_request.save()
    return render(request, 'accounting_system/clients/success_ts.html')


@login_required()
def success_ts(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/client_account.html')


def success_sc(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/clients/success_sc.html')


def logout_view(request: HttpRequest) -> HttpResponse:
    """ Контроллер выхода из системы. """
    logout(request)
    return redirect('login')


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
    ts_queryset = TsRequest.objects.filter(pk=pk)
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
    return render(request, 'accounting_system/anal/ts_anal.html', context)


@login_required
def client_profile(request: HttpRequest) -> HttpResponse:
    """ Контроллер профиля клиента. Отображает список услуг присвоенных клиенту. """
    client_pk = request.POST.get('client_pk')
    client_ch = clients_utils.get_predict_dataframe(client_pk)
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    context: dict = {'page': 'clients', 'user': request.user, 'client': client}
    return render(request, 'accounting_system/clients/client_profile.html', context)


@login_required
def ts_profile(request: HttpRequest) -> HttpResponse:
    ts_pk = request.POST.get('ts_pk')
    ts: TsRequest = get_object_or_404(TsRequest, pk=ts_pk)
    context: dict = {'page': 'staff', 'user': request.user, 'ts': ts}
    return render(request, 'accounting_system/managers/ts_profile.html', context)


@login_required
def close_ts(request: HttpRequest) -> HttpResponse:
    ts_pk = request.POST.get('ts_pk')
    ts: TsRequest = get_object_or_404(TsRequest, pk=ts_pk)
    ts.ts_active = False
    ts.ts_close_date = timezone.now()
    ts.save()
    context: dict = {'page': 'staff', 'user': request.user, 'ts': ts}
    return render(request, 'accounting_system/managers/ts_profile.html', context)


# STAFF


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


# SERVICE


@login_required()
def tel(request: HttpRequest) -> HttpResponse:
    tel_pk = request.POST.get('tel_pk')
    tel: ServiceInfo = get_object_or_404(ServiceInfo, pk=tel_pk)
    tel_name = tel.service_name
    tel_description = tel.service_description
    tel_cost = tel.service_cost
    context: dict = {'page': 'main_page', 'tel_name': tel_name, 'tel_description': tel_description,
                     'tel_cost': tel_cost}
    return render(request, 'accounting_system/services/tel.html', context)


@login_required()
def tel_sc(request: HttpRequest) -> HttpResponse:
    client_pk = request.POST.get('client_pk')
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    service_pk = 1
    service: ServiceInfo = get_object_or_404(ServiceInfo, pk=service_pk)
    service_cost = service.service_cost
    sub_cost = client.sub_cost
    if not client.tel:
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
    if not client.ml:
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
    if not client.internet:
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
    if not client.security:
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
    if not client.backup:
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
    if not client.protect:
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
    if not client.support:
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
    if not client.s_tv:
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
    if not client.s_mov:
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
def service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы с аналитикой. """
    context: dict = {'page': 'service', 'user': request.user}
    return render(request, 'accounting_system/services/service.html', context)


@login_required
def gen_anal(request: HttpRequest) -> HttpResponse:
    cl_queryset = clients_utils.get_clients_queryset()
    service_queryset = clients_utils.get_service_info_queryset()
    workers_queryset = clients_utils.get_workers_queryset()
    sc_sum = ServiceInfo.objects.aggregate(Sum('service_cost'))
    suc_sum = Manager.objects.aggregate(Sum('sub_cost'))
    sub_sum = suc_sum['sub_cost__sum']
    service_sum = sc_sum['service_cost__sum']
    cl_sum = Manager.objects.aggregate(Sum('account'))
    client_sum = cl_sum['account__sum']
    cl = len(cl_queryset)
    ci = len(service_queryset)
    w = len(workers_queryset)
    max_profit = service_sum * cl
    context: dict = {'page': 'staff', 'user': request.user, 'tss': cl_queryset, 'cl': cl, 'ci': ci,
                     'services': service_queryset, 'w': w, 'cl_sum': client_sum, 'sc_sum': service_sum,
                     'max_pro': max_profit, 'real_pro': sub_sum}
    return render(request, 'accounting_system/anal/gen_anal.html', context)


@login_required
def churn_anal(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting_system/anal/churn_anal.html')
