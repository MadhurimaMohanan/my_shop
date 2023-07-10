# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Customer, Address


class CustomerRegistrationForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords you entered do not match')

        return cleaned_data
    

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('address_line1', 'address_line2', 'city', 'state', 'postal_code')


# end forms.py