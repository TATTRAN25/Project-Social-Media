from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import (
    UserRegistrationForm,
    UserProfileInfoForm,
    PageForm,
    PostForm,
    CommentForm,
    GroupForm,
    GroupPostForm,
    ShareForm,
)
from .models import (
    UserProfileInfo,
    PasswordResetOTP,
    FriendRequest,
    FriendShip,
    BlockedFriend,
    Page,
    Post,
    Comment,
    Group,
    GroupPost,
    JoinRequest,
    Reaction,
    Share,
    Follow,
    Notification,
)
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
    pages = Page.objects.filter(author=profile.user)
    groups = Group.objects.filter(creator=profile.user)  # Lọc các group mà người dùng là creator
    join_requests = JoinRequest.objects.filter(group__creator=request.user, status='pending')
    current_user = request.user
    shared_posts = Share.objects.filter(user=profile.user).select_related('post')
    # Get blocked user
    blocked_user = BlockedFriend()
    if BlockedFriend.objects.filter(Q(blocker=current_user, blocked=pk) | Q(blocked=current_user, blocker=pk)).exists():
        blocked_user = BlockedFriend.objects.get(
            Q(blocker=current_user, blocked=pk) | Q(blocker=pk, blocked=current_user)
        )
    # Get follow status
    follow = Follow()
    if Follow.objects.filter(follower=current_user, following=pk).exists():
        follow = Follow.objects.get(follower=current_user, following=pk)
    
    return render(request, 'user/user_profile.html', {'profile': profile, 'pages': pages , 'current_user':current_user, 'blocked_user' : blocked_user, 'join_requests': join_requests, 'groups': groups, 'follow':follow, 'shared_posts': shared_posts})

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

# Thay đổi mật khẩu
@login_required
def change_password(request):
    user = request.user  # Lấy người dùng hiện tại

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST) 
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Cập nhật phiên người dùng
            messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
            return redirect('SocialMedia:user_profile', pk=user.id)  # Chuyển hướng đến trang hồ sơ người dùng
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

    if request.method == 'POST' and form.is_valid():
        page = form.save(commit=False)
        page.author = request.user
        page.save()
        if page_id:
            messages.success(request, 'Trang đã được cập nhật thành công!')
        else:
            messages.success(request, 'Trang đã được tạo thành công!')
        return redirect('SocialMedia:page_detail', page_id=page.id)  

    return render(request, 'Social/manage_page.html', {'form': form, 'page': page})

@login_required
def page_detail(request, page_id):
    # Kiểm tra trạng thái của người dùng
    if request.user.userprofileinfo.status == 'inactive':
        messages.error(request, 'Tài khoản của bạn đã bị tạm ngưng, bạn không thể xem bài viết.')
        return redirect('SocialMedia:index')

    # Xử lý yêu cầu xóa trang
    if request.method == 'POST' and 'delete_page_id' in request.POST:
        page_id = request.POST['delete_page_id']
        page = get_object_or_404(Page, id=page_id)
        if page.author == request.user or request.user.is_staff:
            page.posts.all().delete()
            page.delete()
            messages.success(request, 'Trang và các bài viết đã được xóa thành công!')
        else:
            messages.error(request, 'Bạn không có quyền xóa trang này.')
        return redirect('SocialMedia:index')  
    # Lấy trang theo page_id
    page = get_object_or_404(Page, id=page_id)
    posts = page.posts.all()  

    return render(request, 'Social/page_detail.html', {'page': page, 'posts': posts})

