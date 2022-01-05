from rest_framework.generics import get_object_or_404
from api.user.serializers import UserSerializer, ApiKeySerializer, AutoBalancerSerializer
from api.user.models import User
from rest_framework import serializers, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import mixins
from rest_framework.views import APIView
from django.shortcuts import get_list_or_404
from .models import ApiKeyModel, AutoBalancerModel
from .script import AutoBalancerMainFun


class UserViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin
):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    error_message = {"success": False, "msg": "Error updating user"}

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = User.objects.get(id=request.data.get("userID"))
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("userID")

        if not user_id:
            raise ValidationError(self.error_message)

        if self.request.user.pk != int(user_id) and not self.request.user.is_superuser:
            raise ValidationError(self.error_message)

        self.update(request)

        return Response({"success": True}, status.HTTP_200_OK)


class ApiKeyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = get_list_or_404(ApiKeyModel)
        serializer = ApiKeySerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ApiKeySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.error_messages)
        
class ApiKeyDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        key = ApiKeyModel.objects.get(pk=pk)
        key.delete()
        return Response({"Message": "Deleted!"})



class AutoBalancerView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        auto_balancers = get_list_or_404(AutoBalancerModel)
        serializer = AutoBalancerSerializer(auto_balancers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AutoBalancerModel(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.error_messages)




class AutoBalancerDetail(APIView):

    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        balancer = AutoBalancerModel.objects.get(pk=pk)
        serializer = AutoBalancerSerializer(balancer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RunAutoBalacer(APIView):
     
    def get(self, request, pk):

        balacer = AutoBalancerModel.objects.get(pk=pk)

        key = 'dummy-key'

        AutoBalancerMainFun(
            api_token=key, 
            loadbalancer_tag=balacer.loadbalancer_tag,
            droplet_tag=balacer.droplet_tag,
            max_drop=balacer.max_drop,
            min_drop=balacer.min_drop,
            cpu=balacer.threshold_CPU,
            load1=balacer.threshold_Load1,
            load5=balacer.threshold_Load5,
            load15=balacer.threshold_Load15
        )

        return Response({"Status": f"{balacer.loadbalancer_name} is running"})
