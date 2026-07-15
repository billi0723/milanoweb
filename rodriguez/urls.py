"""
URL configuration for rodriguez project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from bottegaMilano.views import *


# For static files such as images, CSS, and text is very important
from django.conf import settings
from django.conf.urls.static import static

app_name = 'bottegaMilano'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ventas/', formVenta, name='formulario'),
    path('', report_macelleria_Milano, name='report_macelleria_Milano'),
    path('reportData/', reportData, name='reportData'),
    path('listaBDBottegue/', listaBDBottegue, name='listaBDBottegue'),
    path('eliminaData/', eliminaData, name='eliminaData'),
    path('buscar_y_procesar_pdfs/', buscar_y_procesar_pdfs, name='buscar_y_procesar_pdfs'),
    path('lista_reportes/', lista_reportes, name='lista_reportes'),
    path('addPdfDatabase/', addPdfDatabase, name='addPdfDatabase'),
    path('listaBDBottegue/', listaBDBottegue, name='listaBDBottegue'),
    #path('bottegaMilano/', include('bottegaMilano.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
