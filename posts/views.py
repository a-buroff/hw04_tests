from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm

POSTS_PER_PAGE = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "group.html",
        {"group": group, "page": page, "paginator": paginator}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    form_title = "Добавить запись"
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect("index")
    return render(request, "new.html",
                  {"form": form, "form_title": form_title})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if request.user.username != username:
        raise Http404('Вы не являетесь автором этого поста')
    if request.method == "POST":
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post", post.author, post.id)
    form = PostForm(instance=post)
    form_title = "Редактировать запись"
    context = {"form": form, "post": post, "form_title": form_title}
    return render(request, "new.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    viewer = request.user.username
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {"author": author, "viewer": viewer,
               "page": page, "paginator": paginator}
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    viewer = request.user.username
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    context = {"author": author, "viewer": viewer,
               "post": post, "post_id": post_id, "paginator": paginator}
    return render(request, "post.html", context)
