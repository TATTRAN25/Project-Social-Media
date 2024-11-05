from django.contrib import messages
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import SetPasswordForm,PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import UserRegistrationForm, UserProfileInfoForm, PageForm, PostForm
from .models import UserProfileInfo, PasswordResetOTP, Page, Post

# Tự động thêm profile nếu tạo tk admin
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfileInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    profile, created = UserProfileInfo.objects.get_or_create(user=instance)
    profile.save()  
# Chức năng đăng ký, đăng nhập
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Đăng ký thành công! Vui lòng cập nhật hồ sơ của bạn.')
            return redirect('SocialMedia:user_login')
        else:
            for error in user_form.non_field_errors():
                messages.error(request, error)

    else:
        user_form = UserRegistrationForm()
    
    return render(request, 'user/register.html', {
        'user_form': user_form,
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            profile = get_object_or_404(UserProfileInfo, user=user)
            if profile.status == 'banned':
                messages.error(request, 'Tài khoản của bạn đã bị cấm truy cập.')
                return redirect('SocialMedia:user_login')
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('SocialMedia:index')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác.')
    
    return render(request, 'user/login.html')

@login_required
def special(request):
    return HttpResponse("Bạn đang đăng nhập!")

def user_logout(request):
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công!')
    return HttpResponseRedirect(reverse('SocialMedia:index'))
# Quản lý hồ sơ người dùng
def profile_list(request):
    if request.user.is_staff:
        profiles = UserProfileInfo.objects.all()
        return render(request, 'user/profile_list.html', {'profiles': profiles})
    else:
        messages.error(request, 'Bạn không có quyền truy cập vào danh sách hồ sơ.')
        return redirect('SocialMedia:index') 
    
@login_required
def user_profile(request, pk):
    profile = get_object_or_404(UserProfileInfo, pk=pk)
    if request.user.is_staff:
        pages = Page.objects.all()  
    else:
        pages = Page.objects.filter(author=request.user) 
    return render(request, 'user/user_profile.html', {'profile': profile, 'pages': pages})

@login_required
def profile_update(request, user_id):
    profile = get_object_or_404(UserProfileInfo, id=user_id)

    if request.method == 'POST':
        form = UserProfileInfoForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hồ sơ đã được cập nhật thành công!')
            return redirect('SocialMedia:user_profile', pk=profile.pk)
    else:
        form = UserProfileInfoForm(instance=profile, user=request.user)

    return render(request, 'user/profile_form.html', {'form': form, 'profile': profile})
def profile_delete(request, user_id):
    if request.user.is_staff:
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfileInfo.objects.filter(user=user).first()
        if user_profile:
            user_profile.delete()
        user.delete()
        return redirect('SocialMedia:profile_list')
    else:
        return render(request, 'user/profile_list.html')
    
# Gửi mã OTP về cho người dùng
def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            otp_instance = PasswordResetOTP(user=user)
            otp_instance.generate_otp()

            send_mail(
                'Your OTP for Password Reset',
                f'Your OTP is {otp_instance.otp}',
                'anhtuan251104@gmail.com',  
                [email],
                fail_silently=False,
            )
            messages.success(request, 'OTP đã được gửi tới email của bạn.')
            return redirect('SocialMedia:verify_otp')
        else:
            messages.error(request, 'Email không tồn tại.')
    
    return render(request, 'user/send_otp.html')

# Xác thực đoạn mã OTP cho người dùng
def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        try:
            user = User.objects.get(email=email)
            otp_instance = PasswordResetOTP.objects.get(user=user, otp=otp)

            if (timezone.now() - otp_instance.created_at).seconds < 300:
                return redirect('SocialMedia:reset_password', user_id=user.id)
            else:
                messages.error(request, 'OTP đã hết hạn.')
        except (User.DoesNotExist, PasswordResetOTP.DoesNotExist) as e:
            messages.error(request, 'OTP không hợp lệ.')
            print(f'Error: {e}')

    return render(request, 'user/verify_otp.html')
# Reset password
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, 'Password đã được reset thành công.')
            return redirect('SocialMedia:user_login') 
    else:
        form = SetPasswordForm(user)

    return render(request, 'user/reset_password.html', {'form': form})

# Thay đổi mật khẩu@login_required
@login_required
def change_password(request, user_id):
    profile = get_object_or_404(UserProfileInfo, id=user_id)
    user = profile.user  

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST) 
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
            return redirect('SocialMedia:user_profile', pk=profile.pk)  
    else:
        form = PasswordChangeForm(user)  

    return render(request, 'user/change_password.html', {'form': form})

