from rest_framework.serializers import ModelSerializer
from .models import SavedModel

class SavedModelSerializer(ModelSerializer):
    class Meta:
        model = SavedModel
        fields = "__all__"
