from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserProfileInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ['address', 'bio', 'avatar', 'cover_photo']  

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if not self.user.is_staff:
            self.fields.pop('status')
