from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


GENDER = (
    ('м', 'М'),
    ('ж', 'Ж'),
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


class ServiceInfo(models.Model):
    service_id = models.AutoField('id', primary_key=True)
    service_name = models.CharField('Название услуги', max_length=30, null=True, blank=True)
    service_description = models.CharField('Описание услуги', max_length=1000, null=True, blank=True)
    service_cost = models.IntegerField('Стоимость услуги')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.service_name + ' ' + self.service_description


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


class TsRequest(models.Model):
    ts_id = models.AutoField('id', primary_key=True)
    ts_client = models.ForeignKey(Manager, on_delete=models.PROTECT)
    ts_open_date = models.DateTimeField('Дата подачи запроса', default=timezone.now())
    ts_close_date = models.DateTimeField('Дата закрытия запроса', null=True)
    ts_problem = models.CharField('Проблема', max_length=1000, null=True, blank=True)
    ts_active = models.BooleanField(default=True)


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

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])
