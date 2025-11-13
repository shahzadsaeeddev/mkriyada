from rest_framework import serializers
from accounts.models import Users


class SubscriberSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="company.plan.name", read_only=True)
    phone = serializers.CharField(source="company.phone", read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'phone', 'plan_name']