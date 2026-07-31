from ast import Str
from encodings import utf_8
import os
from pickle import INT
import tempfile
import json

from django.core.exceptions import RequestAborted

"""json_content = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if(json_content):
    with tempfile.NamedTemporaryFile(mode="w",delete=False,suffix=".json") as temp_file:
        temp_file.write(json_content)
        temp_file_path = temp_file.name

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path"""


from ctypes.util import test
from datetime import datetime
import io
from http import client
from string import printable
from typing import Self
from urllib import response
from xml.etree.ElementInclude import include
from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from urllib.parse import urlencode
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

def addPdfDatabase(request):
    testo = ""
    #hoy = datetime.date.today()
    fecha_pdf = ""
    fechaI = ""
    fechaF = ""
    datapdf = ""
    bottega = ""
    lista = []
    
    if request.method == 'POST':
        
        formCalendar = CalendarReport(request.POST)
        
        if formCalendar.is_valid():
            fecha_ini = request.POST.get('calendario_inizio')
            fecha_fine = request.POST.get('calendario_fine')
            #return HttpResponse(fecha_ini+fecha_fine)        
            
            #fp = fecha
            #fecha = fecha.replace('/','-')
            partes1 = fecha_ini.split('-')
            meses1 = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul',
                     '08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
            dia1 = int(partes1[2])+1
            fechaI = f"{str(dia1)}-{meses1[partes1[1]]}-{partes1[0]}"
            fechaIni = f"{partes1[2]}-{meses1[partes1[1]]}-{partes1[0]}"

            partes2 = fecha_fine.split('-')
            meses2 = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul',
                     '08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
            dia2 = int(partes2[2])+2
            fechaF = f"{str(dia2)}-{meses2[partes2[1]]}-{partes2[0]}"
            fechaFin = f"{partes2[2]}-{meses1[partes1[1]]}-{partes1[0]}"
            
        mail = conectar_correo()

        if not mail:
            passw = os.environ.get('EMAIL_CONTRASENA')
            return HttpResponse("Non c'e conessione col e-mail.")
        else:
            print("conesso al email ")
        #status, mensajes = mail.uid('search',None,'FROM','reporting@mercatocentrale.it','ON',fecha)
        status, mensajes = mail.uid('search',None,'FROM','reporting@mercatocentrale.it','SINCE',fechaI,'BEFORE',fechaF)
        id_correos = mensajes[0].decode().split()
        if not id_correos:
            return HttpResponse("non ci sono emails")
        
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
                        
                    # Decodificar el asunto del correo si tiene caracteres raros
                if isinstance(asunto, bytes):
                    asunto = asunto.decode(codificacion or "utf-8")
                    print(asunto)
            a = asunto.split()
            #longi = len(a)
            fecha_pdf = a[-1]  
            
            
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

                # Verificar la Bottega
                if "90606" in nombre_archivo:
                    bottega = "Macelleria Bolzano"
                elif "90619" in nombre_archivo:
                    bottega = "Girarrosto Bolzano"
                elif "90132" in nombre_archivo:
                    bottega = "Ristorante Firenze"
                elif "90516" in nombre_archivo:
                    bottega = "Macelleria Milano"
                elif "90518" in nombre_archivo:
                    bottega = "Girarrosto Milano"
                elif "90514" in nombre_archivo:
                    bottega = "Cotoletta Milano"
                elif "90410" in nombre_archivo:
                    bottega = "Girarrosto Torino"
                elif "90422" in nombre_archivo:
                    bottega = "Hamburguer Torino"
                elif "90313" in nombre_archivo:
                    bottega = "Gilly"
                elif "90411" in nombre_archivo:
                    bottega = "Macelleria Torino"
                elif "90119" in nombre_archivo:
                    bottega = "Girarrosto Firenze"
                elif "90204" in nombre_archivo:
                    bottega = "Macelleria Roma"
                elif "90211" in nombre_archivo:
                    bottega = "Girarrosto Roma"
                elif "90101" in nombre_archivo:
                    bottega = "Macelleria Firenze"
                elif "1118" in nombre_archivo:
                    bottega = "Girarrosto Albatroz"
                elif "1131" in nombre_archivo:
                    bottega = "Macelleria Albatroz"
                
                # Verificar si el archivo es un PDF
                if "giornaliero" in asunto:
                    
                    if nombre_archivo.lower().endswith('.pdf'):
                        
                        contenido = parte.get_payload(decode=True)
                        file_memoria = io.BytesIO(contenido)
                        pdfFileObj = PyPDF2.PdfReader(file_memoria)
                        testo = ""
                        
                        for page in pdfFileObj.pages:
                            testo += page.extract_text()
                            
                        #lista.append(addInfoPdf(testo,fecha_pdf,bottega))
                        addInfoPdf(testo,fecha_pdf,bottega)
                        #datapdf = fecha_pdf
                            
                        existepdf = True
                else:
                    continue
        if not existepdf:
            return HttpResponse("non esiste il pdf")        

            # Cerrar sesión de manera segura
        mail.close()
        mail.logout()

    else:
        formCalendar = CalendarReport()
        return render(request, 'calendar.html', {'formCalendar': formCalendar})
     
    #return HttpResponse(lista)       
    base_url = reverse("listaBDBottegue")
    query_string = urlencode({"data_inizio":fechaIni,"data_fine":fechaFin})
    return redirect(f"{base_url}?{query_string}")
        
