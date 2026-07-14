from encodings import utf_8
import os
import tempfile
import json

"""json_content = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if(json_content):
    with tempfile.NamedTemporaryFile(mode="w",delete=False,suffix=".json") as temp_file:
        temp_file.write(json_content)
        temp_file_path = temp_file.name

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path"""


from ctypes.util import test
import datetime
import io
from http import client
from string import printable
from typing import Self
from urllib import response
from xml.etree.ElementInclude import include
from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse
#from google.cloud.storage import bucket

#rfrom bottegaMilano.forms import VentaForm 
from .models import Venta
from .forms import PdfForm,CalendarReport, VentaForm
import PyPDF2 # type: ignore
import traceback
#from google.cloud import storage
#import calendar
from django.utils.safestring import mark_safe
import re


import imaplib
import email
from email.header import decode_header
from google.cloud import bigquery

local_path = r"C:\Users\billi\Desktop\llave\project-d83b9b63-299f-44e9-be1-b432cb598692.json"

if os.path.exists(local_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=local_path
else:
    json_content = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if(json_content):
        with tempfile.NamedTemporaryFile(mode="w",delete=False,suffix=".json") as temp_file:
            temp_file.write(json_content)
            temp_file_path = temp_file.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path


EMAIL_USUARIO = "reportmercato@gmail.com"
EMAIL_CONTRASENA = os.environ.get('EMAIL_CONTRASENA')
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
PROJECTO = "project-d83b9b63-299f-44e9-be1"
DB = "bdBottegue"
TABELA = "venditaGiorno"

def conectar_correo():
    #Se conecta al servidor IMAP y selecciona la bandeja de entrada.
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USUARIO, EMAIL_CONTRASENA)
        mail.select("inbox") # Conectarse a la bandeja de entrada
        return mail
    except Exception as e:
        print(f"Errore di conessione al email: {e}")
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
    listaBottega = {}
    file = []
    listaBottega['mm']= {}
    #bottega_cartella = {
    #    "MCR - GIRARROSTO - MCR":"b_g_roma/",
    #    "MCB - GIRARROSTO - MCB":"b_g_bolzano/",
    #    "MCB - GRILL - MCB":"b_m_bolzano/",
    #    "MCF - BISTECCA FIORENTINA":"b_r_firenze/",
    #    "MCM - GIRARROSTO - MCM":"b_g_milano/",
    #    "MCM - MACELLERIA - MCM":"b_m_milano/",
    #    "MCT - GIRARROSTO - MCT":"b_g_torino/",
    #    "MCT - HAMBURGER - MCT":"b_h_torino/",
    #    "ABG - MACELLERIA - ABG":"b_m_abg/",
    #    "MCT - MACELLERIA - MCT":"b_m_torino/",
    #    "MCF - GIRARROSTO - MCF":"b_g_firenze/",
    #    "MCR - MACELLERIA - MCR":"b_m_roma/",
    #    "MCF - MACELLERIA - MCF":"b_m_firenze/",
    #    "ALB_F&B - ALBATROS - POLLO":"c_g_albatros/",
    #    "ALB_F&B - ALBATROS - RISTO ALFREDO":"c_m_albatros/",
    #}

    listaTitolosPdf=[]
    listaTitoloEmail=[]
    mail = conectar_correo()
    if not mail:
        return HttpResponse("no se conecto al email")

    hoy = datetime.date.today()
    fecha = hoy.strftime('%d-%b-%Y')
    #status, mensajes = mail.uid('search',None,'FROM','reporting@mercatocentrale.it','SINCE','30-May-2026','BEFORE','31-May-2026' )
    status, mensajes = mail.uid('search',None,'FROM','reporting@mercatocentrale.it','ON',fecha)
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
            #ruta_cartella = 'b_defecto'
            #for clave in bottega_cartella:
            #    if isinstance(asunto, bytes):
            #        asunto = asunto.decode(codificacion or "utf-8")
            #    if clave in asunto:
            #        ruta_cartella = bottega_cartella[clave]
            #        break

        # Revisar las partes del correo para buscar archivos adjuntos
        
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
                contenido = parte.get_payload(decode=True)
                file_memoria = io.BytesIO(contenido)
                file.append(nombre_archivo)

                if "90516" in nombre_archivo:
                                bottega = "Macelleria Milano"
                                pdfFileObj = PyPDF2.PdfReader(file_memoria)
                                testo_completo = ""
                                for page in pdfFileObj.pages:
                                    testo_completo += page.extract_text()
                                pdftemp = datosPDF(testo_completo,fecha,bottega)
                                if pdftemp:
                                    listaBottega['mm']=pdftemp

                existepdf = True
            if not existepdf:
                if nombre_archivo.lower().endswith(('.xls','xlsx')):
                    file.append(nombre_archivo)

            #bucket = storage_client.bucket(bucket_name)
            #blob = bucket.blob(ruta_cartella + '/' + file[0])
            #blob.upload_from_string(parte.get_payload(decode=True))


            # Descargar y guardar temporalmente el archivo PDF
            #ruta_guardado = os.path.join(os.getcwd(), nombre_archivo)
            #with open(ruta_guardado, 'wb') as f:
            #    f.write(parte.get_payload(decode=True))
            #    print(f"Archivo guardado en: {ruta_guardado}")

        # PASO EXTRA: Leer el PDF ya descargado
        #extraer_texto_pdf(ruta_guardado)

    # Cerrar sesión de manera segura
    mail.close()
    mail.logout()
    return render(request,'correos.html',{'correos':listaBottega})
    #return HttpResponse("pdf guardado")

