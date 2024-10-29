from django.db import models
from django.contrib.auth.models import User

class UserProfileInfo(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, blank=True)  
    bio = models.CharField(max_length=250, blank=True) 
    avatar = models.ImageField(upload_to='user_pics/', blank=True)  
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.user.username