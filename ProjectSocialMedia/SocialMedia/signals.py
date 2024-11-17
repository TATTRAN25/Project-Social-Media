from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Follow, Notification, Post, FriendRequest

@receiver(post_save, sender=Follow)
def send_follow_notification(sender, instance, created, **kwargs):
    """Send notification to user when someone follows them."""
    if created:
        notification_message = f"{instance.follower.username} started following you."
        Notification.objects.create(user=instance.following, message=notification_message)


@receiver(post_save, sender=Post)  # Assume 'Post' is your model for user posts
def send_post_notification(sender, instance, created, **kwargs):
    """Notify followers when a user creates a new post."""
    if created:
        followers = Follow.objects.filter(following=instance.page.author)
        for follow in followers:
            notification_message = f"{instance.page.author.username} posted something new."
            Notification.objects.create(user=follow.follower, message=notification_message)
