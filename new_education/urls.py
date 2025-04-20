from django.urls import path
from . import views

app_name = 'new_education'

urlpatterns = [
    path('', views.index, name='index'),
] 