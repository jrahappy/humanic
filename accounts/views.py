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


# class CustomPasswordChangeView(PasswordChangeView):
#     template_name = "accounts/password_change.html"
#     form_class = CustomPasswordChangeForm
#     success_url = "/"
#     view_name = "change-password"
#     success_url = "/"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["html_left_menu"] = get_menu(1, 0, 0)  # Add this line
#         return context

#     def form_valid(self, form):
#         messages.success(self.request, "Your password was successfully updated!")
#         form.save(self.request)
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, "There was an error in your password update.")
#         return self.render_to_response(self.get_context_data(form=form))