def addInfoPdf(texto,fecha,bottega):
    
    listaIncasi = {}
    totaleIncassi = ""
    totaleIncassiPre = ""
    diferenza = "0"
    ingresi = "0"
    ingPer = "0"
    ingPre = "0"
    incasso = True
    listaa = []
    
    lineas = texto.splitlines()
    match ="match"
    trovo = False
    for i, t in enumerate(lineas):
        if re.search(r"TOTALE INCASSI\s(.*)",t,re.IGNORECASE):
            if incasso:
                ti = t.split('TOTALE INCASSI')[1]
                totaleIncassi = ti.split()[1]
                listaIncasi['inc']=totaleIncassi
                incasso = False
            else:
                tip = t.split('TOTALE INCASSI')[1]
                totaleIncassiPre = tip.split()[1]
                listaIncasi['pre']=totaleIncassiPre
        elif re.search(r"DIFFERENZA",t,re.IGNORECASE):
            d = t.split("DIFFERENZA % PERIODO PRECEDENTE")[1].strip()
            diferenza = d.split("ANALISI ARTICOLI")[0]
            if diferenza == "":
                diferenza = 100
            listaIncasi['dif']=diferenza
        elif re.search(r"INGRESSI",t,re.IGNORECASE):
            #listaa.append(t)
            #if i+1 < len(lineas):
            #listaa.append(t)
            #siguiente = lineas[i+1].strip()
            #match = re.search(r'INGRESSI\s*(d{1,4})\s*-?\s*[\d\.,]+\s*(\d{1,4})',t)
            #match = re.search(r'INGRESSI\s*(d{1,5})(-?\d+.,\d+)\s*(\d{1,5})',t)
            #match = re.search(r'INGRESSI\s*([\d\.,]+)[-\s]*[\d\.,]*\s*([\d\.,]+)',t,re.IGNORECASE)
            #match = re.search(r'INGRESSI\s*([\d\.,]+).*?([\d\.,]+)\s*$',t,re.IGNORECASE)
            
            numeros = ""
            siguiente = ""
            numerosig = ""
            res = ""
            objn1 = 0
            objn2 = 0
            n1=0
            n2=0
            n3=0
            m1 = 0
            m2 = 0
            r=0
            dec = 1

            alado = re.findall(r'\d{1,4}(?:\.\d{3})*,\d+|\d+,\d+|\d+',t)

            if i+1 < len(lineas):
                siguiente = lineas[i+1].strip()
                numerosig = re.findall(r'\d{1,4}(?:\.\d{3})*,\d+|\d+,\d+|\d+',siguiente)

            if  numerosig != "":
                numeros = numerosig
            else:
                numeros = alado

            if len(numeros) == 3:
                t1 = numeros[0].replace('.','')
                t1 = numeros[0].replace(',','.')
                t2 = numeros[1].replace('.','')
                t2 = numeros[1].replace(',','.')
                n1 = round(float(t1))
                n2 = round(float(t2),2)   
                t3 = numeros[2].replace('.','')
                t3 = numeros[2].replace(',','.')
                n3 = round(float(t3))

                nn2 = round(n2)
                for i in range(len(str(nn2))):
                    dec = dec*10
                r = round(100 - (n1*100/n3),2)
                if r == n2:
                    ingresi = n1
                    ingPer = n2
                    ingPre = n3
                else:
                    trov = False
                    contt = 0
                    while trov == False:
                        pos = len(t2)+contt
                    objn1 = float(t1[:pos])
                    objn2 = float(t1[pos:]+t2)
                    r = round(100 - (objn1*100/n3),2)
                    if r == objn2:
                        ingresi = objn1
                        ip = float(objn2)
                        ingPer = ip/dec
                        ingPre = n3
                        trov = True
                    else:
                        contt += 1
                    
            elif len(numeros) == 2:
                t1 = numeros[0].replace('.','')
                t1 = numeros[0].replace(',','.')
                t2 = numeros[1].replace('.','')
                t2 = numeros[1].replace(',','.')
                n1 = round(float(t1))
                n2 = round(float(t2),2)

                if n2 == 0:
                    if '0.' in t1:
                        ingresi = t1[:t1.find('0.')]
                        ingPer = t1[t1.find('0.'):]
                        ingPre = 0
                elif n1 > n2:
                    trova = False
                    cont = 0
                    while trova == False:
                        pos = len(t2)+cont
                        ob1 = float(t1[:pos])
                        ob2 = float(t1[pos:])
                        r = round(100 - (ob1*100/n2),2)*-1
                        if r == ob2:
                            ingresi = ob1
                            ingPer = ob2
                            ingPre = n2
                            trova = True
                        else:
                            cont += 1
                        
            """listaa.append(bottega)
            listaa.append(fecha)
            listaa.append(n1)
            listaa.append(n2)
            listaa.append(n3)
            listaa.append("---")
            listaa.append(ingresi)
            listaa.append(ingPer)
            listaa.append(ingPre)
            listaa.append('<br>')"""
                      
    client = bigquery.Client()
    table_id = 'project-d83b9b63-299f-44e9-be1.bdBottegue.venditaGiorno'
    row_to_insert = [{
                      'data':fecha,
                      'bottega':bottega,
                      'incasso':totaleIncassi,
                      'incassoPre':totaleIncassiPre,
                      'diferenza':diferenza,
                      'ingressi':ingresi,
                      'ingrepre':ingPre
                      }]
    errors = client.insert_rows_json(table_id,row_to_insert)
    if errors == []:
        return HttpResponse("Nuove righe inserite con successo.")
    else:
        return HttpResponse("Errore durante l'inserimento")

    #return listaa
    
