from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import ClientInfo, Manager, CashMachine, ECP, OFD, FN, TO


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Manager
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class CustomStaffCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Manager
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class CustomClientCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ClientInfo
        fields = ('cl_username', 'cl_password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cl_password'].help_text = None


class ManagerChangeForm(ModelForm):
    class Meta:
        model = Manager
        fields = ('username', 'first_name', 'last_name', 'middle_name',
                  'gender', 'dob', 'email', 'phone', 'adr',
                  'sen_cit', 'partner', 'depends', 'tenure', 'billing', 'payment_method')


class WorkerChangeForm(ModelForm):
    class Meta:
        model = Manager
        fields = ('username', 'first_name', 'last_name', 'middle_name',
                  'gender', 'dob', 'email', 'phone', 'adr')


class PayChangeForm(ModelForm):
    class Meta:
        model = Manager
        fields = ('account',)


class CashMachineCreationForm(ModelForm):
    class Meta:
        model = CashMachine
        fields = ('model',)


class FNCreationForm(ModelForm):
    class Meta:
        model = FN
        fields = ('name', 'validity')


class TOCreationForm(ModelForm):
    class Meta:
        model = TO
        fields = ('name', 'validity')


class ECPCreationForm(ModelForm):
    class Meta:
        model = ECP
        fields = ('name', 'validity')


class OFDCreationForm(ModelForm):
    class Meta:
        model = OFD
        fields = ('model', 'validity')
