from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from customer.forms import (
    InquiryForm,
)
from .models import WebBlog, WebBlogComment, WebInquiry
from .forms import WebBlogForm, WebInquiryForm, PublicWebInquiryForm
from django.contrib.auth.decorators import login_required


# from django_recaptcha.fields import RecaptchaField


# Create your views here.
def index(request):
    return redirect("account_login")
    # return render(request, "web/index.html")


def home(request):
    # Get published news posts
    news_posts = WebBlog.objects.filter(
        status="Published",
        category="news"
    ).order_by("-created_at")[:6]  # Get latest 6 news posts
    
    context = {
        "news_posts": news_posts,
    }
    return render(request, "web/home.html", context)


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
        form = PublicWebInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("web:webinquiry_success")
        else:
            # Debug: print form errors
            print("Form errors:", form.errors)
            print("Form data:", request.POST)
            print("is_agreed value:", request.POST.get('is_agreed'))
            print("is_agreed in cleaned_data:", form.cleaned_data.get('is_agreed') if hasattr(form, 'cleaned_data') else 'No cleaned_data')
    else:
        # Initialize form without status field for public users
        form = PublicWebInquiryForm()

    context = {
        "form": form,
    }
    return render(request, "web/clinicContact.html", context)


def doctorContact(request):
    # Get published HR job postings
    job_postings = WebBlog.objects.filter(
        status="Published", 
        category="hr"
    ).order_by("-created_at")
    
    # Check for success message and clear it
    application_success = request.session.pop("job_application_success", False)
    applied_job_title = request.session.pop("applied_job_title", None)
    
    context = {
        "job_postings": job_postings,
        "application_success": application_success,
        "applied_job_title": applied_job_title,
    }
    return render(request, "web/doctorContact.html", context)


