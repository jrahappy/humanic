from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "briefing/index.html")


# Compare this snippet from provider/views.py:
