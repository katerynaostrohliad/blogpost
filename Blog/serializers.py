from rest_framework import serializers
from .models import User


#change the payload(from models) we received to json
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # is the same as fields = ('first_name', 'last_name')
