from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import BlogForm
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    user = request.user
    posts = Post.objects.filter(author=user)
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
