from django.urls import path

from . import views

app_name = 'blogs'

urlpatterns = [
    path('post_list/', views.post_list, name='post_list'),
    path('about/', views.about, name='about'),
]