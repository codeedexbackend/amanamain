from rest_framework import serializers
from .models import AddTailors,Customer

class TailorLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': False},
            'mobile': {'required': False},
            'length': {'required': False},
            'shoulder': {'required': False},
            'sleeve_length': {'required': False},
            'neck': {'required': False},
            'regal': {'required': False},
            'loose': {'required': False},
            'pocket': {'required': False},
            'cuff_length': {'required': False},
            'bottom1': {'required': False},
            'bottom2': {'required': False},
            'button_type': {'required': False},
            'delivery_date': {'required': False},
            'description': {'required': False},
        }


class CompletedCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'