from .imports import *
from product.tasks import activity_log_task

from product.activityLogsMixins import ActivityLogMixin


class BusinessLocationListCreateView(ActivityLogMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = BusinessLocationsSerializer

    def get_queryset(self):
        company = self.get_company()
        return EgsLocations.objects.filter(company=company)

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        return super().perform_create(serializer)


class BusinessLocationUpdateView(ActivityLogMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = BusinessLocationsUpdateSerializer

    def get_object(self):
        user = self.request.user
        company = None

        api_key = self.request.headers.get('Authorization')
        if api_key and api_key.startswith("Api-Key "):
            key = api_key.split(" ")[1]
            try:
                company = Company.objects.get(api_key=key)
            except Company.DoesNotExist:
                raise PermissionDenied("Invalid API key, company not found.")
        elif isinstance(user, AnonymousUser) or not hasattr(user, 'company'):
            raise PermissionDenied("No API key provided and user is not authenticated.")
        else:
            company = user.company
        location = EgsLocations.objects.filter(company=company).first()
        if not location:
            raise PermissionDenied("No Location details found for the company's company.")

        return location

    def perform_update(self, serializer):
        serializer.save()
