from django.contrib import admin
from django.urls import path
from articles import views

urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        views.archive,
        name='archive'
    ),

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.user_login,
        name='user_login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='user_logout'
    ),

    path(
        'article/new/',
        views.create_post,
        name='create_post'
    ),

    path(
        'article/<int:article_id>/',
        views.get_article,
        name='get_article'
    ),

]
