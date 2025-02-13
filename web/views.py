from django.shortcuts import redirect, render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return redirect("account_login")
    # return render(request, "web/index.html")


def home(request):
    return render(request, "web/home.html")


def terms(request):
    return render(request, "web/terms.html")
