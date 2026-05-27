from xml.parsers.expat import model
from django.db import models

# Create your models here.
class vendutoOra(models.Model):
    data=models.CharField(max_length=50)
    fasciaOraria=models.CharField(max_length=50)
    incassi=models.DecimalField(max_digits=8,decimal_places=2)

class Venta(models.Model):
    data=models.CharField(max_length=50)
    nomeProdutto=models.CharField(max_length=50)
    importo=models.DecimalField(max_digits=6,decimal_places=2)
    unita=models.FloatField()
    totPer=models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nomeProdutto}-{self.importo}-{self.unita}-{self.totPer}"

class prodotiOra(models.Model):
    #numeroProd=models.BigIntegerField(primary_key=True)
    data=models.CharField(max_length=50)
    orario=models.CharField(max_length=20)
    nome=models.CharField(max_length=50)
    importo=models.DecimalField(max_digits=8,decimal_places=2)
    unita=models.IntegerField()

class comparativaVentas(models.Model):
    data=models.CharField(max_length=40)
    dataPrece=models.CharField(max_length=40)
    importo=models.DecimalField(max_digits=8,decimal_places=2)
    importoPrece=models.DecimalField(max_digits=8,decimal_places=2)
    diferenza=models.DecimalField(max_digits=8,decimal_places=2)
    #venta=models.ManyToManyField('Venta')
