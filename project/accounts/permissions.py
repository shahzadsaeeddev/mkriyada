
from rest_framework.permissions import BasePermission
from .models import Users


class HasRolesManager(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        return request.user.is_manager

# class HasUserRols(BasePermission):
#     """
#     Check if the user has any of the required AMP Roles
#     """
#
#     message = (
#         "You do not have any Assets Management Roles, "
#         "Please contact Keycloak Administrator to add roles into your Keycloak Account"
#     )
#
#     def has_permission(self, request, view):
#         if request.method == 'POST':
#             return request.user.is_create
#         elif request.method in ['PUT', 'PATCH', 'DELETE']:
#             return request.user.is_manage
#         elif request.method == 'GET':
#             return request.user.is_view
#         return False


class HasAdminDashboardRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_admin_dashboard

        return False



class HasUserDashboardRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_user_dashboard

        return False



class HasAnalyticsRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_analytics

        return False


class HasInvoicesRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_invoices
        elif request.method == 'POST':
            return request.user.is_create_invoices

        return False



class HasSaleRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_sale
        elif request.method == 'POST':
            return request.user.is_create_sale

        return False



class HasCreditNotesRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_credit_note
        elif request.method == 'POST':
            return request.user.is_create_credit_note

        return False



class HasDebitNoteRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_debit_note
        elif request.method == 'POST':
            return request.user.is_create_debit_note

        return False



class HasCustomerRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_create_customer
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_manage_customer
        elif request.method == 'GET':
            return request.user.is_view_customer

        return False

class HasProductsRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_create_product
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_manage_product
        elif request.method == 'GET':
            return request.user.is_view_product

        return False



class HasUmoRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_create_umo
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_manage_umo
        elif request.method == 'GET':
            return request.user.is_view_umo

        return False


class HasCategoryRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_create_category
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_manage_category
        elif request.method == 'GET':
            return request.user.is_view_category

        return False


class HasReportRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_report

        return False

class HasSubscribersRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_subscribers

        return False



class HasCompanyRole(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_company
        elif request.method in ['PUT', 'PATCH']:
            return request.user.is_manage_company

        return False


class HasPlanRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_create_plan
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_manage_plan
        elif request.method == 'GET':
            return request.user.is_view_plan

        return False



class HasCredentialsRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method in ['GET', 'POST']:
            return request.user.is_view_credentials

        return False


class HasPaymentRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_view_payment_history

        return False


class HasUsersRole(BasePermission):
    """
       Check if the user has any of the required AMP Roles
       """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_create_user
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_manage_user
        elif request.method == 'GET':
            return request.user.is_view_user

        return False



class HasAdminReportsRole(BasePermission):
    """
          Check if the user has any of the required AMP Roles
          """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_admin_reports

        return False

