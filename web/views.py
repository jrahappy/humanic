from django.shortcuts import render, redirect


# Create your views here.
def index(request):
    return redirect("account_login")
    # return render(request, "web/index.html")
