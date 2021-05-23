from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


GENDER = (
    ('м', 'М'),
    ('ж', 'Ж'),
)

STATUS = (
    ('активирован', 'Активирован'),
    ('деактивирован', 'Деактивирован'),
)

WEEK_DAY = (
    ('понедельник', 'Понедельник'),
    ('вторник', 'Вторник'),
    ('среда', 'Среда'),
    ('четверг', 'Четверг'),
    ('пятница', 'Пятница'),
    ('суббота', 'Суббота'),
    ('воскресенье', 'Воскресенье'),
)

PARTNER = (
    ('да', 'Да'),
    ('нет', 'Нет')
)

DEPENDS = (
    ('да', 'Да'),
    ('нет', 'Нет')
)

BILLING = (
    ('ежемесячно', 'Ежемесячно'),
    ('ежегодно', 'Ежегодно')
)

PAYMENT_METHOD = (
    ('Электронный чек', 'электронный чек'),
    ('Почтовый чек', 'почтовый чек'),
    ('Банковский перевод', 'банковский перевод'),
    ('Кредитная карта', 'кредитная карта')
)

ACTION_NAME = (
    ('Пополнение счета', 'пополнение счета'),
    ('Подключение услуги', 'подключение услуги'),
    ('Запрос в техподдержку', 'запрос в техподдержку')
)

SENIOR_CITIZEN = (
    ('да', 'Да'),
    ('нет', 'Нет')
)


class ClientInfo(models.Model):
    client_id = models.AutoField('id', primary_key=True)
    cl_username = models.CharField(verbose_name='Логин', max_length=150, unique=True, null=True)
    cl_password = models.CharField('Пароль', max_length=30, null=True, blank=True)
    cl_last_name = models.CharField('Фамилия', max_length=30, null=True, blank=True)
    cl_first_name = models.CharField('Имя', max_length=30, null=True, blank=True)
    cl_middle_name = models.CharField('Отчество', max_length=30, null=True, blank=True)
    cl_gender = models.CharField('Пол', max_length=10, choices=GENDER)
    cl_dob = models.DateField('Дата рождения', null=True, blank=True)
    cl_number = models.IntegerField('Номер телефона', unique=True)
    cl_mail = models.EmailField('Email', null=True, blank=True)
    cl_adr = models.CharField('Адрес', max_length=300, null=True, blank=True)
    cl_con_date = models.DateField('Дата подключения', default=timezone.now)
    cl_discon_date = models.DateField('Дата отключения', null=True, blank=True)
    cl_account = models.IntegerField('Состояние счета')
    cl_sub_cost = models.IntegerField('Стоимость подписок')
    cl_sen_cit = models.CharField('Пенсионер', max_length=5, choices=SENIOR_CITIZEN, default="Нет")
    cl_partner = models.CharField('Наличие партнера', max_length=5, choices=PARTNER)
    cl_depends = models.CharField('Дети', max_length=5, choices=DEPENDS)
    cl_tenure = models.CharField('Владения', max_length=10, null=True, blank=True)
    cl_billing = models.CharField('Период оплаты', max_length=20, choices=BILLING)
    cl_payment_method = models.CharField('Способ оплаты', max_length=50, choices=PAYMENT_METHOD)

    def __str__(self):
        return self.cl_last_name + ' ' + self.cl_first_name + ' ' + self.cl_middle_name

    @staticmethod
    def save_client_info(post):
        try:
            client_info = ClientInfo(
                cl_passport=post['cl_passport'],
                cl_password=post['cl_password'],
                cl_last_name=post['cl_last_name'],
                cl_first_name=post['cl_first_name'],
                cl_middle_name=post['cl_middle_name'],
                cl_gender=post['cl_gender'],
                cl_dob=post['cl_dob'],
                cl_number=post['cl_number'],
                cl_mail=post['cl_mail'],
                cl_adr=post['cl_adr'],
                cl_con_date=post['cl_con_date'],
                cl_account=post['cl_account'],
                cl_sub_cost=post['cl_sub_cost'],
                cl_sen_cit=post['cl_sen_cit'],
                cl_partner=post['cl_partner'],
                cl_depends=post['cl_depends'],
                cl_tenure=post['cl_tenure'],
                cl_billing=post['cl_billing'],
                cl_payment_method=post['cl_payment_method'])
            client_info.save()
        except Exception:
            return False
        return client_info



class Addmoney(models.Model):
    addmoney_id = models.AutoField('id', primary_key=True)
    addmoney_cl = models.ForeignKey(ClientInfo, on_delete=models.PROTECT)
    addmoney_date = models.DateTimeField('Дата пополнения', default=timezone.now)
    addmoney_sum = models.IntegerField('Сумма пополнения')
    addmoney_dur = models.DateTimeField('Продолжительность пополнения', default=timezone.timedelta)

    def __str__(self):
        return self.addmoney_sum


