from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from studentsapi.serializers import *


@api_view(['POST'])
def register(request):
    user = User.objects.create(email=request.data['email'])
    user.set_password(request.data['password'])
    user.save()
    refresh = RefreshToken.for_user(user)
    return Response({'user': UserSerializerSelf(user).data, 'refresh': str(refresh),
                     'access': str(refresh.access_token), })


@api_view(['POST'])
def login(request):
    user, _ = User.objects.get_or_create(id_code=request.data['id_code'])
    return Response(UserSerializerSelf(user).data)
    """if len(User.objects.filter(id_code=request.POST['id_code'])) > 0:
        user = User.objects.filter(id_code=request.POST['id_code']).first()
        sr = UserSerializerSelf(user)
        return Response(sr.data)
    else:
        user = User.objects.create(
            id_code=request.POST['id_code'],
            name=request.POST['name'],
        )
        sr = UserSerializerSelf(user)
        return Response(sr.data)"""


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def myData(request):
    refresh = RefreshToken.for_user(request.user)
    return Response({'user': UserSerializerSelf(request.user).data, 'refresh': str(refresh),
                     'access': str(refresh.access_token), })
