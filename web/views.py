from django.shortcuts import redirect, render
from django.http import HttpResponse
from customer.forms import (
    InquiryForm,
)
from web.models import WebInquiry, WebBlog

# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
# from django_recaptcha.fields import RecaptchaField


# Create your views here.
def index(request):
    return redirect("account_login")
    # return render(request, "web/index.html")


def home(request):
    return render(request, "web/home.html")


def clinicContact_success(request):
    return render(request, "web/clinicContact_success.html")


def terms(request):
    return render(request, "web/terms.html")


def privacy(request):
    return render(request, "web/privacy.html")


def email_policy(request):
    return render(request, "web/email_policy.html")


def specialties(request):
    return render(request, "web/specialties.html")


def intro(request):
    return render(request, "web/intro.html")


def faq(request):
    return render(request, "web/faq.html")


def clinicContact(request):
    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.is_clinic = True
            company.is_collab = False
            company.is_tele = False
            company.save()
            return redirect("web:clinicContact_success")
        else:
            return render(request, "web/clinicContact.html", {"form": form})
    else:
        form = InquiryForm()

    context = {
        "form": form,
    }
    return render(request, "web/clinicContact.html", context)


def doctorContact(request):
    return render(request, "web/doctorContact.html")
