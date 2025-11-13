import logging
import uuid
import requests

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.forms import model_to_dict
from django.http import HttpResponse
from django.utils.dateparse import parse_date

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import (
    viewsets,
    permissions,
    filters,
    generics,
    status,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework_api_key.permissions import HasAPIKey

from ..Serializers.Commons import (
    LocationSerializer,
    BusinessLocationSerializer,
    CSIDSeliazer,
    ProductionSerializer,
    ProductionX509Serializer,
    BusinessLocationsSerializer,
    BusinessLocationsUpdateSerializer,
    SupplierEgsSerializer,
)
from ..Serializers.CompanySerializers import (
    CompanySerializer,
    CompanyCreateSerializer,
    CompanyUpdateSerializer,
    CompanyPlanSerializer,
)
from ..Serializers.TransactionCommonSerializer import GeneralViewSerializer, ReturnInvoiceNumberSerializer

from ..Serializers.Customer import *
from ..Serializers.Invoices import (
    InvoicesSerializer,
)
from ..Serializers.Production import (
    InvoiceProductionCreateSerializer,
    InvoiceProductionCreditNoteSerializer,
    InvoiceProductionDebitNoteSerializer,
    ProductionCredentialSerializer,
    InvoiceProductionListSerializer
)
from ..Serializers.Sandbox import (
    InvoiceSandboxSerializer,
    InvoiceResubmitSerializer,
    InvoiceSandBoxCreditNoteSerializer,
    InvoiceSandboxDebitNoteSerializer,
    SandboxCredentialSerializer,
    SandBoxViewSerializer,
)
from ..Serializers.Subscription import (
    SubscriptionPlanListSerializer,
    PaymentHistorySerializer,
)
from .Pagination import StandardResultsSetPagination
from ..apifilters import InvoiceFilter, PaymentHistoryFilter
from ..models import (
    Company,
    Invoice,
    EgsLocations,
    Production,
    CustomerDetail,
    Sandbox,
    SupplierDetails,
    SubscriptionPlan,
    PaymentHistory,
)
from ..paypal_sdk import get_paypal_access_token
from ..xmlfiles.compliance import compliance_xml
from ..zatca_operations.zatca import Zatca
from .CompanyMixins import CompanyQuerysetMixin

logger = logging.getLogger(__name__)
