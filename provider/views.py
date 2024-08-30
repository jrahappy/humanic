# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from importdata.models import temp_doctor_table


def index(request):

    doctors = temp_doctor_table.objects.all()
    context = {"doctors": doctors}
    return render(request, "provider/index.html", context)
