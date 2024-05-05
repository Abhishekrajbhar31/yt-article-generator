from django.contrib import admin
from django.contrib.auth.models import User
from .models import BlogPost
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    
class CustomBlogPost(admin.ModelAdmin):
    list_display = ('youtube_title', 'user' , 'created_at')

# Register the custom admin class with the User model
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(BlogPost,CustomBlogPost)