from logging import getLogger
from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.viewsets import ModelViewSet

import numpy as np
from PIL import Image

from django_gui.celery import app
from .step_1_greyX_TP import scrap_the_file

from celery.result import AsyncResult
import re
from .serializers import SavedModelSerializer
from .models import SavedModel, InterSavedModel
from .step_1_greyX_TP import scrap_the_file
from .tasks import upload_via_celery

from pydrive2.auth import GoogleAuth, AuthenticationError
from pydrive2.drive import GoogleDrive
import pandas as pd
import json
from django.utils import timezone
from .models import FileModel
from django.core.files import File

import os

input_path = settings.MEDIA_ROOT + '/screenshots/full/'
output_path = settings.MEDIA_ROOT + '/ocr/'
logger = getLogger(__name__)

gauth = GoogleAuth()
CSV_REQUIRED_FIELD = {
    "Company",
    "Website",
    "Code",
}


@csrf_exempt
def login(request):
    return HttpResponseRedirect(gauth.GetAuthUrl())


def authorized_view(request):
    x = request.GET["code"]
    request.session["code"] = x

    gauth.Auth(x)

    cred_file = re.sub('[\W_]+', '', "file_{}".format(str(timezone.now()))) + ".txt"
    gauth.SaveCredentialsFile(credentials_file=cred_file)
    #
    # drive = GoogleDrive(gauth)
    # file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    # for f in file_list:
    #     if f['mimeType'] == 'application/vnd.google-apps.folder' and f['title'] == "full_screenshots":
    #         folder_list = drive.ListFile({'q': f"'{f['id']}' in parents and trashed=false"}).GetList()
    #         print(folder_list)

    request.session["cred_file"] = cred_file

    return HttpResponseRedirect(reverse("upload_form"))


@csrf_exempt
def upload_form(request):
    if gauth.credentials is None:
        if "cred_file" not in request.session:
            return HttpResponseRedirect(reverse("login"))

        gauth.LoadCredentialsFile(request.session["cred_file"])
        if gauth.credentials is None:
            return HttpResponseRedirect(reverse("login"))

    return render(request, "form_.html")

def is_valid_csv_file(file_stream) -> bool:
    """Validate input CSV file
    - Check first line contain required fields
    """
    first_line = file_stream.readline().strip()
    items_splitted = first_line.decode('utf-8').split(",")
    items = {item.strip() for item in items_splitted}
    missing_columns = CSV_REQUIRED_FIELD - items
    file_stream.seek(0)  # Reset cursor
    logger.warning(f"Found missing columns: {missing_columns}")
    return not missing_columns

@csrf_exempt
def uplo_custom(request):
    if "cred_file" not in request.session:
        return HttpResponseRedirect(reverse("login"))

    if gauth.credentials is None:
        if "cred_file" not in request.session:
            return HttpResponseRedirect(reverse("login"))

        gauth.LoadCredentialsFile(request.session["cred_file"])
        if gauth.credentials is None:
            return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        file = request.FILES["links"]

        file_name = request.POST["csv_name"]

        if not (file.name.endswith(".csv") or file.name.endswith(".txt")):
            return render(request, "form_.html", context={"required": "File must be of type .txt or .csv"})
        
        if not is_valid_csv_file(file_stream=file):
            return render(request, "form_.html", context={"required": f"File must be contains fields: {','.join(CSV_REQUIRED_FIELD)}"})

        # cred_file = re.sub('[\W_]+', '', "file_{}".format(str(timezone.now())))+".txt"
        cred_file = request.session["cred_file"]

        file_model = FileModel(file_field=file, cred_file_field=File(open(cred_file, "r")))
        file_model.save()

        filename = file_model.file_field.name
        cred_file_ = file_model.cred_file_field.name

        task = upload_via_celery_home.delay(open(settings.MEDIA_ROOT + "/" + filename,encoding="utf-8").read().splitlines(),
                                            file_name, open(settings.MEDIA_ROOT + "/" + cred_file_).read())
        file_model.delete()

        cred_file = request.session["cred_file"]
        if os.path.exists(settings.BASE_DIR + "/" + cred_file):
            os.remove(settings.BASE_DIR + "/" + cred_file)
            try:
                del request.session["cred_file"]
            except:
                pass

        return HttpResponseRedirect(reverse("get_task_progress", args=(task.task_id,)))

    return HttpResponseRedirect(reverse("upload_form"))


