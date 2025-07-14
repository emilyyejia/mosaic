# from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('user_feed/', views.user_feed, name='user_feed'),
    path('posts/create/', views.PostCreate.as_view(), name='post-create'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

]
