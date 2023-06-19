# from celery import app
from django.conf import settings
from .step_1_greyX_TP import scrap_the_file
from pydrive2.auth import GoogleAuth
import os
import pandas as pd
from .models import InterSavedModel
from celery import shared_task
from django_gui.celery import app
import json


@shared_task
def add(x,y):
    print(x+y)
    return x+y


@app.task(bind=True)
def upload_via_celery(self,name,file_name,cred_file):
    gauth = GoogleAuth()
    print(os.listdir(settings.MEDIA_ROOT+"/uploaded"))
    gauth.LoadCredentialsFile(settings.MEDIA_ROOT+"/"+cred_file)
    self.update_state(state='PROGRESS')


    # all_objects_dict = {"web_address":[],"original_text":[],"translated_text":[],"name":[],"hyperlink":[],"img":[],"link_to_image":[],"drive_link":[]}
    all_objects_dict = scrap_the_file(name,self)
    print(all_objects_dict)

    dataframe =  pd.DataFrame(all_objects_dict)
    dataframe.drop(columns=["image_data"])
    dataframe.columns = ["Page","description","Translated Text","Name","hyperlink","img","link_to_image","drive_link"]

    dict = dataframe.to_dict()
    json_str = json.dumps(dict)

    if os.path.exists(settings.MEDIA_ROOT+"/"+cred_file):
        os.remove(settings.MEDIA_ROOT+"/"+cred_file)

    if os.path.exists(settings.MEDIA_ROOT+"/"+cred_file):
        os.remove(settings.MEDIA_ROOT+"/"+cred_file)



    return json_str,all_objects_dict["image_data"]
