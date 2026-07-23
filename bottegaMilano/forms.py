from mimetypes import init
from django import forms
from .models import Venta
from django.core.validators import FileExtensionValidator
import datetime

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
    def __ini__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        hoy = datetime.date.today()
        fecha = hoy.strftime('%Y-%m-%d')
        self.fields['calendario'].widget.attrs['max'] = fecha
            
    calendario = forms.DateField(widget=forms.DateInput({'type':'date','min':'2023-02-28'}))