from django.urls import path

from . import views

app_name = 'blogs'

urlpatterns = [
    path('post_list/', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('about/', views.about, name='about'),
]