# Crud Post
@login_required
def manage_post(request, post_id=None, page_id=None):
    if request.user.userprofileinfo.status == 'inactive':
        messages.error(request, 'Tài khoản của bạn đã bị tạm ngưng, bạn không thể đăng bài viết.')
        return redirect('SocialMedia:index')

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

    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            if not post_id:
                new_post.page = get_object_or_404(Page, id=page_id)
                new_post.author = request.user
            
            new_post.view_mode = form.cleaned_data['view_mode']  
            new_post.save()
            messages.success(request, f'Bài viết đã được {action.lower()} thành công!')
            return redirect('SocialMedia:post_detail', post_id=new_post.id)
        else:
            messages.error(request, 'Có lỗi trong việc lưu bài viết. Vui lòng kiểm tra lại.')

    return render(request, 'Social/manage_post.html', {
        'form': form,
        'post': post,
        'action': action
    })

@login_required
def post_detail(request, post_id):
    # Get the post or return a 404 if it doesn't exist
    post = get_object_or_404(Post, id=post_id)

    # Check account status
    if request.user.userprofileinfo.status == 'inactive':
        messages.error(request, 'Tài khoản của bạn đã bị tạm ngưng, bạn không thể xem bài viết.')
        return redirect('SocialMedia:index')

    # Determine if the user can view the post
    can_view = False

    if post.author == request.user:
        can_view = True
    elif post.view_mode == 'public':
        can_view = True
    elif post.view_mode == 'private':
        can_view = FriendShip.objects.filter(
            (Q(user1=request.user) & Q(user2=post.author)) |
            (Q(user1=post.author) & Q(user2=request.user))
        ).exists()
    elif post.view_mode == 'only_me':
        can_view = False  # Only the author can view this

    if not can_view:
        messages.error(request, 'Bạn không có quyền xem bài viết này.')
        return redirect('SocialMedia:index')

    # Fetch comments for the post
    comments = post.comments.filter(parent_comment__isnull=True)
    form = CommentForm()

    # Handle post deletion
    if request.method == 'POST':
        if 'delete_post' in request.POST:
            if request.user == post.author or request.user.is_staff:
                post.delete()
                messages.success(request, 'Bài viết đã được xóa thành công!')
                return redirect('SocialMedia:page_detail', post.page.id)
            else:
                messages.error(request, 'Bạn không có quyền xóa bài viết này.')
        elif 'comment' in request.POST:  # Handle comment submission
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.author = request.user
                new_comment.post = post

                # Check if it's a reply to another comment
                parent_comment_id = request.POST.get('parent_comment')
                if parent_comment_id:
                    parent_comment = get_object_or_404(Comment, id=parent_comment_id)
                    new_comment.parent_comment = parent_comment

                new_comment.save()
                messages.success(request, 'Bình luận của bạn đã được đăng!')
                return redirect('SocialMedia:post_detail', post_id=post.id)

    # Count reactions
    reactions_count = {
        'like': post.reaction_set.filter(reaction_type='like').count(),
        'love': post.reaction_set.filter(reaction_type='love').count(),
        'sad': post.reaction_set.filter(reaction_type='sad').count(),
        'angry': post.reaction_set.filter(reaction_type='angry').count(),
        'wow': post.reaction_set.filter(reaction_type='wow').count(),
    }

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'reactions_count': reactions_count,
    }

    return render(request, 'Social/post_detail.html', context)

def can_user_view_post(user, post):
    if post.author == user:
        return True
    if post.view_mode == 'public':
        return True
    if post.view_mode == 'private':
        return FriendShip.objects.filter(
            (Q(user1=user) & Q(user2=post.author)) |
            (Q(user1=post.author) & Q(user2=user))
        ).exists()
    if post.view_mode == 'only_me':
        return False
    return False
    

@login_required
def delete_comment(request, comment_id):
    # Lấy bình luận cần xóa
    comment = get_object_or_404(Comment, id=comment_id)

    # Kiểm tra xem người dùng có quyền xóa bình luận không
    if request.user == comment.author or request.user.is_staff:
        # Nếu bình luận là phản hồi, chúng ta không cần phải xóa các bình luận con của nó.
        # Nếu bình luận là bình luận gốc, xóa các bình luận con.
        if not comment.parent_comment:
            # Xóa tất cả các bình luận con (reply) của bình luận gốc
            comment.replies.all().delete()
        
        # Xóa bình luận chính (cha hoặc trả lời)
        comment.delete()
        messages.success(request, 'Bình luận đã được xóa thành công!')
    else:
        messages.error(request, 'Bạn không có quyền xóa bình luận này.')

    # Chuyển hướng về trang chi tiết bài viết hoặc trang danh sách bình luận
    return redirect('SocialMedia:post_detail', post_id=comment.post.id)

