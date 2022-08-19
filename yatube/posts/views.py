from django.shortcuts import redirect, render, get_object_or_404
from .utils import paginate_page
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.select_related("group", "author")
    page_obj = paginate_page(request, post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author", "group")
    page_obj = paginate_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    page_obj = paginate_page(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj
    }
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
    form = PostForm(request.POST or None)
    is_edit = False
    context = {'form': form, 'is_edit': is_edit}
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    form = PostForm(request.POST or None, instance=post)
    context = {'form': form, 'is_edit': is_edit, 'post': post}
    if request.method == 'POST':
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)
