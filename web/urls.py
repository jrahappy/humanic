from django.urls import path
from . import views

app_name = "web"
urlpatterns = [
    # path("", views.index, name="index"),
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("clinicContact/", views.clinicContact, name="clinicContact"),
    path(
        "clinicContact_success/",
        views.clinicContact_success,
        name="clinicContact_success",
    ),
    path("doctorContact/", views.doctorContact, name="doctorContact"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("email_policy/", views.email_policy, name="email_policy"),
    path("specialties/", views.specialties, name="specialties"),
    path("intro/", views.intro, name="intro"),
    path("faq/", views.faq, name="faq"),
    # Public news pages
    path("news/", views.news_list, name="news_list"),
    path("news/<int:pk>/", views.news_detail, name="news_detail"),
    # WebBlog CRUD URLs
    path("blog/", views.WebBlogListView.as_view(), name="webblog_list"),
    path("blog/<int:pk>/", views.WebBlogDetailView.as_view(), name="webblog_detail"),
    path("blog/create/", views.WebBlogCreateView.as_view(), name="webblog_create"),
    path(
        "blog/<int:pk>/update/",
        views.WebBlogUpdateView.as_view(),
        name="webblog_update",
    ),
    path(
        "blog/<int:pk>/delete/",
        views.WebBlogDeleteView.as_view(),
        name="webblog_delete",
    ),
    path("blog/<int:pk>/comment/", views.webblog_comment, name="webblog_comment"),
    # Job Application (separate from blog)
    path(
        "job-application/<int:job_id>/", views.job_application, name="job_application"
    ),
    path(
        "job-application-modal/<int:job_id>/",
        views.job_application_modal,
        name="job_application_modal",
    ),
    path("job-detail/<int:job_id>/", views.job_detail_htmx, name="job_detail_htmx"),
    # WebInquiry CRUD URLs
    path("inquiry/", views.WebInquiryListView.as_view(), name="webinquiry_list"),
    path(
        "inquiry/create/",
        views.WebInquiryCreateView.as_view(),
        name="webinquiry_create",
    ),
    path("inquiry/success/", views.webinquiry_success, name="webinquiry_success"),
    path(
        "inquiry/<int:pk>/",
        views.WebInquiryDetailView.as_view(),
        name="webinquiry_detail",
    ),
    path(
        "inquiry/<int:pk>/update/",
        views.WebInquiryUpdateView.as_view(),
        name="webinquiry_update",
    ),
    path(
        "inquiry/<int:pk>/delete/",
        views.WebInquiryDeleteView.as_view(),
        name="webinquiry_delete",
    ),
]