def index(request):
    posts = Post.objects.all().prefetch_related('likes').order_by('-created_at')
    pages = Page.objects.all()
    shared_posts = Share.objects.select_related('post').order_by('-created_at')

    if request.user.is_authenticated:
        liked_posts = request.user.liked_posts.all()
        liked_post_ids = set(post.id for post in liked_posts)

        # Lọc bài viết chính dựa trên view_mode
        visible_posts = []
        for post in posts:
            if can_user_view_post(request.user, post):
                visible_posts.append(post)

        # Lọc các bài viết đã chia sẻ
        visible_shared_posts = []
        for share in shared_posts:
            # Kiểm tra quyền truy cập bài viết đã chia sẻ
            if can_user_view_post(request.user, share.post):
                visible_shared_posts.append(share)

    else:
        liked_post_ids = set()
        visible_posts = posts.filter(view_mode='public')
        visible_shared_posts = shared_posts.filter(post__view_mode='public')

    return render(request, 'home/index.html', {
        'posts': visible_posts,
        'pages': pages,
        'liked_post_ids': liked_post_ids,
        'shared_posts': visible_shared_posts,
    })

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

@login_required
def like_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)

    if request.user in page.likes.all():
        # Nếu người dùng đã "like" rồi, bỏ "like"
        page.likes.remove(request.user)
    else:
        # Nếu chưa "like", thêm vào danh sách "liked"
        page.likes.add(request.user)

    return redirect('SocialMedia:page_detail', page_id=page.id)
    
@login_required
def like_list(request):
    # Lấy danh sách các trang mà người dùng đã like
    liked_pages = Page.objects.filter(likes=request.user)

    # Lấy danh sách các bài viết mà người dùng đã like
    liked_posts = Post.objects.filter(likes=request.user)
    context = {
        'liked_pages': liked_pages,
        'liked_posts': liked_posts,
    }
    return render(request, 'Social/like_list.html', context)

@login_required
def react_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    reaction_type = request.POST.get('reaction_type')
    # Kiểm tra xem người dùng đã phản ứng hay chưa
    existing_reaction = post.reaction_set.filter(user=request.user).first()

    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Nếu đã phản ứng với loại này, xóa phản ứng
            existing_reaction.delete()
            created = False
        else:
            # Nếu phản ứng khác, cập nhật loại phản ứng
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
            created = True
    else:
        # Tạo phản ứng mới
        reaction = Reaction.objects.create(user=request.user, post=post, reaction_type=reaction_type)
        created = True

    # Tính toán số lượng phản ứng mới
    reactions_count = {
        'like': post.reaction_set.filter(reaction_type='like').count(),
        'love': post.reaction_set.filter(reaction_type='love').count(),
        'sad': post.reaction_set.filter(reaction_type='sad').count(),
        'angry': post.reaction_set.filter(reaction_type='angry').count(),
        'wow': post.reaction_set.filter(reaction_type='wow').count(),
    }

    return JsonResponse({'success': True, 'reactions_count': reactions_count, 'created': created})

