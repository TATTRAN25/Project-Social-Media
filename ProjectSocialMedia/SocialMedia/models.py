from django.db import models
from django.contrib.auth.models import User
import random
import string
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

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.save()

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_request', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"

class FriendShip(models.Model):
    user1 = models.ForeignKey(User, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendships2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user1', 'user2'), ('user2', 'user1'))

    def __str__(self):
        return f"{self.user1} is friends with {self.user2}"
    
class BlockedFriend(models.Model):
    blocker = models.ForeignKey(User, related_name="blocked_by", on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name="blocked_users", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f'{self.blocker.username} blocks {self.blocked.username}'