class ServiceInfo(models.Model):
    service_id = models.AutoField('id', primary_key=True)
    service_name = models.CharField('Название услуги', max_length=30, null=True, blank=True)
    service_description = models.CharField('Описание услуги', max_length=1000, null=True, blank=True)
    service_cost = models.IntegerField('Стоимость услуги')
    active = models.BooleanField(default=True)

    def kill(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def __str__(self):
        return self.service_name + ' ' + self.service_cost + ' ' + self.service_description


class Servicecon(models.Model):

    def sclose_time(self):
        return timezone.now() + timezone.timedelta(hours=1)

    servicecon_id = models.AutoField('id', primary_key=True)
    servicecon_service = models.ForeignKey(ServiceInfo, on_delete=models.CASCADE)
    servicecon_con = models.DateTimeField('Дата подключения', default=timezone.now)
    servicecon_discon = models.DateTimeField('Дата отключения', default=sclose_time)
    servicecon_dur = models.DateTimeField('Продолжительность пользования', default=timezone.timedelta)

    def __str__(self):
        return self.servicecon_con + ' ' + self.servicecon_dur


class Manager(AbstractUser):
    username = models.CharField(verbose_name='Логин', max_length=150, unique=True)
    middle_name = models.CharField('Отчество', max_length=30, null=True, blank=True)
    gender = models.CharField('Пол', max_length=10, choices=GENDER, default='заполните поле!')
    dob = models.DateField('Дата рождения', null=True, blank=True)
    phone = models.IntegerField('Телефон', default=0)
    adr = models.CharField('Адрес', max_length=300, null=True, blank=True, default='заполните поле!')
    account = models.IntegerField('Состояние счета', default=0)
    sub_cost = models.IntegerField('Стоимость подписок', default=0)
    sen_cit = models.CharField('Пенсионер', max_length=5, choices=SENIOR_CITIZEN, default='заполните поле!')
    partner = models.CharField('Наличие партнера', max_length=5, choices=PARTNER, default='заполните поле!')
    depends = models.CharField('Дети', max_length=5, choices=DEPENDS, default='заполните поле!')
    tenure = models.CharField('Владения', max_length=20, null=True, blank=True, default='заполните поле!')
    billing = models.CharField('Период оплаты', max_length=20, choices=BILLING, default='заполните поле!')
    payment_method = models.CharField('Способ оплаты', max_length=50, choices=PAYMENT_METHOD, default='заполните поле!')
    tel = models.BooleanField(default=False)
    ml = models.BooleanField(default=False)
    internet = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    backup = models.BooleanField(default=False)
    protect = models.BooleanField(default=False)
    support = models.BooleanField(default=False)
    s_tv = models.BooleanField(default=False)
    s_mov = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name',  'email']

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_clients(self):
        return self.clients.filter(active=True)

    def get_account(self):
        return self.account

    @staticmethod
    def save_pay(post):
        try:
            acc = Manager.get_account() + post['pay']
            pay = Manager(
                account=acc,
            )
            pay.save()
        except Exception:
            return False
        return pay


class Tsrequest(models.Model):

    def close_time(self):
        return timezone.now() + timezone.timedelta(hours=1)

    tsreqest_id = models.AutoField('id', primary_key=True)
    ts_client = models.ForeignKey(Manager, on_delete=models.PROTECT)
    ts_open_date = models.DateTimeField('Дата подачи запроса', default=timezone.now())
    ts_close_date = models.DateTimeField('Дата закрытия запроса', null=True)
    ts_problem = models.CharField('Проблема', max_length=1000, null=True, blank=True)
    ts_active = models.BooleanField(default=True)


class Action(models.Model):
    action_id = models.AutoField('id', primary_key=True)
    action_name = models.CharField('Название', max_length=30, choices=ACTION_NAME)
    action_ts = models.ForeignKey(Tsrequest, on_delete=models.CASCADE)
    action_add = models.ForeignKey(Addmoney, on_delete=models.CASCADE)
    action_scon = models.ForeignKey(Servicecon, on_delete=models.CASCADE)

    def __str__(self):
        return self.action_name


class Worker(models.Model):
    worker_id = models.AutoField('id', primary_key=True)
    worker_password = models.CharField('Пароль', max_length=30, null=True, blank=True)
    worker_last_name = models.CharField('Фамилия', max_length=30, null=True, blank=True)
    worker_first_name = models.CharField('имя', max_length=30, null=True, blank=True)
    worker_middle_name = models.CharField('Отчество', max_length=30, null=True, blank=True)
    worker_gender = models.CharField('Пол', max_length=10, choices=GENDER)
    worker_dob = models.DateField('Дата рождения', null=True, blank=True)
    worker_number = models.CharField('Номер телефона', max_length=13, unique=True)
    worker_mail = models.EmailField('Email', null=True, blank=True)
    worker_adr = models.CharField('Адрес', max_length=300, null=True, blank=True)
    worker_pos = models.CharField('Должность', max_length=60, null=True, blank=True)
    active = models.BooleanField(default=True)

    def kill(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    @staticmethod
    def save_worker(post):
        try:
            worker = Worker(
                worker_password=post['worker_password'],
                worker_last_name=post['worker_last_name'],
                worker_first_name=post['worker_first_name'],
                worker_middle_name=post['worker_middle_name'],
                worker_gender=post['worker_gender'],
                worker_dob=post['worker_dob'],
                worker_number=post['worker_number'],
                worker_mail=post['worker_mail'],
                worker_adr=post['worker_adr'],
                worker_pos=post['worker_pos'])
            worker.save()
        except Exception:
            return False
        return worker


class ClientWorker(models.Model):
    client_worker_id = models.AutoField(primary_key=True)
    client_worker_cl = models.ForeignKey(ClientInfo, on_delete=models.PROTECT)
    client_worker_w = models.ForeignKey(Worker, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def kill(self):
        self.is_active = False
        self.save(update_fields=['is_active'])


class Client(models.Model):
    organization_name = models.CharField('Название организации', max_length=100)
    first_name = models.CharField('Имя', max_length=100, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=100, null=True, blank=True)
    patronymic = models.CharField('Отчество', max_length=100, null=True, blank=True)
    phone_number = models.CharField('Телефон', max_length=100)
    email = models.CharField('Email', max_length=100, null=True, blank=True, default='заполните поле!')
    inn = models.IntegerField('ИНН')
    comment = models.TextField('Комментарий', null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, related_name='clients', null=True)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.organization_name

    def get_count_active_services(self):
        active_services = self.services.filter(active=True)
        counter = 0
        for service in active_services:
            if service.ecp: counter += 1
            if service.ofd: counter += 1
            if service.fn: counter += 1
            if service.to: counter += 1
        return counter

    def get_services(self):
        return self.services.filter(active=True)

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])

    @staticmethod
    def save_client(post):
        try:
            client = Client(
                organization_name=post['organization_name'],
                first_name=post['first_name'],
                last_name=post['last_name'],
                patronymic=post['patronymic'],
                phone_number=post['phone_number'],
                email=post['email'],
                inn=post['inn'],
                comment=post['comment'],
                manager=Manager.objects.get(pk=post['manager'])
            )
            client.save()
        except Exception:
            return False
        return client


class ECP(models.Model):
    name = models.CharField('Название ЭЦП', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)', default=12)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class CashMachine(models.Model):
    model = models.CharField('Модель аппарата', max_length=100)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.model

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class OFD(models.Model):
    model = models.CharField('Название', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)')
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.model

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class FN(models.Model):
    name = models.CharField('Название ФН', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)', default=12)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class TO(models.Model):
    name = models.CharField('Название договора', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)', default=12)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class Service(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True, related_name='services')
    cash_machine = models.ForeignKey(CashMachine, on_delete=models.SET_NULL, blank=True, null=True)
    factory_number = models.CharField('Заводской номер', max_length=50, null=True, blank=True)

    ecp = models.ForeignKey(ECP, on_delete=models.SET_NULL, blank=True, null=True)
    ecp_add_date = models.DateField('Дата покупки ЭЦП', blank=True, null=True)
    ecp_expiration_date = models.DateField('Дата окончания срока действия ЭЦП', blank=True, null=True)
    ecp_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    ecp_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    ofd = models.ForeignKey(OFD, on_delete=models.SET_NULL, blank=True, null=True)
    ofd_add_date = models.DateField('Дата покупки ОФД', blank=True, null=True)
    ofd_expiration_date = models.DateField('Дата окончания срока действия ОФД', blank=True, null=True)
    ofd_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    ofd_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    fn = models.ForeignKey(FN, on_delete=models.SET_NULL, blank=True, null=True)
    fn_add_date = models.DateField('Дата покупки ФН', blank=True, null=True)
    fn_expiration_date = models.DateField('Дата окончания срока действия ФН', blank=True, null=True)
    fn_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    fn_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    to = models.ForeignKey(TO, on_delete=models.SET_NULL, blank=True, null=True)
    to_add_date = models.DateField('Дата заключения договора на ТО аппарата', blank=True, null=True)
    to_expiration_date = models.DateField('Дата окончания срока договора на ТО аппарата', blank=True, null=True)
    to_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    to_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    active = models.BooleanField(default=True)
    objects = models.Manager()

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])
