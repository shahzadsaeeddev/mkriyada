from rest_framework import serializers
from ..models import Company, PaymentHistory, SubscriptionPlan


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'details', 'price', 'support_level', 'number_of_users', 'invoice_limit']



class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        exclude = ['id', 'updated_at']


class SubscriptionPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        exclude = ['updated_at']



class SubscribersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        exclude = ['updated_at']