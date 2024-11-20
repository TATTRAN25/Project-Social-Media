from django.urls import path
from . import views

app_name = "SocialMedia"

urlpatterns = [
    # url home page
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('post/<int:id>/', views.post_details, name='post_details'),
    path('contact/', views.contact, name='contact'),
    # Url registration
    path('login/', views.special, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    # url profile user
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<int:pk>/', views.user_profile, name='user_profile'),
    path('profiles/update/<int:user_id>/', views.profile_update, name='profile_update'),
    path('profiles/delete/<int:user_id>/', views.profile_delete, name='profile_delete'),
    # url reset password with OTP
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('change_password/', views.change_password, name='change_password'),
    # url Social Page,Post
    path('likes/', views.like_list, name='like_list'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<int:post_id>/react/', views.react_to_post, name='react_to_post'),
    path('page/<int:page_id>/like/', views.like_page, name='like_page'),
    path('pages/<int:page_id>/', views.page_detail, name='page_detail'),
    path('pages/manage/', views.manage_page, name='manage_page'), 
    path('pages/manage/<int:page_id>/', views.manage_page, name='manage_page'), 
    path('pages/<int:page_id>/posts/manage/', views.manage_post, name='manage_post'),
    path('posts/manage/<int:post_id>/', views.manage_post, name='manage_post_edit'),   
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('share/<int:post_id>/', views.share_post, name='new_share'), 
    path('share/<int:share_id>/<int:post_id>/', views.share_post, name='share_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('group_comment/<int:comment_id>/delete/', views.delete_group_comment, name='delete_group_comment'),
    path('group_comment/<int:comment_id>/edit/', views.edit_group_comment, name='edit_group_comment'),
    path('group_comment/<int:comment_id>/reply/', views.reply_group_comment, name='reply_group_comment'),
    path('group/<int:group_id>/members/', views.manage_group_members, name='manage_group_members'),
    # url friend
    path('friends_list/', views.friends_list, name='friends_list'),
    path('search-friends/', views.search_friends, name='search_friends'),
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('unfriend/<int:friend_id>/', views.unfriend, name='unfriend'),
    path('friends_list/block_friend/<int:friend_id>/', views.blockfriend, name='block_friend'),
    path('block_list/', views.block_list, name='block_list'),
    path('block_list/unblock/<int:user_id>/', views.unblock, name='unblock'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('notifications/', views.notification_view, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    # url group
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/update/<int:pk>/', views.update_group, name='update_group'),
    path('groups/delete/<int:pk>/', views.delete_group, name='delete_group'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/create_group_post/', views.create_group_post, name='create_group_post'),
    path('posts/<int:post_id>/approve/', views.approve_group_post, name='approve_group_post'),
    path('posts/<int:post_id>/reject/', views.reject_group_post, name='reject_group_post'),
    path('posts/<int:post_id>/edit/', views.edit_group_post, name='edit_group_post'),
    path('posts/<int:post_id>/delete/', views.delete_group_post, name='delete_group_post'),
    path('group/<int:pk>/approve/', views.approve_join_request, name='approve_join_request'),
    path('group/<int:pk>/reject/', views.reject_join_request, name='reject_join_request'),
    path('group/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('group/<int:group_id>/reject_join_request/<int:pk>/', views.reject_join_request, name='reject_join_request'),
    # url massages
    path('chat/<int:receiver_id>/', views.chat_view, name='chat_view'),
    path('delete_message/<int:message_id>/', views.delete_message_view, name='delete_message'),
    # url OnlyFan
    path('create-paid-content/', views.manage_paid_content, name='create_paid_content'),
    path('edit-paid-content/<int:content_id>/', views.manage_paid_content, name='edit_paid_content'),
    path('content/<int:content_id>/purchase/', views.purchase_content, name='purchase_content'),
]
