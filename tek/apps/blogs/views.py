from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BlogCommentForm
from .models import BlogCategory, BlogPost


def post_list(request):
    posts = (
        BlogPost.objects.filter(is_published=True)
        .select_related("category")
        .annotate(approved_comments=Count('comments', filter=Q(comments__is_approved=True)))
        .order_by('-created_at')
    )
    selected_category = request.GET.get("category")
    categories = BlogCategory.objects.annotate(
        post_count=Count("posts", filter=Q(posts__is_published=True))
    ).order_by("name")

    if selected_category:
        posts = posts.filter(category__slug=selected_category)


    featured_post = posts.first()
    other_posts = posts[1:] if featured_post else posts

    return render(
        request,
        'blogs_app/post_list.html',
          {
            'featured_post': featured_post,
            'posts': other_posts,
            'categories': categories,
            'selected_category': selected_category,
        },
    )


def about(request):
    return render(request, 'blogs_app/about.html')


def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    approved_comments = post.comments.filter(is_approved=True).select_related("user").order_by("-created_at")
    pending_comments_map = request.session.get("pending_blog_comments", {})
    post_pending_ids = pending_comments_map.get(str(post.id), [])
    pending_comments_qs = post.comments.filter(
        id__in=post_pending_ids, is_approved=False
    ).select_related("user")

    if request.user.is_authenticated:
        pending_comments_qs = pending_comments_qs.filter(
            Q(user=request.user) | Q(user__isnull=True)
        )

    pending_comments = list(pending_comments_qs)
    valid_pending_ids = [comment.id for comment in pending_comments]
    if valid_pending_ids != post_pending_ids:
        pending_comments_map[str(post.id)] = valid_pending_ids
        request.session["pending_blog_comments"] = pending_comments_map
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
            comment.is_approved = False
            comment.save()
            pending_comments_map = request.session.get("pending_blog_comments", {})
            post_pending_ids = pending_comments_map.get(str(post.id), [])
            if comment.id not in post_pending_ids:
                post_pending_ids.append(comment.id)
                pending_comments_map[str(post.id)] = post_pending_ids
                request.session["pending_blog_comments"] = pending_comments_map
            messages.success(request, 'نظر شما پس از تایید ادمین نمایش داده خواهد شد.')
            return redirect('blogs:post_detail', slug=post.slug)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = BlogCommentForm(initial=initial)

    return render(
        request,
        'blogs_app/post_detail.html',
        {
            'post': post,
            'form': form,
            'approved_comments': approved_comments,
            'pending_comments': pending_comments,
        },
    )