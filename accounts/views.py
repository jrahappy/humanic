from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):

    user = request.user
    if user.is_authenticated:
        return redirect("dashboard:index")
