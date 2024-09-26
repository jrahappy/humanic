# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, "dashboard/daisyui.html")


def daisyui(request):
    return render(request, "dashboard/daisyui.html")
