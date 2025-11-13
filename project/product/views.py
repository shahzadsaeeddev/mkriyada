import os

from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated
from api.Views.Pagination import StandardResultsSetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client
from .activityLogsMixins import ActivityLogMixin
from .serializers import *
from accounts.permissions import HasProductsRole, HasUmoRole, HasCategoryRole

from api.Views.CompanyMixins import CompanyQuerysetMixin


class MediaFilesListCreateView(ActivityLogMixin, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MediaFilesSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return MediaFiles.objects.by_location(self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save(company=self.request.user.company)
        return super().perform_create(serializer)


class MediaFilesRetrieveUpdateView(ActivityLogMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MediaFilesSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        pk = self.kwargs.get(self.lookup_field)
        return MediaFiles.objects.by_location(self.request.user).filter(pk=pk)


class CategoryListCreateView(ActivityLogMixin, CompanyQuerysetMixin, ListCreateAPIView):
    permission_classes = [HasCategoryRole]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']


    def perform_create(self, serializer):
        instance = serializer.save(company=self.request.user.company)
        return super().perform_create(serializer)


class CategoryRetrieveUpdateDeleteView(ActivityLogMixin, CompanyQuerysetMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [HasCategoryRole]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'pk'




class UnitOfMeasurementListCreateView(ActivityLogMixin, CompanyQuerysetMixin, ListCreateAPIView):
    permission_classes = [HasUmoRole]
    serializer_class = UnitOfMeasurementSerializer
    queryset = UnitOfMeasurements.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'unit_value']

    def perform_create(self, serializer):
        instance = serializer.save(company=self.request.user.company)
        return super().perform_create(serializer)


class UnitOfMeasurementRetrieveUpdateDeleteView(ActivityLogMixin, CompanyQuerysetMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [HasUmoRole]
    serializer_class = UnitOfMeasurementSerializer
    queryset = UnitOfMeasurements.objects.all()
    lookup_field = 'pk'


class ProductListCreateView(ActivityLogMixin, CompanyQuerysetMixin, ListCreateAPIView):
    permission_classes = [HasProductsRole]
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['item_no', 'name', 'item_type']
    queryset = ProductItems.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        instance = serializer.save(company=self.request.user.company)
        return super().perform_create(serializer)

class ProductRetrieveUpdateDeleteView(ActivityLogMixin, CompanyQuerysetMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [HasProductsRole]
    serializer_class = ProductSerializer
    queryset = ProductItems.objects.all()
    lookup_field = 'pk'



class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = NotificationCenter.objects.all()
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            subject = serializer.validated_data["subject"]
            channel = serializer.validated_data["channel"]
            message = serializer.validated_data["message"]
            recipient = "shahzadmehar0214@gmail.com"
            notification = serializer.save(status="Pending")
            print(subject, recipient, message, channel)

            if channel == "Email":
                send_mail(subject, message, os.environ.get("EMAIL_HOST_USER"), [recipient], fail_silently=False, )
                notification.status = "Sent"
                notification.save()
                return Response({"status": "Email sent!", "id": notification.id}, status=status.HTTP_200_OK, )

            elif channel == "SMS":
                account_sid = os.environ["TWILIO_ACCOUNT_SID"]
                auth_token = os.environ["TWILIO_AUTH_TOKEN"]

                client = Client(account_sid, auth_token)
                sms = client.messages.create(body=message, from_=os.environ["TWILIO_PHONE_NUMBER"], to=recipient, )
                notification.status = "Sent"
                notification.save()
                return Response({"status": "SMS sent!", "id": notification.id}, status=status.HTTP_200_OK, )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ActivityLogsListApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = ActivityLog.objects.filter(company=request.user.company)
        serializer = ActivityLogSerializer(queryset, many=True)
        return Response(serializer.data)


class ItemTagsListCreateApiView(CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemTagsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    queryset = ItemTags.objects.all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)



class ItemTagsRetrieveUpdateDeleteApiView(CompanyQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemTagsSerializer
    queryset = ItemTags.objects.all()
    lookup_field = 'pk'
