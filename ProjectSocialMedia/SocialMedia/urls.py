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
]