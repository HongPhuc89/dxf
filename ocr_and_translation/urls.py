from . import views
from django.urls import path


list_saved_models = views.SavedModelViewSet.as_view({
    'get':'list'
})

detail_saved_models = views.SavedModelViewSet.as_view({
    'get':'retrieve'
})


urlpatterns = [
    path("",views.login,name = "login"),
    path("authorized/",views.authorized_view,name="authorized"),
    path("form/",views.upload_form,name="upload_form"),

    path("upload_custom/",views.uplo_custom,name="upload_custom"),
    path("get_table/",views.get_table,name="get_table"),


    path("rest/saved_models/",list_saved_models),
    path("rest/saved_models/<int:pk>",detail_saved_models),

    path("get_task/<str:task_id>/",views.get_task_update,name="get_task_update"),
    path("get_task_progress/<str:task_id>/",views.get_task_progress,name="get_task_progress"),


]
