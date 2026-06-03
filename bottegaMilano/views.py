from ctypes.util import test
from urllib import response
from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse
from google.cloud.storage import bucket

from bottegaMilano.forms import VentaForm
from .models import Venta
from .forms import PdfForm
import PyPDF2 # type: ignore
import traceback

from django.utils.safestring import mark_safe
import re

import os
import imaplib
import email
from email.header import decode_header
#from google.cloud import storage


# Create your views here
EMAIL_USUARIO = "reportmercato@gmail.com"
EMAIL_CONTRASENA = os.environ.get('EMAIL_CONTRASENA')
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def conectar_correo():
    #Se conecta al servidor IMAP y selecciona la bandeja de entrada.
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USUARIO, EMAIL_CONTRASENA)
        mail.select("inbox") # Conectarse a la bandeja de entrada
        return mail
    except Exception as e:
        print(f"Error al conectar al correo: {e}")
        traceback.print_exc()
    return None

def extraer_texto_pdf(ruta_pdf):
    #Lee un archivo PDF local y extrae su texto."""
    #print(f"\n--- Leyendo contenido de: {ruta_pdf} ---")
    try:
        reader = PyPDF2.PdfReader(ruta_pdf)
        texto_completo = ""
        for i, pagina in enumerate(reader.pages):
            #texto_completo += f"\n--- Página {i+1} ---\n"
            texto_completo += pagina.extract_text()
        return texto_completo
    except Exception as e:
        print(f"Error al leer el PDF: {e}")

def buscar_y_procesar_pdfs(request):
    #storage_client = storage.Client()
    #bucket_name = "storage_report_23"
    
    bottega_cartella = {
        "MCR - GIRARROSTO - MCR":"b_g_roma/",
        "MCB - GIRARROSTO - MCB":"b_g_bolzano/",
        "MCB - GRILL - MCB":"b_m_bolzano/",
        "MCF - BISTECCA FIORENTINA":"b_r_firenze/",
        "MCM - GIRARROSTO - MCM":"b_g_milano/",
        "MCM -  MACELLERIA - MCM":"b_m_milano/",
        "MCT - GIRARROSTO - MCT":"b_g_torino/",
        "MCT - HAMBURGER - MCT":"b_h_torino/",
        "ABG - MACELLERIA - ABG":"b_m_abg/",
        "MCT - MACELLERIA - MCT":"b_m_torino/",
        "MCF - GIRARROSTO - MCF":"b_g_firenze/",
        "MCR - MACELLERIA - MCR":"b_m_roma/",
        "MCF - MACELLERIA - MCF":"b_m_firenze/",
        "ALB_F&B - ALBATROS - POLLO":"c_g_albatros/",
        "ALB_F&B - ALBATROS - RISTO ALFREDO":"c_m_albatros/",
    }

    listaTitolosPdf=[]
    listaTitoloEmail=[]
    mail = conectar_correo()
    if not mail:
        return HttpResponse("no se conecto al email")
    status, mensajes = mail.uid('search',None,"FROM reporting@mercatocentrale.it",'SINCE 18-Oct-2025','BEFORE 02-Jun-2026')
    id_correos = mensajes[0].decode().split()

    if not id_correos:
        print("No se encontraron correos nuevos sin leer.")
        return HttpResponse("no hay correos")

    #print(f"Se encontraron {len(id_correos)} correos sin leer. Procesando el más reciente...")
    
    for correos in id_correos:
        asunto="vacio"
        msg="vacio"
         # Obtener el contenido del correo
        status, data = mail.uid('fetch',correos, '(RFC822)')
        if data and isinstance(data[0], tuple):
            # Parsear el contenido del correo
            msg = email.message_from_bytes(data[0][1])
            if msg["Subject"]:
                asunto, codificacion = decode_header(msg["Subject"])[0]
            ruta_cartella = 'b_defecto'
            for clave in bottega_cartella:
                if isinstance(asunto, bytes):
                    asunto = asunto.decode(codificacion or "utf-8")
                if clave in asunto:
                    ruta_cartella = bottega_cartella[clave]
                    break

        # Revisar las partes del correo para buscar archivos adjuntos
        file = []
        existepdf = False
        for parte in msg.walk():
            # Si el tipo de contenido no es un adjunto, lo saltamos
            if parte.get_content_maintype() == 'multipart':
                continue
            if parte.get('Content-Disposition') is None:
                continue
            nombre_archivo = parte.get_filename()

            if nombre_archivo:
            # Decodificar el nombre del archivo si tiene caracteres raros
                nombre_archivo_decodificado, cod = decode_header(nombre_archivo)[0]
            if isinstance(nombre_archivo_decodificado, bytes):
                nombre_archivo = nombre_archivo_decodificado.decode(cod or "utf-8")

            # Verificar si el archivo es un PDF
            if nombre_archivo.lower().endswith('.pdf'):
                file.append(nombre_archivo)
                existepdf = True
            if not existepdf:
                if nombre_archivo.lower().endswith(('.xls','xlsx')):
                    file.append(nombre_archivo)

            #bucket = storage_client.bucket(bucket_name)
            #blob = bucket.blob(ruta_cartella + '/' + file[0])
            #blob.upload_from_string(parte.get_payload(decode=True))


            # Descargar y guardar temporalmente el archivo PDF
            ruta_guardado = os.path.join(os.getcwd(), nombre_archivo)
            with open(ruta_guardado, 'wb') as f:
                f.write(parte.get_payload(decode=True))
                print(f"Archivo guardado en: {ruta_guardado}")

        # PASO EXTRA: Leer el PDF ya descargado
        extraer_texto_pdf(ruta_guardado)

    # Cerrar sesión de manera segura
    mail.close()
    mail.logout()
    return HttpResponse("pdf guardado")

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

def lista_reportes(request):
    #ruta_dir = os.path.join(os.getcwd())
    ruta_dir = "C:\Users\billi\Desktop\Python App\DjangoWeb\report"
    reportes = []
    if os.path.exists(ruta_dir):
        for archivo in os.listdir(ruta_dir):
            if archivo.endswith(('.pdf','.xls','.xlsx')):
                reportes.append(archivo)
    return render(request,reportes.html,{'reportes':reportes})

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

    totaleCotoleteria += totaleContorni/2
    totaleMacelleria += totaleContorni/2
    return render(request, 'testoExtra.html',{'testo':listaArti,'orari':listaImporario,'tm':totaleMacelleria,'tc':totaleCotoleteria,'c':totaleContorni,
                                              'dfz':diferenza,'ti':totaleIncassi,'tip':totaleIncassiPre})





            

