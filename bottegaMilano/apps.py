from django.apps import AppConfig
import os
import firebase_admin
from firebase_admin import credentials


class BottegamilanoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bottegaMilano'

    def ready(self):
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'bottega-milano-web-firebase-adminsdk.json')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred,{
                'databaseURL':'http://firebaseio.com'
                })
    
