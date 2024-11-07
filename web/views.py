from django.shortcuts import redirect


# Create your views here.
def index(request):
    return redirect("account_login")
    # return render(request, "web/index.html")
