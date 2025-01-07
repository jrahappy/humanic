from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from allauth.account.forms import ChangePasswordForm
from .forms import (
    ProfileForm,
    CustomSignupForm,
    # CustomPasswordChangeForm,
)


@login_required
def profile(request):
    user = request.user

    form = ProfileForm(instance=user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=user.profile)

    return render(request, "accounts/profile.html", {"form": form})


def profile_update_partial(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid():
            form.save()
            real_name = form.cleaned_data.get("real_name")
            email = form.cleaned_data.get("email")
            user.first_name = real_name
            user.last_name = real_name
            user.email = email
            user.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
        else:
            print(form.errors)
    else:
        form = ProfileForm(instance=user.profile)

    return render(
        request, "accounts/profile_update_partial.html", {"form": form, "user": user}
    )


def signup(request):
    if request.method == "POST":
        # form = SignupForm(request.POST)
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created.")
            return redirect("account_login")
    else:
        # form = SignupForm()
        form = CustomSignupForm()

    return render(request, "accounts/signup.html", {"form": form})


def user_update(request):
    user = request.user

    if request.method == "POST":
        form = ChangePasswordForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect("accounts:profile")
    else:
        form = ChangePasswordForm(instance=user)

    return render(request, "accounts/user_update.html", {"form": form})


@login_required
def password_change(request):
    if request.method == "POST":
        form = ChangePasswordForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully updated!")
            update_session_auth_hash(request, form.user)
            return HttpResponse(
                '<script>window.location.href="%s";</script>'
                % reverse_lazy("accounts:password_change_done")
            )  # Redirect to success URL using JavaScript if the form is valid

        else:
            messages.error(request, "There was an error in your password update.")
            return render(request, "accounts/password_change.html", {"form": form})
    else:
        form = ChangePasswordForm(user=request.user)

    context = {
        "form": form,
    }
    return render(request, "accounts/password_change.html", context)


def password_change_done(request):
    return render(request, "accounts/password_change_done.html")