@login_required
def share_post(request, share_id=None, post_id=None):
    post = get_object_or_404(Post, id=post_id) if post_id else None

    if share_id:
        share = get_object_or_404(Share, id=share_id)
        form = ShareForm(request.POST or None, instance=share)
    else:
        share = None
        form = ShareForm(request.POST or None)

    if request.method == 'POST':
        if 'delete' in request.POST and share:
            share.delete()  
            return redirect('SocialMedia:user_profile', pk=request.user.id)  
        elif form.is_valid():
            new_share = form.save(commit=False)
            new_share.user = request.user  
            new_share.post = post  
            new_share.save()  
            return redirect('SocialMedia:user_profile', pk=request.user.id)  

    return render(request, 'Social/share_post.html', {
        'form': form,
        'share': share,
        'post': post, 
    })

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
    return redirect('SocialMedia:notifications')

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
    # Get all friendships involving the logged-in user
    friend_ships = FriendShip.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    
    # Create a dictionary to store friendship status (True if the user is a friend)
    friend_status = {}
    for friendship in friend_ships:
        if friendship.user1.id == request.user.id:
            friend_status[friendship.user2.id] = 'friend'
        elif friendship.user2.id == request.user.id:
            friend_status[friendship.user1.id] = 'friend'

    # Check for pending friend requests sent by the current user or received by the current user
    pending_requests = {}
    sent_requests = FriendRequest.objects.filter(from_user=request.user, accepted=False)
    for request_sent in sent_requests:
        pending_requests[request_sent.to_user.id] = 'sent'

    # Search query
    query = request.GET.get('friend_name', '').strip()
    results = []

    if query:
        results = User.objects.filter(username__icontains=query).exclude(id=request.user.id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        suggestions = []
        users = User.objects.exclude(id=request.user.id)
        for user in users:
            if user.id not in friend_status:
                suggestions.append({
                    'id': user.id,
                    'username': user.username,
                })

        return JsonResponse({'suggestions': suggestions})

    # Render the regular template when it's not an AJAX request
    return render(request, 'friend/search_friends.html', {
        'results': results,
        'friend_status': friend_status,
        'pending_requests': pending_requests,
    })


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

# Folow other user
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    Follow.objects.create(follower=request.user, following=user_to_follow)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

# Unfollow
def unfollow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_follow).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

# Send notification to follower
@login_required
def notification_view(request):
    # Fetch notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    friend_requests = FriendRequest.objects.filter(to_user=request.user, accepted=False).order_by('-created_at')
    return render(request, 'friend/notifications.html', {'notifications': notifications, 'friend_requests':friend_requests})

@login_required
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
    except Notification.DoesNotExist:
        pass
    return redirect('SocialMedia:notifications')

def group_list(request):
    groups = Group.objects.all()  # Lấy tất cả nhóm từ cơ sở dữ liệu
    return render(request, 'Social/group_list.html', {'groups': groups})

def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            return redirect('SocialMedia:group_list')  # Sau khi tạo nhóm, chuyển tới danh sách nhóm
    else:
        form = GroupForm()

    return render(request, 'Social/create_group.html', {'form': form})

