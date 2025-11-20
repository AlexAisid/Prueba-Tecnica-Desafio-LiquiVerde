from rest_framework import serializers
from api.models.product import Product
from api.serializers.sustainability import SustainabilityScoreSerializer

class ProductSerializer(serializers.ModelSerializer):
    sustainability = SustainabilityScoreSerializer(read_only=True)
    price_per_unit = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'barcode',
            'name',
            'brand',
            'category',
            'price',
            'weight',
            'unit',
            'nutriscore',
            'ecoscore',
            'origin',
            'is_organic',
            'is_fairtrade',
            'is_local',
            'image_url',
            'description',
            'price_per_unit',
            'sustainability',
            'created_at',
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listas"""
    sustainability_score = serializers.FloatField(
        source='sustainability.total_score',
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'brand',
            'category',
            'price',
            'weight',
            'nutriscore',
            'ecoscore',
            'sustainability_score',
            'image_url',
        ]