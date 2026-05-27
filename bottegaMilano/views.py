from ctypes.util import test
from urllib import response
from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse

from bottegaMilano.forms import VentaForm
from .models import Venta
from .forms import PdfForm
import PyPDF2 # type: ignore

from django.utils.safestring import mark_safe
import re


# Create your views here

def listaVenta(request):
    lst=Venta.objects.all().values("nomeProdutto","importo","unita","totPer")
    response = ""
    for i in lst:
        response+=f"{i}<br>"
    return HttpResponse(response)

def formVenta(request):
    if request.method == 'POST':
        formV = VentaForm(request.POST)
        if formV.is_valid():
            formV.save()
            return redirect('http://127.0.0.1:8000/')
    else:
        formV = VentaForm()
        return render(request,'venta.html',{'formulario':formV})

def caricarePdf(request):
    testo=""
    if request.method == 'POST':
        form = PdfForm(request.POST, request.FILES)
        if form.is_valid():
             f = request.FILES['pdf_extra']
             pdfFileObj = PyPDF2.PdfReader(f)
             for page in pdfFileObj.pages:
                testo += page.extract_text()+"\n"
    else:
        form = PdfForm()
        return render(request, 'pdfTesto.html', {'form': form})

    request.session['testo'] = testo
    return render(request, 'pdfTesto.html', {'testo': testo})

cotoletteArticoli = ["Base + patatine","Manzo sportiva","La mortazza","Manzo base + patate","La sportiva",
            "Cotoletta base","Cotoletta Pros Crudo E Fichi - Vitello","Cotoletta Pros Crudo E Fichi - Suino",
            "Con osso manzo","Manzo porcellina","Manzo mortazza","La porcellina","La raffinata","Manzo base","Manzo base + patate"]
contorni = ["Patate Al Forno","Verdure","Riso"]

def save_DataPDF(request):
    listaTesto = []
    listaOrari = []
    listaTotale = []
    totaleIncassi = ""
    totaleIncassiPre = ""
    diferenza = ""
    incasso = True
    datosArti = False
    datosOrari = False
    testo = request.session.get('testo','')
    fila = testo.splitlines()
    dataDoc = fila[0].split()[0]
    for orari in testo.splitlines():
        if re.search(r"FASCIA ORARIA INCASSI BOTTEGA?",orari,re.IGNORECASE):
            datosOrari = True
            continue
        if re.search(r"TOTALE INCASSI\s(.*)",orari,re.IGNORECASE):
            if incasso:
                totaleIncassi = orari
                incasso = False
            else:
                totaleIncassiPre = orari
            datosOrari = False
        if re.search(r"DIFFERENZA\s*(.*)",orari,re.IGNORECASE):
            diferenza = orari
            datosOrari = False
        if datosOrari:
            listaOrari.append(orari)

    totaleIncassi
    patronOrari = r"(?P<orari>\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})\s*(?P<importeOra>[\d.,]+)"
    listaImporario = []
    for incassi in listaOrari:
        o = re.search(patronOrari,incassi)
        if o:
            ora = o.groupdict()
            ora['data']=dataDoc
            listaImporario.append(ora)
    
    for linea in testo.splitlines():
        if re.search(r"ANALISI ARTICOLI?",linea,re.IGNORECASE):
            datosArti = True
            continue
        if re.search(r"^TOTALE\s+\d",linea,re.IGNORECASE):
            listaTesto.append(linea)
            datosArti = False
            break
        if re.search(r"ARTICOLI PER FASCIA DI SERVIZIO?",linea,re.IGNORECASE):
            datosArti = False
            break
        if datosArti:
            listaTesto.append(linea)
    
    patron = r"^(?P<nome>.+?)\s+(?P<importo>\d+,\d+)\s+(?P<unita>\d+(?:,\d+)?)\s+(?P<perTotal>\d+,\d+%)\s*,?$"
    listaArti = []
    totaleMacelleria=0;
    totaleCotoleteria=0;
    totaleContorni=0;
    for lista in listaTesto:
        t = re.search(patron,lista)
        if t:
            articolo = t.groupdict()
            articolo['importo']=float(articolo['importo'].replace(',','.'))
            articolo['unita']=float(articolo['unita'].replace(',','.'))
            articolo['data']=dataDoc
            listaArti.append(articolo)
    for i in listaArti:
        if i['nome'] in contorni:
            totaleContorni += i['importo']
            continue
        if i['nome'] in cotoletteArticoli:
            totaleCotoleteria += i['importo']
            continue
        else:
            totaleMacelleria += i['importo']
            continue

    return render(request, 'testoExtra.html',{'testo':listaArti,'orari':listaImporario,'tm':totaleMacelleria,'tc':totaleCotoleteria,'c':totaleContorni,
                                              'dfz':diferenza,'ti':totaleIncassi,'tip':totaleIncassiPre})





            

