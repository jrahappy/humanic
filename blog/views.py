from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from .models import Post, PostAttachment
from .forms import BlogForm
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.core.cache import cache
import json


@login_required
def index(request):
    # post_list = Post.objects.all().order_by("-created_at").select_related("author")
    user = request.user
    # if not user.is_authenticated:
    #     return redirect("account_login")
    # Check if the user is a staff member
    if not user.is_staff:
        #     pass
        # else:
        # 판독의의 경우
        if user.is_doctor:
            return redirect("dashboard:index")
        # 병원(고객)의 경우
        else:
            return redirect("collab:index")

    page_number = request.GET.get("page", 1)
    cache_key = f"post_list_page_{page_number}"
    post_list = cache.get(cache_key)

    if not post_list:
        post_list = (
            Post.objects.filter(is_public=True)
            .select_related("author")
            .order_by("-created_at")
        )
        paginator = Paginator(post_list, 10)
        post_list = paginator.get_page(page_number)
        cache.set(cache_key, post_list, timeout=60 * 15)  # Cache for 15 minutes

    context = {"posts": post_list}
    return render(request, "blog/index.html", context)


def create_post_admin(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            post = Post.objects.create(
                author=request.user,
                title=form.cleaned_data.get("title"),
                content=form.cleaned_data.get("content"),
            )
            files = request.FILES.getlist("attachments")
            for file in files:
                PostAttachment.objects.create(post=post, file=file)
            return redirect("blog:detail", pk=post.id)
        else:
            print(form.errors)
    else:
        form = BlogForm()
        context = {
            "form": form,
            "author": request.user,
        }
        return render(
            request,
            "blog/post_form_admin.html",
            context,
        )


def delete_file(request, file_id):
    if request.method == "DELETE":
        file = get_object_or_404(PostAttachment, id=file_id)
        file.delete()
        return HttpResponse(
            status=204, headers={"HX-Trigger": json.dumps({"fileDeleted": file_id})}
        )
    return HttpResponse(status=405)


@login_required
def home(request):
    user = request.user
    posts = (
        Post.objects.filter(author=user)
        .select_related("author")
        .order_by("-created_at")
    )
    context = {"posts": posts, "user": user, "side_menu": "blog"}
    return render(request, "blog/home.html", context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)  # Pass both POST data and FILES
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.instance.author = request.user
            new_post.save()
            files = request.FILES.getlist("attachments")
            if files:
                for file in files:
                    PostAttachment.objects.create(post=new_post, file=file)
                return redirect("blog:home")

            return redirect(
                "blog:detail", pk=new_post.id
            )  # Redirect to home after successful update

            return redirect("blog:home")  # Redirect to the desired URL after saving
        else:
            print(form.errors)  # Debugging: print any validation errors to the console
    else:
        form = BlogForm()  # Instantiate an empty form for GET requests
        # print(form)
    return render(request, "blog/post_form.html", {"form": form})


@login_required
def update_post(request, pk):
    # Safely get the post or return 404 if not found
    post = get_object_or_404(Post, id=pk)
    post_attachments = PostAttachment.objects.filter(post=post)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            files = request.FILES.getlist("attachments")
            if files:
                for file in files:
                    PostAttachment.objects.create(post=post, file=file)
                return redirect("blog:index")

            return redirect(
                "blog:detail", pk=post.id
            )  # Redirect to home after successful update
        else:
            # Handle invalid form and re-render the form with errors
            context = {
                "form": form,
                "post": post,
                "post_attachments": post_attachments,
            }
            return render(request, "blog/update_post_form.html", context)
    else:
        # Display the form pre-filled with the current post data
        form = BlogForm(instance=post)
        context = {
            "form": form,
            "post": post,
            "post_attachments": post_attachments,
        }

    return render(request, "blog/update_post_form.html", context)


def delete_post(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect("blog:index")


def detail(request, pk):
    user = request.user
    post = Post.objects.get(id=pk)
    post_attachments = PostAttachment.objects.filter(post=post)
    print(post_attachments)
    context = {
        "post": post,
        "post_attachments": post_attachments,
        "user": user,
        "side_menu": "blog",
    }
    return render(request, "blog/detail.html", context)
