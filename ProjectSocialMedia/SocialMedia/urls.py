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
]