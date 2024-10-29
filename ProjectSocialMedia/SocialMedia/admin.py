from django.contrib import admin
from .models import UserProfileInfo

# Register your models here.
@admin.register(UserProfileInfo)
class UserProfileInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'bio', 'status', 'avatar')
    search_fields = ('user__username', 'address')