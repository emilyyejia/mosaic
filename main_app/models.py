from django.db import models
from django.urls import reverse
from datetime import date
from storages.backends.s3 import S3File
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class PhotoImageStorage(S3Boto3Storage):  
    location = 'postsphotos'  # This is the name of the bucket in S3

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=500)
    tags = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    country = CountryField(blank=True, null=True)
    image = models.ImageField(
    upload_to='postsphotos/',
    storage=PhotoImageStorage(),
    null=True,
    blank=True,
    )
    def __str__(self):
        return f'{self.title}'
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'post_id': self.id})

class Comment(models.Model):
    date = models.DateField('Commented on', auto_now_add=True)
    text = models.CharField(max_length=500)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    def __str__(self):
        return f'{self.text} by {self.user} on {self.date}'
    
