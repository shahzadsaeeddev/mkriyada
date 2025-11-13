from django.urls import path
from rest_framework.routers import DefaultRouter

from .Views.Commons import *
from .Views.CompanyViews import *
from .Views.CustomerViews import *
from .Views.EgsLocations import *
from .Views.InvoicesViews import *
from .Views.PaypalViews import *
from .Views.ProductionViews import *
from .Views.SandboxViews import *
from .Views.SubscriptionViews import *
from .Views.SupplierViews import *
from .Views.DashboardViews import *
from .Views.InitTransactionViews import *
from .Views.ReportsViews import *