def webblog_comment(request, pk):
    blog = get_object_or_404(WebBlog, pk=pk)
    if request.method == "POST":
        comment = WebBlogComment(
            blog=blog,
            applicant=request.POST.get("applicant"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            is_agreed=request.POST.get("is_agreed") == "on",
            attached_file=request.FILES.get("attached_file"),
        )
        comment.save()
        
        # Check if the request came from doctorContact page
        if "doctorContact" in request.META.get("HTTP_REFERER", ""):
            # Add success message to session
            request.session["application_success"] = True
            return redirect("web:doctorContact")
    
    return redirect("web:webblog_detail", pk=pk)


def job_application(request, job_id):
    """Handle job applications from the public doctorContact page"""
    job = get_object_or_404(WebBlog, pk=job_id, status="Published", category="hr")
    
    if request.method == "POST":
        try:
            # Create the application (using WebBlogComment model)
            application = WebBlogComment(
                blog=job,
                applicant=request.POST.get("applicant"),
                phone=request.POST.get("phone"),
                email=request.POST.get("email"),
                is_agreed=request.POST.get("is_agreed") == "on",
                attached_file=request.FILES.get("attached_file"),
            )
            application.save()
            
            # Check if it's an HTMX request
            if request.headers.get('HX-Request'):
                # Return success modal content
                return render(request, "web/partials/job_application_success.html", {
                    "job_title": job.title
                })
            
            # Regular form submission
            request.session["job_application_success"] = True
            request.session["applied_job_title"] = job.title
            return redirect(f"{reverse('web:doctorContact')}#job-{job_id}")
            
        except Exception as e:
            if request.headers.get('HX-Request'):
                return render(request, "web/partials/job_application_error.html", {
                    "error": str(e)
                })
            return redirect("web:doctorContact")
    
    # If not POST, redirect to doctorContact
    return redirect("web:doctorContact")


def job_application_modal(request, job_id):
    """Return the job application modal content for HTMX"""
    job = get_object_or_404(WebBlog, pk=job_id, status="Published", category="hr")
    
    return render(request, "web/partials/job_application_modal.html", {
        "job": job
    })


def job_detail_htmx(request, job_id):
    """Return the job detail content for HTMX"""
    job = get_object_or_404(WebBlog, pk=job_id, status="Published", category="hr")
    
    return render(request, "web/partials/job_detail.html", {
        "job": job
    })


# WebBlog CRUD Views
class WebBlogListView(LoginRequiredMixin, ListView):
    model = WebBlog
    template_name = "web/webblog_list.html"
    context_object_name = "blogs"
    paginate_by = 10

    def get_queryset(self):
        # Show all blogs for authenticated users, only published for anonymous
        if self.request.user.is_authenticated:
            queryset = WebBlog.objects.all().order_by("-created_at")
        else:
            queryset = WebBlog.objects.filter(status="Published").order_by("-created_at")
        
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class WebBlogDetailView(LoginRequiredMixin, DetailView):
    model = WebBlog
    template_name = "web/webblog_detail.html"
    context_object_name = "blog"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.all().order_by("-created_at")
        return context


class WebBlogCreateView(LoginRequiredMixin, CreateView):
    model = WebBlog
    form_class = WebBlogForm
    template_name = "web/webblog_form.html"
    success_url = reverse_lazy("web:webblog_list")
    login_url = "/accounts/login/"

    def form_valid(self, form):
        try:
            form.instance.author = self.request.user
            print(f"Form is valid. Author: {self.request.user}")
            print(f"Form data: {form.cleaned_data}")
            response = super().form_valid(form)
            print(f"Object saved with ID: {self.object.pk}")
            print(f"Redirecting to: {self.get_success_url()}")
            return response
        except Exception as e:
            print(f"Error saving form: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def form_invalid(self, form):
        print("Form is invalid!")
        print("Form errors:", form.errors)
        print("Form data:", form.data)
        return super().form_invalid(form)
    
    def post(self, request, *args, **kwargs):
        print("POST request received")
        print("POST data:", request.POST)
        print("FILES:", request.FILES)
        return super().post(request, *args, **kwargs)


class WebBlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = WebBlog
    form_class = WebBlogForm
    template_name = "web/webblog_form.html"
    success_url = reverse_lazy("web:webblog_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        print("Update POST data:", self.request.POST)
        print("Update FILES:", self.request.FILES)
        return super().form_valid(form)


class WebBlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = WebBlog
    template_name = "web/webblog_confirm_delete.html"
    success_url = reverse_lazy("web:webblog_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_staff


# WebInquiry CRUD Views
class WebInquiryListView(LoginRequiredMixin, ListView):
    model = WebInquiry
    template_name = "web/webinquiry_list.html"
    context_object_name = "inquiries"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = WebInquiry.objects.all().order_by("-created_at")
        
        # Filter by status if provided
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(business_name__icontains=search) |
                models.Q(name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(message__icontains=search)
            )
        
        return queryset


class WebInquiryDetailView(LoginRequiredMixin, DetailView):
    model = WebInquiry
    template_name = "web/webinquiry_detail.html"
    context_object_name = "inquiry"


class WebInquiryCreateView(CreateView):
    model = WebInquiry
    form_class = WebInquiryForm
    template_name = "web/webinquiry_form.html"
    success_url = reverse_lazy("web:webinquiry_success")
    
    def form_valid(self, form):
        # Don't require login for creating inquiries (public form)
        return super().form_valid(form)


class WebInquiryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = WebInquiry
    form_class = WebInquiryForm
    template_name = "web/webinquiry_form.html"
    success_url = reverse_lazy("web:webinquiry_list")
    
    def test_func(self):
        # Only staff can update inquiries
        return self.request.user.is_staff


class WebInquiryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = WebInquiry
    template_name = "web/webinquiry_confirm_delete.html"
    success_url = reverse_lazy("web:webinquiry_list")
    
    def test_func(self):
        # Only staff can delete inquiries
        return self.request.user.is_staff


def webinquiry_success(request):
    """Success page after inquiry submission"""
    return render(request, "web/webinquiry_success.html")


@login_required
def webinquiry_update_status(request, pk):
    """Update only the status of an inquiry"""
    if not request.user.is_staff:
        return redirect('web:webinquiry_list')
    
    inquiry = get_object_or_404(WebInquiry, pk=pk)
    
    if request.method == "POST":
        status = request.POST.get('status')
        if status in ['Inquiry', 'In Progress', 'Closed']:
            inquiry.status = status
            inquiry.save()
    
    return redirect('web:webinquiry_detail', pk=pk)


@login_required
def webblogcomment_update_status(request, blog_pk, comment_pk):
    """Update only the status of a blog comment"""
    if not request.user.is_staff:
        return redirect('web:webblog_detail', pk=blog_pk)
    
    comment = get_object_or_404(WebBlogComment, pk=comment_pk, blog__pk=blog_pk)
    
    if request.method == "POST":
        status = request.POST.get('status')
        if status in ['Pending', 'Approved', 'Rejected']:
            comment.status = status
            comment.save()
    
    return redirect('web:webblog_detail', pk=blog_pk)


def news_detail(request, pk):
    """Public news detail view for visitors"""
    news = get_object_or_404(WebBlog, pk=pk, status="Published", category="news")
    
    # Get related news posts
    related_news = WebBlog.objects.filter(
        status="Published",
        category="news"
    ).exclude(pk=pk).order_by("-created_at")[:3]
    
    context = {
        "news": news,
        "related_news": related_news,
    }
    return render(request, "web/news_detail.html", context)


def news_list(request):
    """Public news list view for visitors"""
    news_posts = WebBlog.objects.filter(
        status="Published",
        category="news"
    ).order_by("-created_at")
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(news_posts, 9)  # Show 9 news per page (3x3 grid)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "news_posts": page_obj,
    }
    return render(request, "web/news_list.html", context)
