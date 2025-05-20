from django import forms
from django.contrib.auth.models import User
from .models import PTOBalance
class PTOBalanceForm(forms.ModelForm):
    class Meta:
        model = PTOBalance
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude users who already have a PTO balance record
        if self.instance and self.instance.pk:  # Editing an existing record
            self.fields['user'].queryset = User.objects.filter(pto_balance__isnull=True) | User.objects.filter(pk=self.instance.user.pk)
        else:  # Creating a new record
            self.fields['user'].queryset = User.objects.filter(pto_balance__isnull=True)