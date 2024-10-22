from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, F, Func, Avg
from accounts.models import Profile, CustomUser
from .models import Post, PostAttachment
from .forms import BlogForm, PostForm


def index(request):
    posts = (
        Post.objects.select_related("author")
        .prefetch_related("postattachment_set")
        .order_by("-created_at")
    )
    context = {"posts": posts}
    return render(request, "blog/index.html", context)


def create_post_admin(request):

    if request.method == "POST":
        data = request.POST

        post = Post.objects.create(
            author=CustomUser.objects.get(id=data.get("author")),
            is_public=data.get("is_public"),
            # category=data.get("category"),
            title=data.get("title"),
            content=data.get("content"),
        )

        files = request.FILES.getlist("files")
        print(files)

        for file in files:
            print(file)
            PostAttachment.objects.create(post=post, file=file)

        return redirect("blog:index")

    else:
        ko_kr = Func(
            "real_name",
            function="ko_KR.utf8",
            template='(%(expressions)s) COLLATE "%(function)s"',
        )
        authors = Profile.objects.all().order_by(ko_kr.asc())
        post_form = PostForm()

        return render(
            request,
            "blog/post_form_admin.html",
            {
                "authors": authors,
                "user": request.user,
            },
        )


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
            form.instance.author = request.user
            form.save()
            return redirect("blog:home")  # Redirect to the desired URL after saving
        else:
            print(form.errors)  # Debugging: print any validation errors to the console
    else:
        form = BlogForm()  # Instantiate an empty form for GET requests
        print(form)
    return render(request, "blog/post_form.html", {"form": form})


@login_required
def update_post(request, pk):
    # Safely get the post or return 404 if not found
    post = get_object_or_404(Post, id=pk)

    if request.method == "POST":
        # Bind the form to the existing post
        form = BlogForm(request.POST, request.FILES, instance=post)

        # Check if the user cleared the file
        file_clear = request.POST.get("file-clear", False)

        if file_clear:
            post.file = None  # Clear the file
            post.save()

        # Check if the form is valid
        if form.is_valid():
            form.save()  # Update the post
            return redirect("blog:home")  # Redirect to home after successful update
        else:
            # Handle invalid form and re-render the form with errors
            return render(
                request, "blog/update_post_form.html", {"form": form, "post": post}
            )
    else:
        # Display the form pre-filled with the current post data
        form = BlogForm(instance=post)

    return render(request, "blog/update_post_form.html", {"form": form, "post": post})


def delete_post(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect("blog:home")
