from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Page, Post, Share

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

        # Nếu người dùng là admin
        if self.user.is_staff:
            # Admin có thể chỉnh sửa thông tin của chính mình và status
            if self.instance.user == self.user:
                # Admin chỉnh sửa thông tin của chính mình
                pass  # Thực hiện không làm gì, giữ nguyên tất cả các trường
            else:
                # Admin chỉnh sửa thông tin của người khác, chỉ cho phép status
                self.fields['status'].required = True  # Bắt buộc trường status
                for field in self.fields:
                    if field != 'status':
                        self.fields[field].disabled = True  # Vô hiệu hóa các trường khác
        else:
            # Người dùng bình thường không được phép chỉnh sửa status
            self.fields.pop('status', None)  # Loại bỏ trường status

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

class ShareForm(forms.ModelForm):
    class Meta:
        model = Share
        fields = ['comment']  
        widgets = {
            'comment': forms.Textarea(attrs={
                'placeholder': 'Nhập bình luận...',
                'rows': 3,
                'class': 'form-control'
            }),
        }