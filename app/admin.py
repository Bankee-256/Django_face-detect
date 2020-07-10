from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Result, Like

from .models import UserProfile


class ProfileInline(admin.StackedInline):  # 将UserProfile加入到Admin的user表中
    model = UserProfile
    verbose_name = 'profile'


class UserProfileAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)  # 去掉在admin中的注册
admin.site.register(User, UserProfileAdmin)
admin.site.register(Result)
admin.site.register(Like)
# Register your models here.
