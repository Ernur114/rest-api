from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.serializers import UserModelSerializer
from users.models import Client
from common.paginators import CustomPageNumberPagination
from common.permissions import IsOwnerOrAdmin


class RegistrationViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Client.objects.all()
    serializer_class = UserModelSerializer
    parser_classes = [MultiPartParser, FormParser]


class ActivateAccount(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, pk: int) -> Response:
        code = request.query_params.get("code")
        user: Client = get_object_or_404(
            Client, pk=pk, activation_code=code
        )
        now = timezone.now()
        if now > user.expired_code:
            raise PermissionDenied()
        user.is_active = True
        user.save()
        return Response(data={"message": "activation success!"})


class UserModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [IsOwnerOrAdmin]
    queryset = Client.objects.all()
    serializer_class = UserModelSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPageNumberPagination

    @method_decorator(cache_page(timeout=600))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(timeout=600))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
