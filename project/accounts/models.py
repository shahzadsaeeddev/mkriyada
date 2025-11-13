import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

from utility.modelMixins import TimeStampMixins


class RoleGroup(TimeStampMixins):
    group_name = models.CharField(max_length=50, blank=False, null=False)
    group_code = models.CharField(max_length=150, default="",blank=False, null=False)
    visible = models.BooleanField(default=False)
    company=models.ForeignKey("api.Company",blank=True, null=True, on_delete=models.CASCADE)


    def __str__(self):
        return self.group_name


class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    keycloak_uuid = models.CharField(max_length=136, blank=False, null=False)
    is_owner = models.BooleanField(default=False)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    user_roles = models.ForeignKey(RoleGroup, blank=True, null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey("api.Company", blank=True, null=True, on_delete=models.SET_NULL, related_name="users")
    application_roles = ArrayField(models.CharField(
        blank=True,
        null=True, max_length=50
    ),
        size=100, default=list
    )
    is_delete = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @property
    def is_manager(self):
        return "PERMISSIONS_CAN_LOGIN" in self.application_roles

    @property
    def is_admin_dashboard(self):
        return "PERMISSION_CAN_VIEW_ADMIN_DASHBOARD" in self.application_roles

    @property
    def is_user_dashboard(self):
        return "PERMISSION_CAN_VIEW_USER_DASHBOARD" in self.application_roles

    @property
    def is_view_dashboard(self):
        return "PERMISSION_CAN_VIEW_DASHBOARD" in self.application_roles

    @property
    def is_view_analytics(self):
        return "PERMISSION_CAN_VIEW_ANALYTICS" in self.application_roles

    @property
    def is_view_invoices(self):
        return "PERMISSION_CAN_VIEW_INVOICES" in self.application_roles

    @property
    def is_create_invoices(self):
        return "PERMISSION_CAN_CREATE_INVOICES" in self.application_roles

    @property
    def is_view_customer(self):
        return "PERMISSION_CAN_VIEW_CUSTOMER" in self.application_roles

    @property
    def is_create_customer(self):
        return "PERMISSION_CAN_CREATE_CUSTOMER" in self.application_roles

    @property
    def is_manage_customer(self):
        return "PERMISSION_CAN_MANAGE_CUSTOMER" in self.application_roles

    @property
    def is_view_product(self):
        return "PERMISSION_CAN_VIEW_PRODUCTS" in self.application_roles

    @property
    def is_create_product(self):
        return "PERMISSION_CAN_CREATE_PRODUCTS" in self.application_roles

    @property
    def is_manage_product(self):
        return "PERMISSION_CAN_MANAGE_PRODUCTS" in self.application_roles

    @property
    def is_view_sale(self):
        return "PERMISSION_CAN_VIEW_SALE" in self.application_roles

    @property
    def is_create_sale(self):
        return "PERMISSION_CAN_CREATE_SALE" in self.application_roles

    @property
    def is_view_credit_note(self):
        return "PERMISSION_CAN_VIEW_CREDIT_NOTE" in self.application_roles

    @property
    def is_create_credit_note(self):
        return "PERMISSION_CAN_CREATE_CREDIT_NOTE" in self.application_roles

    @property
    def is_view_debit_note(self):
        return "PERMISSION_CAN_VIEW_DEBIT_NOTE" in self.application_roles

    @property
    def is_create_debit_note(self):
        return "PERMISSION_CAN_CREATE_DEBIT_NOTE" in self.application_roles

    @property
    def is_view_umo(self):
        return "PERMISSION_CAN_VIEW_UOM" in self.application_roles

    @property
    def is_create_umo(self):
        return "PERMISSION_CAN_CREATE_UOM" in self.application_roles

    @property
    def is_manage_umo(self):
        return "PERMISSION_CAN_MANAGE_UOM" in self.application_roles

    @property
    def is_view_category(self):
        return "PERMISSION_CAN_VIEW_CATEGORY" in self.application_roles

    @property
    def is_create_category(self):
        return "PERMISSION_CAN_CREATE_CATEGORY" in self.application_roles

    @property
    def is_manage_category(self):
        return "PERMISSION_CAN_MANAGE_CATEGORY" in self.application_roles

    @property
    def is_view_report(self):
        return "PERMISSION_CAN_VIEW_REPORTS" in self.application_roles

    @property
    def is_admin_reports(self):
        return "PERMISSION_CAN_VIEW_ADMIN_REPORTS" in self.application_roles

    @property
    def is_view_subscribers(self):
        return "PERMISSION_CAN_VIEW_SUBSCRIBERS" in self.application_roles


    @property
    def is_view_company(self):
        return "PERMISSION_CAN_VIEW_COMPANY_INFO" in self.application_roles

    @property
    def is_manage_company(self):
        return "PERMISSION_CAN_MANAGE_COMPANY_INFO" in self.application_roles


    @property
    def is_view_plan(self):
        return "PERMISSION_CAN_VIEW_PLAN" in self.application_roles

    @property
    def is_create_plan(self):
        return "PERMISSION_CAN_CREATE_PLAN" in self.application_roles

    @property
    def is_manage_plan(self):
        return "PERMISSION_CAN_MANAGE_PLAN" in self.application_roles

    @property
    def is_view_credentials(self):
        return "PERMISSION_CAN_VIEW_CREDENTIALS" in self.application_roles

    @property
    def is_view_user(self):
        return "PERMISSION_CAN_VIEW_USERS" in self.application_roles

    @property
    def is_create_user(self):
        return "PERMISSION_CAN_CREATE_USERS" in self.application_roles

    @property
    def is_manage_user(self):
        return "PERMISSION_CAN_MANAGE_USERS" in self.application_roles

    @property
    def is_view_payment_history(self):
        return "PERMISSION_CAN_VIEW_PAYMENT_HISTORY" in self.application_roles






