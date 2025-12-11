from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render


def post_list(request):
    return render(request, 'blogs_app/post_list.html')

def about(request):
    return render(request, 'blogs_app/about.html')