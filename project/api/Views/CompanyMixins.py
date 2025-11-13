from rest_framework.exceptions import PermissionDenied

class CompanyQuerysetMixin:
    def get_company(self):
        company = getattr(self.request, "company", None)
        user = getattr(self.request, "user", None)

        if company:
            return company

        if user and user.is_authenticated:
            if getattr(user, "company", None):
                return user.company

        raise PermissionDenied("Company not found or user not authorized.")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated and getattr(user, "user_roles", None) and user.user_roles.group_name == "Owner":
            return queryset

        company = self.get_company()
        return queryset.filter(company=company)

    def perform_create(self, serializer):
        user = self.request.user
        company = self.get_company()

        if user.is_authenticated and getattr(user, "user_roles", None) and user.user_roles.group_name == "Owner":
            serializer.save(company=user.company)
        else:
            serializer.save(company=company)
