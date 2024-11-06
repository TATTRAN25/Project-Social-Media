from django.contrib import admin
from .models import UserProfileInfo, FriendRequest, FriendShip,  BlockedFriend

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