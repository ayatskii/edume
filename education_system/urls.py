from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from education.views import home  # Import our template-based home view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Use our template-based home view
    path('education/', include('education.urls', namespace='education')),
    path('new-education/', include('new_education.urls', namespace='new_education')),
]

# Add the static and media URL patterns for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 