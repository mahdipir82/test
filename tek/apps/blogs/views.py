from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BlogCommentForm
from .models import BlogPost


def post_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, 'blogs_app/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    approved_comments = post.comments.filter(is_approved=True)
    average_rating = approved_comments.aggregate(avg=Avg('rating')).get('avg') or 0

    if request.method == 'POST':
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.user = request.user
                if not comment.name:
                    comment.name = request.user.get_full_name() or request.user.username
                if not comment.email:
                    comment.email = request.user.email
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = BlogCommentForm(initial=initial)

    context = {
        'post': post,
        'comments': approved_comments,
        'average_rating': round(average_rating, 1) if average_rating else 0,
        'form': form,
    }
    return render(request, 'blogs_app/post_detail.html', context)