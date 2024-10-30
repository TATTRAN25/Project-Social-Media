from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import UserRegistrationForm, UserProfileInfoForm
from .models import UserProfileInfo, PasswordResetOTP

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
    return render(request, 'user/user_profile.html', {'profile': profile})

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
def index(request):
    return render(request, 'home/index.html')

def about(request):
    return render(request, 'home/about.html')

def blog(request):
    return render(request, 'home/blog.html')

def post_details(request):
    return render(request, 'home/post_details.html')

def contact(request):
    return render(request, 'home/contact.html')
