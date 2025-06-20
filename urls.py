from django.urls import path, include

urlpatterns = [
    # ...existing code...
    # path('web/', include('web.urls', namespace='web')),  # Only one should use 'web'
    # path('another/', include('another.urls', namespace='web')),  # <-- Change this to a unique namespace
    path('another/', include('another.urls', namespace='another')),  # Fixed
    # ...existing code...
]