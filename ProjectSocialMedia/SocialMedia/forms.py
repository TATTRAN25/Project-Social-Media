from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Page, Post

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, help_text='Mật khẩu phải có ít nhất 8 ký tự.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Tên người dùng',
            'email': 'Địa chỉ email',
        }

class UserLoginForm(forms.Form):
    username = forms.CharField(label='Tên người dùng')
    password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu')

class UserProfileInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ['address', 'bio', 'avatar', 'cover_photo', 'status']
        labels = {
            'address': 'Địa chỉ',
            'bio': 'Tiểu sử',
            'avatar': 'Ảnh đại diện',
            'cover_photo': 'Ảnh bìa',
            'status': 'Trạng thái',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.user.is_staff:
            self.fields.pop('status', None)

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'content']  
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Nội dung trang...'}),
        }
        labels = {
            'title': 'Tiêu đề',
            'content': 'Nội dung',
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image'] 
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Nội dung bài viết...'}),
        }
        labels = {
            'title': 'Tiêu đề',
            'content': 'Nội dung',
             'image' : 'Hình ảnh',
        }