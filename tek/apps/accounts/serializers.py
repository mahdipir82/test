from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['mobile_number'] = user.mobile_number
        token['name'] = user.name
        token['family'] = user.family
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user': {
                'id': self.user.id,
                'mobile_number': self.user.mobile_number,
                'name': self.user.name,
                'family': self.user.family,
                'email': self.user.email,
            }
        })
        return data