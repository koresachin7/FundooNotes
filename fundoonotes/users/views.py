"""
* @Author: Sachin S Kore
* @Date: 2022-1-17
* @Title : Fundoo Notes User serializer
"""
import json
import datetime

from drf_yasg import openapi
from rest_framework.exceptions import ValidationError

from loghandler import logger
from django.contrib.auth.models import auth
# third party imports

from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from .task import send_mail
from .utility import JwtEnodeDecode


class UserRegistration(APIView):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('TOKEN', openapi.IN_HEADER, "token", type=openapi.TYPE_STRING)
    ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="username"),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="first_name"),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="last_name"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="password"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="email"),
                'age': openapi.Schema(type=openapi.TYPE_STRING, description="age"),
                'mobile': openapi.Schema(type=openapi.TYPE_STRING, description="mobile"),
            }
        ))
    def post(self, request):
        """
            Description:
                This method is writing Registration of user to inserting data
            Parameter:
                using json
            :return : Response
        """
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.create(validate_data=serializer.data)
                # send_mail.delay(serializer.data.get("email"))
                return Response({"message": "User Creating Successfully ", "data": serializer.data["username"]},
                                status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.error(e)
            return Response({"message": "validation error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            logger.error(e)
            return Response({"message": "invalidate credentials"}, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('TOKEN', openapi.IN_HEADER, "token", type=openapi.TYPE_STRING)
    ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="username"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="password"),
            }
        ))
    def post(self, request):
        """
                Description:
                        This method is writing Login of user
                Parameter:
                        using Dictionary
            """
        try:
            data = request.data
            username = data.get("username")
            password = data.get("password")
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                payload = {
                    'user_id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=600),
                    'iat': datetime.datetime.utcnow()
                }
                print(user.id)
                token = JwtEnodeDecode.encode(payload)
                return Response({"message": "login successfully", 'token': token}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User is invalid", "data": data}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({"message": "validation error"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_403_FORBIDDEN)

# from rest_framework import generics
# from .models import User
# from .serializers import UserSerializer
# from rest_framework import permissions
#
#
# class UserRegistrationGenerics(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#     def perform_create(self, serializer):
#         return serializer.save(id=self.request.data.get("id"))
#
#
# class LoginGenerics(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permissions = [permissions.IsAuthenticated]
#
#     def preform_create(self):
#         return self.queryset.fliter(username=self.request.data.get("username"),
#                                     password=self.request.data.get("password"))
