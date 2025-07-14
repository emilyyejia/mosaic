from django.db import models
from django.urls import reverse
from datetime import date
# Import the User
from django.contrib.auth.models import User

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=500)
    tags = models.CharField(max_length=100)
    created_at = models.DateTimeField

    def __str__(self):
        return f'{self.title}'
    def get_absolute_url(self):
        # Use the 'reverse' function to dynamically find the URL for viewing this cat's details
        return reverse('post_detail', kwargs={'post_id': self.id})