# -------------LIST DE DATOS DE LA BD-----------------
def listaBDBottegue(request):
    
    dataI = request.GET.get('data_inizio')
    dataF = request.GET.get('data_fine')

    dataI = datetime.strptime(dataI,'%d-%b-%Y').strftime('%d/%m/%Y')
    dataF = datetime.strptime(dataF,'%d-%b-%Y').strftime('%d/%m/%Y')
            
    lista = []
    if not dataI or not dataF:
        return HttpResponse("Mancanno le date")
    try:
        client = bigquery.Client()
        query = f"""SELECT * FROM `{PROJECTO}.{DB}.{TABELA}` WHERE PARSE_DATE('%d/%m/%Y',data) BETWEEN PARSE_DATE('%d/%m/%Y',@dataI) AND PARSE_DATE('%d/%m/%Y',@dataF) LIMIT 100"""
        #query_job = client.query(query)
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("dataI", "STRING", dataI),
                bigquery.ScalarQueryParameter("dataF", "STRING", dataF),
            ]
        )
        query_job = client.query(query, job_config=job_config)

        for row in query_job.result():
            lista.append(dict(row))
    except Exception as e:
        print (f"Errore di conessione {e}")

    return render(request,'listaBD.html',{'lista':lista, 'dataI':dataI, 'dataF':dataF})

