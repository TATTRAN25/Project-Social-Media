from django.contrib import admin
from .models import UserProfileInfo, FriendRequest, FriendShip,  BlockedFriend, Follow, Notification,PaidContent

# Register your models here.
@admin.register(UserProfileInfo)
class UserProfileInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'bio', 'status', 'avatar')
    search_fields = ('user__username', 'address')

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at', 'accepted')
    search_fields = ('from_user__username', 'to_user__username')

@admin.register(FriendShip)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')

@admin.register(BlockedFriend)
class BlockFriendAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')
    search_fields = ('blocker', 'blocked')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower', 'following')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    search_fields = ('user',)

@admin.register(PaidContent)
class PaidContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'price', 'is_active') 
    list_filter = ('author', 'is_active')  
    search_fields = ('title', 'content') 
    prepopulated_fields = {'title': ('content',)}  
    ordering = ('-created_at',)  
