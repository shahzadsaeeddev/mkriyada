from rest_framework import generics
from ..Serializers.SubscribersSerializer import SubscriberSerializer
from .Pagination import StandardResultsSetPagination
from accounts.models import Users
from accounts.permissions import HasSubscribersRole


class SubscriberListApiView(generics.ListAPIView):
    permission_classes = [HasSubscribersRole]
    serializer_class = SubscriberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Users.objects.filter(company__isnull=False)
