from django import forms
from .models import Venta
from django.core.validators import FileExtensionValidator

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields=['nomeProdutto','importo','unita','totPer']

class PdfMergeForm(forms.Form):
    file1 = forms.FileField(label="Upload PDF file 1")
    file2 = forms.FileField(label="Upload PDF files 2")

class PdfForm(forms.Form):
    pdf_extra = forms.FileField(label="Caricare Pdf",validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

class CalendarReport(forms.Form):
    calendario = forms.DateField(widget=forms.DateInput({'type':'date','min':'2023-01-01','max':'2026-12-31'}))