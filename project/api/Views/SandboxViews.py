from .imports import *
from product.activityLogsMixins import ActivityLogMixin

from accounts.permissions import HasCredentialsRole

from accounts.keycloak import update_role_self


class InvoicesSandboxApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.CreateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = InvoiceSandboxSerializer
    queryset = Invoice.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        self.log_activity("Create", instance)
        return instance


class ResubmitInvoiceAPIView(APIView):
    permission_classes = [IsAuthenticated | HasAPIKey]

    def post(self, request):
        company = None
        if request.user and request.user.is_authenticated:
            company = request.user.company
        else:
            api_key = request.headers.get("Authorization")
            if api_key and api_key.startswith("Api-Key "):
                key = api_key.split(" ")[1]
                try:
                    company = Company.objects.get(api_key=key)
                except Company.DoesNotExist:
                    raise PermissionDenied("Invalid API key. Company not found.")
            else:
                raise PermissionDenied("Authentication required.")

        serializer = InvoiceResubmitSerializer(data=request.data, context={"company": company})
        if serializer.is_valid():
            invoice = serializer.save()
            invoice_serialized = InvoiceSandboxSerializer(invoice)
            return Response({"message": "Invoice resubmitted successfully.", "invoice": invoice_serialized.data},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoicesSandboxCreditNoteApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = InvoiceSandBoxCreditNoteSerializer

    def get_queryset(self):
        return Invoice.objects.filter(company=self.get_company())

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        self.log_activity("Create", instance)
        return instance


class InvoicesSandboxDebitNoteApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = InvoiceSandboxDebitNoteSerializer

    def get_queryset(self):
        return Invoice.objects.filter(company=self.get_company())

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        self.log_activity("Create", instance)
        return instance


class ValidateOtpApiView(APIView):
    permission_classes = [HasCredentialsRole]

    def post(self, request, *args, **kwargs):
        scope = request.data.get("scope")
        company = request.user.company

        if scope == "sandbox":
            serializer = SandboxCredentialSerializer(instance=company, data=request.data)
            # auth_header = request.META.get('HTTP_AUTHORIZATION', None)
            # if not auth_header or not auth_header.startswith("Bearer "):
            #     raise serializers.ValidationError("Authorization token missing")
            # auth_token = auth_header.split(" ")[1]
            # company.enabled_zatca = True
            company.save()
            # update_role_self(auth_token, request.user.username, company.name, company.enabled_zatca)
        else:
            return Response({"error": "Invalid scope"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            return Response({"message": "CSID and X509 generated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateSpecificActionApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        scope = request.data.get("scope")
        action = request.data.get("action")
        company = request.user.company

        data = Sandbox.objects.filter(company=company).first() if scope == "sandbox" else Production.objects.filter(
            company=company).first()

        if not data:
            return Response({"error": f"{scope.capitalize()} credentials not found."},
                            status=status.HTTP_400_BAD_REQUEST)

        zatca = Zatca(scope, data.id, request.data.get("otp"))
        response_data = {}

        if action == "csid":
            if not zatca.generate_csid():
                return Response({"error": "CSID generation failed."}, status=status.HTTP_400_BAD_REQUEST)
            response_data["message"] = "CSID generated successfully"

        elif action == "x509":
            if not zatca.generate_x509():
                return Response({"error": "X509 generation failed."}, status=status.HTTP_400_BAD_REQUEST)
            response_data["message"] = "X509 generated successfully"

        elif action == "compliance":
            supplier = SupplierDetails.objects.filter(company=company).first()
            if not supplier:
                return Response({"error": "Supplier details not found."}, status=status.HTTP_400_BAD_REQUEST)

            result_code = compliance_xml(supplier.xml_text, data.id)

            if result_code != 200:
                return Response({"error": "Compliance check failed."}, status=status.HTTP_400_BAD_REQUEST)

            response_data["message"] = "Compliance check passed"

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_200_OK)


class SandboxCredentialsView(CompanyQuerysetMixin, generics.ListAPIView):
    permission_classes = [HasCredentialsRole]
    serializer_class = SandBoxViewSerializer

    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company.id)
