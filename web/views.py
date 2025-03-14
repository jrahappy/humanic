from django.shortcuts import redirect, render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return redirect("account_login")
    # return render(request, "web/index.html")


def home(request):
    return render(request, "web/home.html")


def customer(request):
    return render(request, "web/customer.html")


def provider(request):
    return render(request, "web/provider.html")
