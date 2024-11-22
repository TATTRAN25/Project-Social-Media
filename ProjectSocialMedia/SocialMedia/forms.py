from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Page, Post, Comment, Group, GroupPost,Share, GroupComment, PersonalPost, PersonalComment,PaidContent

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
        fields = ['title', 'content', 'image', 'view_mode'] 
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Nội dung bài viết...'}),
        }
        labels = {
            'title': 'Tiêu đề',
            'content': 'Nội dung',
             'image' : 'Hình ảnh',
            'view_mode': 'Chế độ xem',
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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'editable medium-editor-textarea', 'rows': 1, 'style': 'resize: none; height: auto;', 'placeholder': 'Viết bình luận...'}),
        }

        # Cập nhật CSS cho trường nhập liệu (nếu cần)
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Viết bình luận...'})
            self.fields['image'].widget.attrs.update({'class': 'form-control-file'})

class GroupCommentForm(forms.ModelForm):
    class Meta:
        model = GroupComment
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'editable medium-editor-textarea', 'rows': 1, 'style': 'resize: none; height: auto;', 'placeholder': 'Viết bình luận...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Viết bình luận...'})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
        
        parent_comment = kwargs.get('parent_comment', None)
        super().__init__(*args, **kwargs)
        if parent_comment:
            self.instance.parent_comment = parent_comment

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'is_private']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thêm lớp CSS cho từng trường
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ['title', 'content', 'group', 'image']  # Các trường cần hiển thị trong form

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Lấy user từ kwargs (nếu có)
        group = kwargs.pop('group', None)  # Lấy group từ kwargs (nếu có)
        super().__init__(*args, **kwargs)  # Gọi __init__ của form cha (ModelForm)

        # Thêm lớp CSS cho từng trường
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

        # Nếu có user và group, chúng ta kiểm tra quyền của người dùng
        if user and group:
            # Kiểm tra nếu người dùng không phải là thành viên và không phải là người tạo nhóm
            if not group.members.filter(id=user.id).exists() and user != group.creator:
                raise forms.ValidationError("You must be a member or the creator of this group to post.")
            
            # Cập nhật queryset của trường 'group' để chỉ hiển thị nhóm mà người dùng là thành viên hoặc người tạo nhóm
            self.fields['group'].queryset = Group.objects.filter(id=group.id)

class PersonalPostForm(forms.ModelForm):
    class Meta:
        model = PersonalPost
        fields = ['title', 'content', 'image']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
            # Thêm lớp CSS cho từng trường
            self.fields['title'].widget.attrs.update({'class': 'form-control'})
            self.fields['content'].widget.attrs.update({'class': 'form-control'})
            self.fields['image'].widget.attrs.update({'class': 'form-control'})

class PersonalCommentForm(forms.ModelForm):
    class Meta:
        model = PersonalComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'editable medium-editor-textarea', 'rows': 1, 'style': 'resize: none; height: auto;', 'placeholder': 'Viết bình luận...'}),
        }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # Kiểm tra xem có thiếu trường nào không
            if not self.fields:
                raise forms.ValidationError("You must specify at least one field.")
            
class PaidContentForm(forms.ModelForm):
    class Meta:
        model = PaidContent
        fields = ['title', 'content', 'price', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề...',
                'required': 'required',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập nội dung...',
                'rows': 5,
                'required': 'required',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập giá (VNĐ)...',
                'required': 'required',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
            }),
        }

