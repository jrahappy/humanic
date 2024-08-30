from django.shortcuts import render
from .models import Product, Platform


# Create your views here.
def index(request):
    products = Product.objects.all()
    context = {"products": products, "title": "Product List"}
    return render(request, "product/index.html", context)


def platform(request):
    platforms = Platform.objects.all()
    context = {"platforms": platforms, "title": "Platform List"}
    return render(request, "product/platform.html", context)
