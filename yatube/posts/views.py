from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm

SELECT_NUM = 10


def get_page_context(request, queryset):
    paginator = Paginator(queryset, SELECT_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj
    }


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    context = get_page_context(request, post_list)
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group
    }
    context.update(get_page_context(request, posts))
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    context = {
        'author': author
    }
    context.update(get_page_context(request, post_list))
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form_class = PostForm(request.POST or None)
    context = {
        'form': form_class
    }
    if request.method == 'POST':
        if form_class.is_valid():
            form = form_class.save(commit=False)
            form.author = request.user
            form.save()
            return redirect(
                'posts:profile', form.author
            )
        return render(request, template, context)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(
            'posts:post_detail', post_id
        )
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail', post_id
        )
    context = {
        'form': form,
        'is_edit': True,
        'post': post
    }
    return render(request, template, context)