def lista_reportes(request):
    #ruta_dir = os.path.join(os.getcwd())
    ruta_dir = "C:/Users/billi/Desktop/Python App/DjangoWeb/report"
    reportes = []
    if os.path.exists(ruta_dir):
        for archivo in os.listdir(ruta_dir):
            if archivo.endswith(('.pdf','.xls','.xlsx')):
                reportes.append(archivo)
    return render(request,'reportes.html',{'reportes':reportes})

def reportData(request):
    respuesta = ""
    fecha = ""
    listaBottega = {}
    if request.method == 'POST':
        formCalendar = CalendarReport(request.POST)
        if formCalendar.is_valid():
             fecha = request.POST.get('calendario')
             fp = fecha
             fecha = fecha.replace('/','-')
             partes = fecha.split('-')
             fecha = f"{partes[2]}-{partes[1]}-{partes[0]}"
             ruta_dir = "C:/Users/billi/Desktop/Python App/DjangoWeb/report"
             reportes = []
             listaBottega['mb']= {}
             listaBottega['gb']= {}
             listaBottega['rf']= {}
             listaBottega['mm']= {}
             listaBottega['gm']= {}
             listaBottega['gt']= {}
             listaBottega['ht']= {}
             listaBottega['mabg']= {}
             listaBottega['mt']= {}
             listaBottega['gf']= {}
             listaBottega['mr']= {}
             listaBottega['gr']= {}
             listaBottega['mf']= {}
             listaBottega['ga']= {}
             listaBottega['ma']= {}
            
             if os.path.exists(ruta_dir):
                 for archivo in os.listdir(ruta_dir):
                     if archivo.endswith(('.pdf')):
                         if fecha in archivo:

                            if "90606" in archivo:
                                bottega = "Macelleria Bolzano"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo = ""
                                for page in pdfFileObj.pages:
                                    testo_completo += page.extract_text()
                                pdftemp = datosPDF(testo_completo,fecha,bottega)
                                if pdftemp:
                                    listaBottega['mb'] = pdftemp
                            elif "90619" in archivo:
                                bottega = "Girarrosto Bolzano"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo1 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo1 += page.extract_text()
                                pdftemp = datosPDF(testo_completo1,fecha, bottega)
                                if pdftemp:
                                    listaBottega['gb'] = pdftemp
                            elif "90132" in archivo:
                                bottega = "Ristorante Firenze"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo2 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo2 += page.extract_text()
                                pdftemp = datosPDF(testo_completo2,fecha,bottega)
                                if pdftemp:
                                    listaBottega['rf']=pdftemp
                            elif "90516" in archivo:
                                bottega = "Macelleria Milano"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo3 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo3 += page.extract_text()
                                pdftemp = datosPDF(testo_completo3,fecha,bottega)
                                if pdftemp:
                                     listaBottega['mm']=pdftemp
                            elif "90518" in archivo:
                                bottega = "Girarrosto Milano"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo4 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo4 += page.extract_text()
                                pdftemp = datosPDF(testo_completo4,fecha,bottega)
                                if pdftemp:
                                     listaBottega['gm']=pdftemp
                            elif "90410" in archivo:
                                bottega = "Girarrosto Torino"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo5 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo5 += page.extract_text()
                                pdftemp = datosPDF(testo_completo5,fecha,bottega)
                                if pdftemp:
                                     listaBottega['gt']=pdftemp
                            elif "90422" in archivo:
                                bottega = "Hamburguer Torino"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo6 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo6 += page.extract_text()
                                pdftemp = datosPDF(testo_completo6,fecha,bottega)
                                if pdftemp:
                                     listaBottega['ht']=pdftemp
                            elif "90313" in archivo:
                                bottega = "Gilly"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo7 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo7 += page.extract_text()
                                pdftemp = datosPDF(testo_completo7,fecha,bottega)
                                if pdftemp:
                                     listaBottega['mabg']=pdftemp
                            elif "90411" in archivo:
                                bottega = "Macelleria Torino"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo8 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo8 += page.extract_text()
                                pdftemp = datosPDF(testo_completo8,fecha,bottega)
                                if pdftemp:
                                     listaBottega['mt']=pdftemp
                            elif "90119" in archivo:
                                bottega = "Girarrosto Firenze"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo9 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo9 += page.extract_text()
                                pdftemp = datosPDF(testo_completo9,fecha,bottega)
                                if pdftemp:
                                     listaBottega['gf'] =pdftemp
                            elif "90204" in archivo:
                                bottega = "Macelleria Roma"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo10 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo10 += page.extract_text()
                                pdftemp = datosPDF(testo_completo10,fecha,bottega)
                                if pdftemp:
                                     listaBottega["mr"] = pdftemp
                            elif "90211" in archivo:
                                bottega = "Girarrosto Roma"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo11 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo11 += page.extract_text()
                                pdftemp = datosPDF(testo_completo11,fecha,bottega)
                                if pdftemp:
                                     listaBottega['gr']=pdftemp
                            elif "90101" in archivo:
                                bottega = "Macelleria Firenze"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo12 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo12 += page.extract_text()
                                pdftemp = datosPDF(testo_completo12,fecha,bottega)
                                if pdftemp:
                                     listaBottega['mf']=pdftemp
                            elif "1118" in archivo:
                                bottega = "Girarrosto Albatroz"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo13 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo13 += page.extract_text()
                                pdftemp = datosPDF(testo_completo13,fecha,bottega)
                                if pdftemp:
                                     listaBottega['ga']=pdftemp
                            elif "1131" in archivo:
                                bottega = "Macelleria Albatroz"
                                pdfFileObj = PyPDF2.PdfReader(os.path.join(ruta_dir,archivo))
                                testo_completo14 = ""
                                for page in pdfFileObj.pages:
                                    testo_completo14 += page.extract_text()
                                pdftemp = datosPDF(testo_completo14,fecha,bottega)
                                if pdftemp:
                                     listaBottega['ma']=pdftemp
    else:
        formCalendar = CalendarReport()
        return render(request, 'reportes.html', {'formCalendar': formCalendar})

    #patron = r"(\d{2}/\d{2}/\d{4})\s+(?:MACELLERIA|GIRARROSTO|GRILL|BISTECCA FIORENTINA)"
    #partes = re.split(patron,respuesta)
    #partes_limpias = [p.strip() for p in partes if p.strip()]
    #print(listaBottega)
    return render(request, 'reportes.html', {'respuesta': listaBottega,'fecha':fecha,'formCalendar':formCalendar})

