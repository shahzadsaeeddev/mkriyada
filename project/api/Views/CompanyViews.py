from .imports import *
from accounts.permissions import HasCompanyRole

from ..Serializers.CompanySerializers import CompanyMasterAccountSerializer
from ..Serializers.Subscription import SubscriptionSerializer


class CompanyListApiView(generics.ListAPIView):
    permission_classes = [HasAPIKey | HasCompanyRole]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated and user.company:
            return Company.objects.filter(id=user.company.id)
        api_key = self.request.headers.get("Authorization")
        if api_key and api_key.startswith("Api-Key "):
            key = api_key.split(" ")[1]
            try:
                company = Company.objects.get(api_key=key)
                return Company.objects.filter(id=company.id)
            except Company.DoesNotExist:
                return Company.objects.none()

        return Company.objects.none()


class CompanyListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = CompanyCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated:
            return Company.objects.filter(users=user)
        api_key = self.request.headers.get("Authorization")
        if api_key and api_key.startswith("Api-Key "):
            key = api_key.split(" ")[1]
            return Company.objects.filter(api_key=key)
        return Company.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)




class CompanyUpdateApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasAPIKey | HasCompanyRole]
    serializer_class = CompanyCreateSerializer

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
        location = Company.objects.filter(id=company.id).first()
        if not location:
            raise PermissionDenied("No Company details found")

        return location

    def perform_update(self, serializer):
        serializer.save()


class CompanyMasterAccountListApiView(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, *args, **kwargs):
        companies = Company.objects.all()
        plans = SubscriptionPlan.objects.all()

        data = {
            "company": CompanyMasterAccountSerializer(companies, many=True).data,
            "plan": SubscriptionSerializer(plans, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)