def get_task_progress(request, task_id):
    return render(request, 'display_progress.html', context={'task_id': task_id})


def get_task_update(request, task_id):
    result = AsyncResult(task_id)
    if result.state == "SUCCESS":
        request.session["dict"], request.session["csv_link"] = result.get()

    data = {"state": result.state, "info": result.info}
    logger.warning(f"result = {data}")

    return JsonResponse({"state": result.state, "info": result.info})


def get_table(request):
    dict_ = json.loads(request.session["dict"])

    dict_["link_to_image"] = {}
    for i in dict_["image_data"].keys():
        im = np.array(dict_["image_data"][i])
        # print(im.shape)

        im = Image.fromarray(im.astype(np.uint8))
        name = re.sub(r'[\W_]+', "", str(timezone.now()))
        # print(name)
        im.save(settings.MEDIA_ROOT + "/screenshots/permanent/" + name + ".jpg")
        dict_["link_to_image"][i] = "permanent/" + name + ".jpg"

    if "image_data" in dict_:
        del dict_["image_data"]

    logger.info(f"data: {dict_}")

    print(dict_)

    df = pd.DataFrame(data=dict_)
    df.rename(columns={'Translated Text': 'translated_text'}, inplace=True)

    data = json.dumps({"links": list(df["link_to_image"]), "drive_links": list(df["drive_link"])})

    return render(request, "table.html", {"table": df, "links": str(data), "csv_link": request.session["csv_link"]})


class SavedModelViewSet(ModelViewSet):
    serializer_class = SavedModelSerializer
    queryset = SavedModel.objects.all()


@app.task(bind=True)
def upload_via_celery_home(self, name, file_name, cred_file):
    self.update_state(state='PROGRESS')
    cred_name = str(timezone.now())
    cred_name = re.sub('[\W_]+', '', "file_{}".format(cred_name)) + ".txt"
    uploaded_file_path = os.path.join(settings.MEDIA_ROOT,
                                      'uploaded',
                                      f"{cred_name}.txt")
    with open(uploaded_file_path, "w") as file:
        file.write(cred_file)

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(uploaded_file_path)

    # all_objects_dict = {"web_address":[],"original_text":[],"translated_text":[],"name":[],"hyperlink":[],"img":[],"link_to_image":[],"drive_link":[]}
    all_objects_dict = scrap_the_file(name, gauth, self)
    dataframe = pd.DataFrame(all_objects_dict)
    dataframe.columns = ["Page", "description", "Translated Text", "Name", "hyperlink", "img", "link_to_image",
                         "drive_link", "image_data"]
    # dict = dataframe.to_csv(settings.MEDIA_ROOT+"/"+file_name+".csv")
    dataframe_dict = dataframe.to_dict()
    json_str = json.dumps(dataframe_dict)

    df = dataframe.drop(columns=["image_data", "link_to_image"], axis=1)

    csv_name = re.sub(r'[\W_]+', "", str(timezone.now()))
    df.to_csv("csv_{}.csv".format(csv_name))
    drive = GoogleDrive(gauth)
    file = drive.CreateFile()
    file.SetContentFile("csv_{}.csv".format(csv_name))
    file["title"] = file_name
    file.Upload()

    if os.path.exists("csv_{}.csv".format(csv_name)):
        try:
            os.remove("csv_{}.csv".format(csv_name))
        except:
            pass
    return json_str, file.metadata["embedLink"]
