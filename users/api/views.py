from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CustomUserRegSerializer,
    CustomUserLoginSerializer,
    CustomUserSerializer,
    TokenSerializer,
)
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = CustomUserRegSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(ObtainAuthToken):
    login_serializer_class = CustomUserLoginSerializer

    def post(self, request, *args, **kwargs):
        login_serializer = self.login_serializer_class(data=request.data)

        try:
            if login_serializer.is_valid():
                user = login_serializer.validated_data
                token = Token.objects.get(user=user)
                # try:
                #     token = Token.objects.create(user=user)
                #     print('TRY : ', token)
                # except:
                #     token = Token.objects.get(user=user)
                #     print('EXCEPT : ', token)

                return Response({
                    'token': str(token),
                    'email': user.email,
                },
                    status=status.HTTP_200_OK
                )
        except Exception as ex:
            print(request.data, " : ", ex)
            return Response({
                'message': 'Unable to log in with provided credentials.'
            },
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomUserAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