def datosPDF(texto,fecha,bottega):
    dataDoc = fecha
    
    listaIncasi = {}
    totaleIncassi = ""
    totaleIncassiPre = ""
    diferenza = ""
    ingresi = ""
    incasso = True
    
    #testo = request.session.get('testo','')
    #fila = texto.splitlines()
    #dataDoc = fila[0].split()[0]
    
    for t in texto.splitlines():
            if re.search(r"TOTALE INCASSI",t,re.IGNORECASE):
                if incasso:
                    ti = t.split('TOTALE INCASSI')[1].strip()
                    totaleIncassi = ti.split(" ")[1]
                    listaIncasi['inc']=totaleIncassi
                    incasso = False
                else:
                    tip = t.split('TOTALE INCASSI')[1].strip()
                    totaleIncassiPre = tip.split(" ")[1]
                    listaIncasi['pre']=totaleIncassiPre
            elif re.search(r"DIFFERENZA",t,re.IGNORECASE):
                d = t.split("DIFFERENZA % PERIODO PRECEDENTE")[1].strip()
                diferenza = d.split("ANALISI ARTICOLI")[0]
                listaIncasi['dif']=diferenza
            elif re.search(r"INGRESSI",t,re.IGNORECASE):
                i = t.split('INGRESSI')[1].strip()
                longi = len(i.split(" ")[1])
                cadena = i.split(" ")[0]
                ingresi = cadena[longi:len(cadena)]
                listaIncasi['ing']=ingresi

    client = bigquery.Client()
    table_id = 'project-d83b9b63-299f-44e9-be1.bdBottegue.venditaGiorno'
    row_to_insert = [{'incasso':totaleIncassi,
                      'incassoPre':totaleIncassiPre,
                      'diferenza':diferenza,
                      'ingressi':ingresi,
                      'data':dataDoc,
                      'bottega':bottega}]
    errors = client.insert_rows_json(table_id,row_to_insert)
    return listaIncasi