def update_group(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if group.creator != request.user:
        return redirect('SocialMedia:group_detail', pk=group.pk)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('SocialMedia:user_profile', pk=request.user.pk)  # Sau khi cập nhật, chuyển tới danh sách nhóm
    else:
        form = GroupForm(instance=group)

    return render(request, 'Social/update_group.html', {'form': form, 'group': group})

@login_required
def delete_group(request, pk):
    # Lấy nhóm với ID = pk
    group = get_object_or_404(Group, pk=pk)

    # Kiểm tra quyền của người dùng
    if group.creator != request.user:
        return redirect('SocialMedia:group_detail', pk=group.pk)

    # Nếu là POST request, thực hiện xóa
    if request.method == 'POST':
        group.delete()  # Xóa nhóm
        return redirect('SocialMedia:user_profile', pk=request.user.pk)  # Chuyển hướng về trang người dùng

    # Nếu không phải POST, trả về trang xác nhận xóa (confirmation)
    return render(request, 'Social/confirm_delete_group.html', {'group': group})

@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    posts = GroupPost.objects.filter(group=group).order_by('-created_at')
    # Lọc yêu cầu tham gia nhóm chỉ cho nhóm này
    join_requests = JoinRequest.objects.filter(group=group, status='pending')
    # Kiểm tra xem người dùng có phải là thành viên của nhóm hay không
    is_member = request.user in group.members.all()

    return render(request, 'Social/group_detail.html', {
        'group': group,
        'posts': posts,
        'is_member': is_member,
        'join_requests': join_requests,
    })

@login_required
def join_group(request, pk):
    group = get_object_or_404(Group, pk=pk)

    # Kiểm tra nếu người dùng đã là thành viên của nhóm
    if group.members.filter(id=request.user.id).exists():
        messages.info(request, 'Bạn đã là thành viên của nhóm này.')
        return redirect('SocialMedia:group_detail', pk=group.pk)

    # Kiểm tra xem người dùng đã gửi yêu cầu tham gia hay chưa
    if JoinRequest.objects.filter(user=request.user, group=group, status='pending').exists():
        messages.info(request, 'Bạn đã gửi yêu cầu tham gia nhóm này rồi.')
        return redirect('SocialMedia:group_detail', pk=group.pk)

    # Tạo yêu cầu tham gia
    JoinRequest.objects.create(user=request.user, group=group, status='pending')
    messages.success(request, 'Bạn đã gửi yêu cầu tham gia nhóm thành công!')

    return redirect('SocialMedia:group_detail', pk=group.pk)

@login_required
def create_post(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    # if request.user not in group.members.all():
    #     return redirect('SocialMedia:group_detail', group_id=group.id)

    if request.method == 'POST':
        form = GroupPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.group = group
            post.save()
            return redirect('SocialMedia:group_detail', group_id=group.id)
    else:
        form = GroupPostForm()

    return render(request, 'Social/create_post.html', {'form': form, 'group': group})

@login_required
def approve_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.group.creator != request.user:
        return redirect('SocialMedia:group_detail', group_id=post.group.id)

    if request.method == 'POST':
        post.status = 'approved'
        post.save()
        return redirect('SocialMedia:group_detail', group_id=post.group.id)

    return render(request, 'Social/approve_post.html', {'post': post})

@login_required
def reject_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.group.creator != request.user:
        return redirect('SocialMedia:group_detail', group_id=post.group.id)

    if request.method == 'POST':
        post.status = 'rejected'
        post.save()
        return redirect('SocialMedia:group_detail', group_id=post.group.id)

    return render(request, 'Social/reject_post.html', {'post': post})

@login_required
def manage_join_requests(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Chỉ người tạo nhóm mới có quyền quản lý yêu cầu tham gia
    if group.creator != request.user:
        return redirect('SocialMedia:group_detail', group_id=group.id)

    join_requests = group.join_requests.filter(status='pending')

    return render(request, 'SocialMedia/manage_join_requests.html', {'group': group, 'join_requests': join_requests})

@login_required
def approve_join_request(request, pk):
    join_request = get_object_or_404(JoinRequest, pk=pk)
    
    if request.user == join_request.group.creator:
        join_request.status = 'approved'
        join_request.save()
        join_request.group.members.add(join_request.user)
        messages.success(request, f"Đã phê duyệt yêu cầu tham gia của {join_request.user.username}")
    else:
        messages.error(request, "Bạn không có quyền phê duyệt yêu cầu tham gia nhóm này.")
    
    return redirect('SocialMedia:group_detail', pk=join_request.group.pk)

@login_required
def reject_join_request(request, pk):
    join_request = get_object_or_404(JoinRequest, pk=pk)
    
    if request.user == join_request.group.creator:
        join_request.status = 'rejected'
        join_request.save()
        messages.success(request, f"Đã từ chối yêu cầu tham gia của {join_request.user.username}")
    else:
        messages.error(request, "Bạn không có quyền từ chối yêu cầu tham gia nhóm này.")
    
    return redirect('SocialMedia:user_profile')