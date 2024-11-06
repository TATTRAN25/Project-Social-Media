from django.contrib import messages
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm,PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import UserRegistrationForm, UserProfileInfoForm
from .models import UserProfileInfo, PasswordResetOTP, FriendRequest, FriendShip, BlockedFriend
from django.db.models import Q

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
    current_user = request.user

    # Get blocked user
    blocked_user = BlockedFriend()
    if BlockedFriend.objects.filter(Q(blocker=current_user) | Q(blocked=current_user)):
        blocked_user = BlockedFriend.objects.get(
            Q(blocker=current_user) | Q(blocked=current_user)
        )
    
    return render(request, 'user/user_profile.html', {'profile': profile, 'current_user':current_user, 'blocked_user' : blocked_user})

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

# Handle friend request
# Send friend request
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    # Ensure a request isn't already sent
    if not FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect('SocialMedia:search_friends')

# Reject friend request
@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return redirect('SocialMedia:pending_friend_requests')

# Add friend
@login_required
def accept_friend_request(request, request_id):
    friend_requests = FriendRequest.objects.filter(id=request_id, to_user=request.user)
    for friend_request in friend_requests:
        friend_request.accepted = True
        friend_request.save()

        friend_request_reverses = FriendRequest()
        if FriendRequest.objects.filter(from_user=request.user):
            friend_request_reverses = FriendRequest.objects.filter(from_user=request.user)
            for friend_request_reverse in friend_request_reverses:
                friend_request_reverse.accepted = True
                friend_request_reverse.save()

        # Create a Friendship record
        FriendShip.objects.create(user1=friend_request.from_user, user2=request.user)

    return redirect('SocialMedia:friends_list')

# Display pending friend requests for the user
@login_required
def pending_friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    return render(request, 'friend/pending_requests.html', {'requests': requests})

# List friend
@login_required
def friends_list(request):
    # Fetch friendships where the logged-in user is either user1 or user2
    friendships = FriendShip.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2')

    # Prepare a list of friends
    friends = []
    for friendship in friendships:
        # Determine which user is the friend
        if friendship.user1 == request.user:
            friends.append(friendship.user2)
        else:
            friends.append(friendship.user1)

    return render(request, 'friend/friends_list.html', {'friends': friends})

# Search friend
@login_required
def search_friends(request):
    friend_request = FriendRequest()
    if (FriendRequest.objects.filter(from_user=request.user).exists()):
        friend_request = FriendRequest.objects.get(from_user=request.user)
    friend_ship = FriendShip()
    if (FriendShip.objects.filter(Q(user1=request.user) | Q(user2=request.user)).exists()):
        friend_ship = FriendShip.objects.get(Q(user1=request.user) | Q(user2=request.user))

    query = request.GET.get('friend_name')
    results = []
    if query:
        results = User.objects.filter(username__icontains=query).exclude(id=request.user.id)  # Exclude the current user

    context = {
        'results': results,
        'friend_request':friend_request,
        'friend_ship':friend_ship
    }
            
    return render(request, 'friend/search_friends.html', context)

# Delete friend
def unfriend(request, friend_id):
    friendship = get_object_or_404(
        FriendShip, 
        Q(user1=request.user, user2=friend_id) | Q(user1=friend_id, user2=request.user)
    )
    friendrequest = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=friend_id) | Q(from_user=friend_id, to_user=request.user)
    )
    friendrequest.delete()
    friendship.delete()
    return redirect('SocialMedia:friends_list')

# Block friend
def blockfriend(request, friend_id):
    # Get user to be blocked
    user_to_block = User.objects.get(id=friend_id)

    # Block user
    if not BlockedFriend.objects.filter(blocker=request.user, blocked=user_to_block).exists():
        BlockedFriend.objects.create(blocker=request.user, blocked=user_to_block)
        # Unfirend blocked user
        unfriend(request, friend_id)

    return redirect("SocialMedia:friends_list")

# Block list
def block_list(request):
    # Get blocked users
    blocked_friends = BlockedFriend.objects.filter(blocker=request.user)
    return render(request, 'friend/block_list.html', {'blocked_friends':blocked_friends})

# Unblock
def unblock(request, user_id):
    # Get blocked user
    blocked_user = BlockedFriend.objects.get(blocker=request.user, blocked=user_id)
    blocked_user.delete()
    return redirect("SocialMedia:block_list")