from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse

# Create a simple direct view without using templates
def direct_home(request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Education System</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col-md-12">
                    <h1 class="display-4 text-center">Welcome to Education System</h1>
                    <p class="lead text-center mt-3">A comprehensive platform for online learning</p>
                    <div class="d-flex justify-content-center mt-4">
                        <a href="/education/login/" class="btn btn-primary mx-2">Login</a>
                        <a href="/education/register/" class="btn btn-success mx-2">Register</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Direct HTML response for home page
    path('', direct_home, name='home'),
    path('education/', include('education.urls', namespace='education')),
    path('new-education/', include('new_education.urls', namespace='new_education')),
]

# Add the static and media URL patterns for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 