# from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('user_feed/', views.user_feed, name='user_feed'),
    path('posts/create/', views.PostCreate.as_view(), name='post-create'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/update/', views.PostUpdate.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', views.PostDelete.as_view(), name='post-delete'),
    path('user_posts/', views.user_posts, name='user_posts'),
    path('posts/<int:post_id>/add-comment', views.add_comment, name='add-comment'),
    path('comment/<int:pk>/edit/', views.CommentUpdate.as_view(), name='comment-edit'),
    path('comment/<int:pk>/delete/', views.CommentDelete.as_view(), name='comment-delete'),
    path('posts/<int:post_id>/translate/', views.get_translated_post, name='get_translated_post'),
    path('tag/<slug:tag_slug>/', views.posts_by_tag, name='posts_by_tag'),
]
