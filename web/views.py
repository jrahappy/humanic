from django.shortcuts import redirect, render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return redirect("account_login")
    # return render(request, "web/index.html")


def home(request):
    return render(request, "web/home.html")


def clinicContact(request):
    return render(request, "web/clinicContact.html")


def doctorContact(request):
    return render(request, "web/doctorContact.html")
