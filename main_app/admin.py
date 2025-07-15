from django.contrib import admin
from .models import Post, Comment

admin.site.register(Post)
# Register the new Feeding model
admin.site.register(Comment)