# Crud Page
@login_required
def manage_page(request, page_id=None):
    if page_id:
        # Cập nhật trang nếu page_id có giá trị
        page = get_object_or_404(Page, id=page_id)
        form = PageForm(request.POST or None, instance=page)
    else:
        # Tạo trang mới
        page = None
        form = PageForm(request.POST or None)

    if form.is_valid():
        page = form.save(commit=False)
        page.author = request.user
        page.save()
        if page_id:
            messages.success(request, 'Trang đã được cập nhật thành công!')
            return redirect('SocialMedia:page_list')
        else:
            messages.success(request, 'Trang đã được tạo thành công!')
            return redirect('SocialMedia:page_list')

    return render(request, 'Social/manage_page.html', {'form': form, 'page': page})

@login_required
def page_list(request):
    # Kiểm tra trạng thái của người dùng
    if request.user.userprofileinfo.status == 'inactive':
        messages.error(request, 'Tài khoản của bạn đã bị tạm ngưng, bạn không thể xem bài viết.')
        return redirect('SocialMedia:index')

    # Xử lý yêu cầu xóa trang
    if request.method == 'POST' and 'delete_page_id' in request.POST:
        page_id = request.POST['delete_page_id']
        page = get_object_or_404(Page, id=page_id)
        if page.author == request.user or request.user.is_staff:
            page.delete()
            messages.success(request, 'Trang đã được xóa thành công!')
        else:
            messages.error(request, 'Bạn không có quyền xóa trang này.')
        return redirect('SocialMedia:page_list')

    # Lấy danh sách trang dựa trên quyền truy cập
    if request.user.is_staff:
        pages = Page.objects.all() 
    else:
        pages = Page.objects.filter(author=request.user)  

    return render(request, 'Social/page_list.html', {'pages': pages})

# Crud Post
@login_required
def manage_post(request, post_id=None, page_id=None):
    # Kiểm tra trạng thái tài khoản
    if request.user.userprofileinfo.status == 'inactive':
        messages.error(request, 'Tài khoản của bạn đã bị tạm ngưng, bạn không thể đăng bài viết.')
        return redirect('SocialMedia:index')

    # Xử lý bài viết đã tồn tại
    if post_id:
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user and not request.user.is_staff:
            messages.error(request, 'Bạn không có quyền chỉnh sửa bài viết này.')
            return redirect('SocialMedia:post_detail', post_id=post.id)
        form = PostForm(request.POST or None, request.FILES or None, instance=post) 
        action = 'Cập Nhật'
    else:
        post = None
        form = PostForm(request.POST or None, request.FILES or None)  
        action = 'Đăng Bài Viết'

    # Xử lý form khi được gửi
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            if not post_id:
                new_post.page = get_object_or_404(Page, id=page_id)
                new_post.author = request.user
            new_post.save()
            messages.success(request, f'Bài viết đã được {action.lower()} thành công!')
            return redirect('SocialMedia:post_detail', post_id=new_post.id)

    return render(request, 'Social/manage_post.html', {
        'form': form,
        'post': post,
        'action': action
    })
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Kiểm tra trạng thái tài khoản
    if request.user.userprofileinfo.status == 'inactive':
        messages.error(request, 'Tài khoản của bạn đã bị tạm ngưng, bạn không thể xóa bài viết.')
        return redirect('SocialMedia:index')

    # Xử lý xóa bài viết
    if request.method == 'POST':
        if request.user == post.author or request.user.is_staff:
            post.delete()
            messages.success(request, 'Bài viết đã được xóa thành công!')
            return redirect('SocialMedia:page_list')
        else:
            messages.error(request, 'Bạn không có quyền xóa bài viết này.')

    return render(request, 'Social/post_detail.html', {'post': post})
def index(request):
    posts = Post.objects.all().prefetch_related('likes').order_by('-created_at')
    pages = Page.objects.all()
    
    if request.user.is_authenticated:
        liked_posts = request.user.liked_posts.all()
        liked_post_ids = set(post.id for post in liked_posts)
    else:
        liked_post_ids = set()

    return render(request, 'home/index.html', {
        'posts': posts,
        'pages': pages,
        'liked_post_ids': liked_post_ids,
    })

@csrf_exempt
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            is_liked = False
        else:
            post.likes.add(request.user)
            is_liked = True
        data = {
            'is_liked': is_liked,
            'likes_count': post.likes.count()
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)

    
def about(request):
    return render(request, 'home/about.html')

def blog(request):
    return render(request, 'home/blog.html')

def post_details(request):
    return render(request, 'home/post_details.html')

def contact(request):
    return render(request, 'home/contact.html')
