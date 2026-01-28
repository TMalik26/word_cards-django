from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from users.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    username = forms.CharField()
    password = forms.CharField()


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name", 
            "last_name",
            "username",
            "email",
            "password1",
            "password2"
        ]

    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()


class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            "image",
            "first_name",
            "last_name",
            "username",
            "email"
        ]
    
    image = forms.ImageField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()