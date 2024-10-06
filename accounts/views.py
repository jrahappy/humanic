from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from allauth.account.views import PasswordChangeView
from allauth.account.forms import ChangePasswordForm
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ProfileForm,
    CustomPasswordChangeForm,
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


def user_update(request):
    user = request.user

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect("accounts:profile")
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, "accounts/user_update.html", {"form": form})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = CustomPasswordChangeForm
    success_url = "/"
    view_name = "change-password"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["html_left_menu"] = get_menu(1, 0, 0)  # Add this line
        return context

    def form_valid(self, form):
        messages.success(self.request, "Your password was successfully updated!")
        form.save(self.request)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in your password update.")
        return self.render_to_response(self.get_context_data(form=form))