# -------------GET DE DATOS DE LA BD-----------------
def listaBDBottegue(request):
    lista = []
    try:
        client = bigquery.Client()
        query = f"SELECT * FROM `{PROJECTO}.{DB}.{TABELA}` LIMIT 100"
        query_job = client.query(query)

        for row in query_job.result():
            lista.append(dict(row))
    except Exception as e:
        print (f"Errore di conessione {e}")

    return render(request,'listaBD.html',{'lista':lista})

# ----------DELETE TABLA -------------------
def eliminaData(request):
    client = bigquery.Client()
    sql = f"TRUNCATE TABLE `{PROJECTO}.{DB}.{TABELA}`"
    client.query(sql).result()
    return redirect('/listaBD/')

#-------------DOCUMENTO DE MILANO----------------------------
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

def lege_DataPDF(request):
    respuesta = ""
    mail = conectar_correo()
    if not mail:
        passw = os.environ.get('EMAIL_CONTRASENA')
        return HttpResponse(passw)
    else:
        print("se conecto al email ")

    hoy = datetime.date.today()
    fecha = hoy.strftime('%d-%b-%Y')
    print("fecha "+fecha)
    
    status, mensajes = mail.uid('search',None,'FROM','reporting@mercatocentrale.it','ON',fecha)
    id_correos = mensajes[0].decode().split()
    if not id_correos:
        print("No se encontraron correos nuevos sin leer.")
        return HttpResponse("non ci sono emails")
    giornaliero = False
    existepdf = False
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
                print(asunto)
             # Decodificar el asunto del correo si tiene caracteres raros
            if isinstance(asunto, bytes):
                asunto = asunto.decode(codificacion or "utf-8")

        # Revisar las partes del correo para buscar archivos adjuntos
        
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
            if "giornata MCM" in asunto:
                if  "90516" in nombre_archivo:
                    if nombre_archivo.lower().endswith('.pdf'):
                        contenido = parte.get_payload(decode=True)
                        file_memoria = io.BytesIO(contenido)
                        print(file_memoria)
                
                        bottega = "Macelleria Milano"
                        pdfFileObj = PyPDF2.PdfReader(file_memoria)
                        testo_completo = ""
                        for page in pdfFileObj.pages:
                            respuesta += page.extract_text()
                        existepdf = True
            if "giornaliero MCM" in asunto:
                if  "90516" in nombre_archivo:
                    if nombre_archivo.lower().endswith('.pdf'):
                        contenido = parte.get_payload(decode=True)
                        file_memoria = io.BytesIO(contenido)
                        print(file_memoria)
                
                        bottega = "Macelleria Milano"
                        pdfFileObj = PyPDF2.PdfReader(file_memoria)
                        testo_completo = ""
                        for page in pdfFileObj.pages:
                            respuesta += page.extract_text()
                        existepdf = True
                        giornaliero = True
            else:
                continue
    if not existepdf:
        if nombre_archivo.lower().endswith(('.xls','xlsx')):
            return HttpResponse("non esiste il pdf")        

    # Cerrar sesión de manera segura
    mail.close()
    mail.logout()

    
    """if request.method == 'POST':
        form = PdfForm(request.POST, request.FILES)
        if form.is_valid():
             f = request.FILES['pdf_extra']
             pdfFileObj = PyPDF2.PdfReader(f)
             for page in pdfFileObj.pages:
                respuesta += page.extract_text()+"\n"
    else:
        form = PdfForm()
        return render(request, 'pdfTesto.html', {'form': form})"""
    #testo=""
    #if request.method == 'POST':
    #   form = PdfForm(request.POST, request.FILES)
    #    if form.is_valid():
    #         f = request.FILES['pdf_extra']
    #         pdfFileObj = PyPDF2.PdfReader(f)
    #         for page in pdfFileObj.pages:
    #            testo += page.extract_text()+"\n"
    #else:
    #    form = PdfForm()
    #    return render(request, 'pdfTesto.html', {'form': form})

    listaTesto = []
    listaOrari = []
    listaTotale = []
    totaleIncassi = ""
    totaleIncassiPre = ""
    diferenza = ""
    incasso = True
    datosArti = False
    datosOrari = False
    #testo = request.session.get('testo','')
    fila = respuesta.splitlines()
    dataDoc = fila[0].split()[0]
    for orari in respuesta.splitlines():
        if re.search(r"FASCIA ORARIA INCASSI BOTTEGA?",orari,re.IGNORECASE):
            datosOrari = True
            continue
        if re.search(r"TOTALE INCASSI\s(.*)",orari,re.IGNORECASE):
            if incasso:
                ti = orari
                numinc = ti.split("TOTALE INCASSI")[1]
                partes = numinc.split()
                fechaincaso = partes[0]
                totaleIncassi = partes[1]
                incasso = False
            else:
                tip = orari
                numincpre = tip.split("TOTALE INCASSI")[1]
                partespre = numincpre.split()
                fechaincasopre = partespre[0]
                totaleIncassiPre = partespre[1]
            datosOrari = False
        if re.search(r"DIFFERENZA\s*(.*)",orari,re.IGNORECASE): 
            dif = orari
            num = dif.split("ANALISI ARTICOLI")[0]
            diferenza = num.split("DIFFERENZA % PERIODO PRECEDENTE")[1]
            datosOrari = False
        if datosOrari:
            listaOrari.append(orari)

    patronOrari = r"(?P<orari>\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})\s*(?P<importeOra>[\d.,]+)"
    listaImporario = []
    for incassi in listaOrari:
         o = re.search(patronOrari,incassi)
         if o:
             ora = o.groupdict()
             ora['data']=dataDoc
             listaImporario.append(ora)
     
    for linea in respuesta.splitlines():
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

    tcper = totaleCotoleteria + totaleCotoleteria*10/100
    tmper = totaleMacelleria + totaleMacelleria*10/100

    return render(request, 'pdfTesto.html',{'testo':listaArti,'orari':listaImporario,'tm':tmper,'tc':tcper,'c':totaleContorni,
                                              'dfz':diferenza,'ti':totaleIncassi,'tip':totaleIncassiPre,
                                              'fi':fechaincaso,'fip':fechaincasopre,'giornaliero':giornaliero})

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