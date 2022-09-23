from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from coreapp.models import User
from rest_framework.authtoken.models import Token


class UserSerializer(ModelSerializer):
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    extra_kwargs = {
        'password': {'write_only': True}
    }

    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'message': 'passwords most match'})

        user.set_password(password)
        user.save()
        Token.objects.create(user=user)
        return user