from django.shortcuts import render, redirect
from .models import Post
from .forms import BlogForm
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    posts = Post.objects.all()
    return render(request, "blog/home.html", {"posts": posts})


@login_required
def detail(request, pk):
    post = Post.objects.get(id=pk)
    return render(request, "blog/detail.html", {"post": post})


@login_required
def create_post(request):
    # Handle POST or GET requests with form data and file uploads
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)  # Pass both POST data and FILES
        if form.is_valid():
            # Set the author as the currently logged-in user
            form.instance.author = request.user
            # Save the form, which includes handling file uploads
            form.save()
            return redirect("blog:home")  # Redirect to the desired URL after saving
        else:
            print(form.errors)  # Debugging: print any validation errors to the console
    else:
        form = BlogForm()  # Instantiate an empty form for GET requests

    return render(request, "blog/post_form.html", {"form": form})


def update_post(request, pk):
    post = Post.objects.get(id=pk)
    form = BlogForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("blog:home")
    return render(request, "blog/post_form.html", {"form": form})


def delete_post(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect("blog:home")
