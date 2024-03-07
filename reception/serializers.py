from rest_framework import serializers
from dashboard.models import AddTailors, Add_order, Item


class TailorLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class AddOrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(source='customer_id.name')
    mobile = serializers.StringRelatedField(source='customer_id.mobile')
    class Meta:
        model = Add_order
        fields = '__all__'


class UpdateToInProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Add_order
        fields = ['id', 'status']


class InProgressOrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(source='customer_id.name')
    mobile = serializers.StringRelatedField(source='customer_id.mobile')

    class Meta:
        model = Add_order
        fields = '__all__'


class InProgressToCompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Add_order
        fields = ['id']


class CompletedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Add_order
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'