from .imports import *


class SupplierDetailsCreateApiView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = SupplierEgsSerializer

    def get_queryset(self):
        company = self.request.user.company
        return SupplierDetails.objects.filter(company=company)

    def perform_create(self, serializer):
        company_id = self.request.data.get("company")
        company = Company.objects.get(id=company_id)
        serializer.save(company=company)


class SupplierDetailsUpdateApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = SupplierEgsSerializer

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
        supplier = SupplierDetails.objects.filter(company=company).first()
        if not supplier:
            raise PermissionDenied("No supplier details found for the company's company.")

        return supplier

    def perform_update(self, serializer):
        serializer.save()