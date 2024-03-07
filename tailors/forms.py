# tailors/forms.py
from django import forms
from .models import Order, AddTailor
from django.contrib.auth.forms import UserCreationForm

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_date', 'tailor']  # Exclude 'order_date' from fields

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['tailor'].queryset = AddTailor.objects.all()


class TailorForm(UserCreationForm):
    tailor_name = forms.CharField(max_length=100)
    mobile_number = forms.CharField(max_length=15)

    class Meta:
        model = AddTailor
        fields = ['tailor_name','username', 'password', 'mobile_number']

class TailorSelectionForm(forms.Form):
    tailor = forms.ModelChoiceField(queryset=AddTailor.objects.all(), empty_label="Select a tailor")
