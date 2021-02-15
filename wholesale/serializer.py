from re import match
from django.conf import settings
from wholesale.utils import get_last_created_file
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from wholesale.models import Product, Purchase


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseSerializer(ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


class PurchaseDetailedSerializer(ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Purchase
        fields = '__all__'


class RefillSerializer(Serializer):
    refill_count = serializers.IntegerField(min_value=1)

    class Meta:
        fields = ('refill_count')


class FilesSerializer(serializers.Serializer):
    file = serializers.FilePathField(path=settings.MEDIA_ROOT, match=get_last_created_file()[0])

    class Meta:
        fields = ['file',]


# class PurchaseCSVSerializer(Serializer):

#     class Meta:
#         fields = ('Product Id', 'Purchased Id', 'Purchased Qty', 'Product Name', 'Price Per Quantity')
