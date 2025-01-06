from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # new

# from django.views.static import serve  # new


urlpatterns = [
    # re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    # re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path("primrose/", admin.site.urls),
    path("", include("web.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("briefing/", include("briefing.urls")),
    path("customer/", include("customer.urls")),
    path("provider/", include("provider.urls")),
    path("product/", include("product.urls")),
    path("importdata/", include("importdata.urls")),
    path("minibooks/", include("minibooks.urls")),
    path("report/", include("report.urls")),
    path("dogfoot/", include("dogfoot.urls")),
    path("blog/", include("blog.urls")),
    path("cust/", include("cust.urls")),
    path("referdex/", include("referdex.urls")),
    path("crm/", include("crm.urls")),
    path("collab", include("collab.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
