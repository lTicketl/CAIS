from typing import Any
from django.http import HttpRequest
from accounting_system.models import TsRequest, Manager, ServiceInfo
import pandas as pd
from django.shortcuts import get_object_or_404


def get_clients_queryset():
    clients_queryset = Manager.objects.filter(is_staff=False)
    print(type(clients_queryset))
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


def get_predict_dataframe(id):
    client_pk: str = id
    client: Manager = get_object_or_404(Manager, pk=client_pk)
    gender1 = client.gender
    if gender1 == 'м':
        gender = 'Male'
    else:
        gender = 'Female'
    Partner1 = client.partner
    if Partner1 == 'да':
        Partner = 'Yes'
    else:
        Partner = 'No'
    Dependents1 = client.depends
    if Dependents1 == 'да':
        Dependents = 'Yes'
    else:
        Dependents = 'No'
    PhoneService1 = client.tel
    MultipleLines1 = client.ml
    if PhoneService1 == 0:
        PhoneService = 'No'
        MultipleLines = 'No phone service'
    else:
        PhoneService = 'Yes'
        if MultipleLines1 == 0:
            MultipleLines = 'No'
        else:
            MultipleLines = 'Yes'
    InternetService1 = client.internet
    OnlineSecurity1 = client.security
    OnlineBackup1 = client.backup
    DeviceProtection1 = client.protect
    TechSupport1 = client.support
    StreamingTV1 = client.s_tv
    StreamingMovies1 = client.s_mov
    if InternetService1 == 0:
        InternetService = 'No'
        OnlineSecurity = 'No internet service'
        OnlineBackup = 'No internet service'
        DeviceProtection = 'No internet service'
        TechSupport = 'No internet service'
        StreamingTV = 'No internet service'
        StreamingMovies = 'No internet service'
    else:
        InternetService = 'Fiber optic'
        if OnlineSecurity1 == 0:
            OnlineSecurity = 'No'
        else:
            OnlineSecurity = 'Yes'
        if OnlineBackup1 == 0:
            OnlineBackup = 'No'
        else:
            OnlineBackup = 'Yes'
        if DeviceProtection1 == 0:
            DeviceProtection = 'No'
        else:
            DeviceProtection = 'Yes'
        if TechSupport1 == 0:
            TechSupport = 'No'
        else:
            TechSupport = 'Yes'
        if StreamingTV1 == 0:
            StreamingTV = 'No'
        else:
            StreamingTV = 'Yes'
        if StreamingMovies1 == 0:
            StreamingMovies = 'No'
        else:
            StreamingMovies = 'Yes'
    Contract1 = client.billing
    if Contract1 == 'ежемесячно':
        Contract = 'Month-to-month'
    else:
        Contract = 'One year'
    PaperlessBilling = 'Yes'
    PaymentMethod1 = client.payment_method
    if PaymentMethod1 == 'Электронный чек':
        PaymentMethod = 'Electronic check'
    elif PaymentMethod1 == 'Почтовый чек':
        PaymentMethod = 'Mailed check'
    elif PaymentMethod1 == 'Банковский перевод':
        PaymentMethod = 'Bank transfer (automatic)'
    else:
        PaymentMethod = 'Credit card (automatic)'
    TotalCharges = client.sub_cost
    # TotalCharges = 20.2
    print(gender)
    print(Partner)
    print(Dependents)
    print(PhoneService)
    print(MultipleLines)
    print(InternetService)
    print(OnlineSecurity)
    print(OnlineBackup)
    print(DeviceProtection)
    print(TechSupport)
    print(StreamingTV)
    print(StreamingMovies)
    print(Contract)
    print(PaperlessBilling)
    print(PaymentMethod)
    print(TotalCharges)
    dataframe: dict = {'gender': gender, 'Partner': Partner, 'Dependents': Dependents, 'PhoneService': PhoneService,
                       'MultipleLines': MultipleLines, 'InternetService': InternetService,
                       'OnlineSecurity': OnlineSecurity, 'OnlineBackup': OnlineBackup,
                       'DeviceProtection': DeviceProtection, 'TechSupport': TechSupport, 'StreamingTV': StreamingTV,
                       'StreamingMovies': StreamingMovies, 'Contract': Contract, 'PaperlessBilling': PaperlessBilling,
                       'PaymentMethod': PaymentMethod, 'TotalCharges': TotalCharges}
    return dataframe