def listaInfoBottegue(request):
    if request.method == 'POST':
        formCalendar = CalendarReport(request.POST)
        
        if formCalendar.is_valid():
            fecha_ini = request.POST.get('calendario_inizio')
            fecha_fine = request.POST.get('calendario_fine')
            lista = []
            totalePeriodo = {}
            #return HttpResponse(fecha_ini+fecha_fine)        
            
            #fp = fecha
            #fecha = fecha.replace('/','-')
            partes1 = fecha_ini.replace('-','/')
            """partes1 = fecha_ini.split('-')
            meses1 = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul',
                        '08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}"""
            #dia1 = int(partes1[2])+1
            #fechaI = f"{str(dia1)}-{meses1[partes1[1]]}-{partes1[0]}"
            dataI = partes1

            partes2 = fecha_fine.replace('-','/')
            """partes2 = fecha_fine.split('-')
            meses2 = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul',
                        '08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}"""
            #dia2 = int(partes2[2])+2
            #fechaF = f"{str(dia2)}-{meses2[partes2[1]]}-{partes2[0]}"
            dataF = partes2

            dataI = datetime.strptime(dataI,'%Y/%m/%d').strftime('%d/%m/%Y')
            dataF = datetime.strptime(dataF,'%Y/%m/%d').strftime('%d/%m/%Y')

            """lista.append(dataI)
            lista.append(dataF)
            return HttpResponse(lista)"""
            
            if not dataI or not dataF:
                return HttpResponse("Mancanno le date")
            try:
                client = bigquery.Client()
                query = f"""SELECT * FROM `{PROJECTO}.{DB}.{TABELA}` WHERE PARSE_DATE('%d/%m/%Y',data) BETWEEN PARSE_DATE('%d/%m/%Y',@dataI) AND PARSE_DATE('%d/%m/%Y',@dataF) LIMIT 100"""
                #query_job = client.query(query)
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("dataI", "STRING", dataI),
                        bigquery.ScalarQueryParameter("dataF", "STRING", dataF),
                    ]
                )
                query_job = client.query(query, job_config=job_config)

                for row in query_job.result():
                    lista.append(dict(row))
                
                
                #return HttpResponse(lista)
                #totalePeriodo = calculoTotalePeriodo(lista)
            except Exception as e:
                print (f"Errore di conessione {e}")
    else:
        formCalendar = CalendarReport()
        return render(request, 'buscar.html', {'formCalendar': formCalendar})

    return render(request,'infoBD.html',{'lista':lista, 'dataI':dataI, 'dataF':dataF})

# ----------DELETE TABLA -------------------
def eliminaData(request):
    data = request.GET.get('data')

    client = bigquery.Client()
    sql = f"DELETE FROM `{PROJECTO}.{DB}.{TABELA}` WHERE data = '{data}'"
    client.query(sql).result()
    return redirect('/listaBD/')

