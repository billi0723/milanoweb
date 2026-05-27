from django.urls import path, re_path
from . import views

# namespace
app_name = 'bottegaMilano'

urlpatterns = [
    # Upload pdf, pages need to extract user input, return to the page to be extracted
    #path('extract/', views.pdf_extract, name='pdf_extract'),
    path('merge/', views.pdf_merge, name='pdf_merge'),
]