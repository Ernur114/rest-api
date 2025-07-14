from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet, ModelViewSet
from rest_framework import mixins
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger

from users.serializers import UserModelSerializer
from users.models import Client
from common.paginators import CustomPageNumberPagination


class RegistrationViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Client.objects.all()
    serializer_class = UserModelSerializer
    parser_classes = [MultiPartParser, FormParser]


class ActivateAccount(ViewSet):
    permission_classes = [AllowAny]

    def retrieve(
        self, request: Request, pk: str
    ) -> Response:
        user: Client = get_object_or_404(Client, activation_code=pk)
        now = timezone.now()
        if now > user.expired_code:
            raise PermissionDenied()
        user.is_active = True
        user.save()
        return Response(data={"message": "activation success!"})


# class UserViewSet(ViewSet):
#     permission_classes = [AllowAny]
#     # authentication_classes = [JWTAuthentication]

#     @staticmethod
#     def check_user(request: Request, pk: int) -> User:
#         user = get_object_or_404(User, pk=pk)
#         if request.user.pk != user.pk:
#             raise PermissionDenied(detail="you have no power here")
#         return user



#     @swagger_auto_schema(
#         responses={200: UserSerializer(many=True)}
#     )
#     @method_decorator(cache_page(timeout=60*10))
#     def list(self, request: Request) -> Response:
#         queryset = User.objects.all() # Достаем пользователей
#         logger.info(f"Запросы после queryset: {connection.queries}")
#         paginator = CustomPageNumberPagination() # объявляем пагинатор
#         items = paginator.paginate_queryset(
#             queryset=queryset, request=request
#         ) # делим юзеров на кучки
#         logger.info(f"Запросы после пагинации: {connection.queries}")
#         serializer = UserSerializer(
#             instance=items, many=True
#         ) # в сериализатор передаем кучки пользователей
#         # return Response(data=serializer.data)
#         return paginator.get_paginated_response(
#             data=serializer.data
#         ) # вывод с пагинацией

#     @swagger_auto_schema(
#         responses={
#             200: UserSerializer,
#             404: "User not found"
#         }
#     )
#     @method_decorator(cache_page(timeout=60*10))
#     def retrieve(self, request: Request, pk: int) -> Response:
#         user = get_object_or_404(User, pk=pk)
#         serializer = UserSerializer(user)
#         return Response(data=serializer.data)

#     @swagger_auto_schema(
#         request_body=UserModelSerializer,
#         responses={
#             200: "user updated",
#             400: "serializer not valid",
#             403: "forbidden",
#             404: "user not found"
#         }
#     )
#     def update(self, request: Request, pk: int) -> Response:
#         user = self.check_user(request=request, pk=pk)
#         serializer = UserModelSerializer(
#             instance=user, data=request.data
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(data={"message": "user updated"})

#     @swagger_auto_schema(
#         request_body=UserModelSerializer,
#         responses={
#             200: "user partial updated",
#             400: "serializer not valid",
#             403: "forbidden",
#             404: "user not found"
#         }
#     )
#     def partial_update(self, request: Request, pk: int) -> Response:
#         user = self.check_user(request=request, pk=pk)
#         serializer = UserModelSerializer(
#             instance=user, data=request.data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(data={"message": "user partial updated"})

#     @swagger_auto_schema(
#         responses={
#             200: "user has been deleted",
#             403: "forbidden",
#             404: "user not found"
#         }
#     )
#     def destroy(self, request: Request, pk: int) -> Response:
#         user = self.check_user(request=request, pk=pk)
#         user.delete()
#         return Response(
#             data={"message": "user has been deleted"}
#         )


class UserModelViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Client.objects.all
    serializer_class = UserModelSerializer
    parser_classes = [MultiPartParser, FormParser]
