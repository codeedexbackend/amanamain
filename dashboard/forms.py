from django import forms
from .models import AddTailors

class TailorForm(forms.ModelForm):
    class Meta:
        model = AddTailors
        fields = ['tailor','username','password','mobile_number']