"""def calculoTotalePeriodo(lista):
    totaleBottegue = {}
    data = ""
    incasso = ""
    incassoPre = ""
    diferenza = ""
    ingressi = ""
    ingrepre = ""
    totalMacRoma = {}
    totalGirRoma = {}
    totalMacFir = {}
    totalGirFir = {}
    totalMacMil = {}
    totalGirMil = {}
    totalMacTor = {}
    totalGirTor = {}
    totalHamTor = {}
    totalMacBol = {}
    totalGirBol = {}
    totalMacAlb = {}
    totalGirAlb = {}
    totalGily = {}
    totalCotMil = {}
    for item in lista:
        totaleBottegue['data'] = item['data']
        totaleBottegue['bottega'] = item['bottega']
        totaleBottegue['incasso'] = item['incasso']
        totaleBottegue['incassoPre'] = item['incassoPre']
        totaleBottegue['diferenza'] = item['diferenza']
        totaleBottegue['ingressi'] = item['ingressi']
        totaleBottegue['ingrepre'] = item['ingrepre']"""
        

#-------------DOCUMENTO DE MILANO----------------------------

cotoletteArticoli = ["Base + patatine","Manzo sportiva","La mortazza","Manzo base + patate","La sportiva",
            "Cotoletta base","Cotoletta Pros Crudo E Fichi - Vitello","Cotoletta Pros Crudo E Fichi - Suino",
            "Con osso manzo","Manzo porcellina","Manzo mortazza","La porcellina","La raffinata","Manzo base","Manzo base + patate"]
contorni = ["Patate Al Forno","Verdure","Riso"]

def report_macelleria_Milano(request):
    respuesta = ""
    mail = conectar_correo()
    if not mail:
        passw = os.environ.get('EMAIL_CONTRASENA')
        return HttpResponse("Non c'e conessione col e-mail.")
    else:
        print("conetto al email ")

    hoy = datetime.today()
    fecha = hoy.strftime('%d-%b-%Y')
    
    status, mensajes = mail.uid('search',None,'FROM','reporting@mercatocentrale.it','ON',fecha)
    id_correos = mensajes[0].decode().split()
    if not id_correos:
        return HttpResponse("non ci sono emails")
    giornaliero = True
    existepdf = False
    
    for correos in id_correos:
        if not existepdf:
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
                            break
                else:
                    continue
                """if "giornaliero MCM" in asunto:
                    if giornaliero and not existepdf:
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
                                existepdf = True"""

    if not existepdf:
        if nombre_archivo.lower().endswith(('.xls','xlsx')):
            return HttpResponse("Non esiste ancora il report di metà giornata di oggi")        

    # Cerrar sesión de manera segura
    mail.close()
    mail.logout()

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

    tcoper = totaleCotoleteria + totaleCotoleteria*10/100
    tmper = totaleMacelleria + totaleMacelleria*10/100
    tcper = totaleContorni + totaleContorni*10/100
    return render(request, 'reportMacelleriaMilano.html',{'testo':listaArti,'orari':listaImporario,'tm':tmper,'tc':tcoper,'c':tcper,
                                              'dfz':diferenza,'ti':totaleIncassi,'tip':totaleIncassiPre,
                                              'fi':fechaincaso,'fip':fechaincasopre,'giornaliero':giornaliero})


def reportData(request):
    respuesta = ""
    fecha = ""
    listaBottega = {}
    if request.method == 'POST':
        formCalendar = CalendarReport(request.POST)
        if formCalendar.is_valid():
             fecha = request.POST.get('calendario')
             #fp = fecha
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
                      'data':fecha,
                      'bottega':bottega}]
    errors = client.insert_rows_json(table_id,row_to_insert)
    return listaIncasi

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


def lista_reportes(request):
    #ruta_dir = os.path.join(os.getcwd())
    ruta_dir = "C:/Users/billi/Desktop/Python App/DjangoWeb/report"
    reportes = []
    if os.path.exists(ruta_dir):
        for archivo in os.listdir(ruta_dir):
            if archivo.endswith(('.pdf','.xls','.xlsx')):
                reportes.append(archivo)
    return render(request,'reportes.html',{'reportes':reportes})

def extraer_texto_pdf(ruta_pdf):
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