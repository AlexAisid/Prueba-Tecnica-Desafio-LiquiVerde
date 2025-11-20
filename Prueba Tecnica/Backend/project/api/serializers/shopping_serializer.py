from rest_framework import serializers
from api.serializers.product_serializer import ProductListSerializer
from api.models.shopping import ShoppingList, ShoppingListItem

class ShoppingListItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ShoppingListItem
        fields = [
            'id',
            'product',
            'product_id',
            'quantity',
            'price_at_addition',
            'subtotal',
        ]
        read_only_fields = ['subtotal']


class ShoppingListSerializer(serializers.ModelSerializer):
    items = ShoppingListItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = ShoppingList
        fields = [
            'id',
            'name',
            'budget',
            'is_optimized',
            'total_price',
            'total_items',
            'average_score',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['total_price', 'total_items', 'average_score']