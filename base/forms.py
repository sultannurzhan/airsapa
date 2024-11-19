from django import forms
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget



class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}), label="Password")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username does not exist.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password
    


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    country = CountryField(blank_label='Select Country').formfield(
        widget=CountrySelectWidget(attrs={'class': 'form-control'})
    )
    city = forms.CharField(max_length=100, label='City', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise forms.ValidationError("Passwords do not match")
        return password_confirmation