from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models.shopping import ShoppingList, ShoppingListItem
from api.models.product import Product
from api.serializers.shopping_serializer import (
    ShoppingListSerializer,
    ShoppingListItemSerializer,
)
from api.algorithms.knapsack import knapsack_multi_objective


class ShoppingListViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de listas de compras.
    
    Endpoints:
    - GET /api/shopping-lists/ - Lista todas las listas
    - POST /api/shopping-lists/ - Crea una nueva lista
    - GET /api/shopping-lists/{id}/ - Detalle de una lista
    - POST /api/shopping-lists/{id}/add-item/ - Agrega item a lista
    - DELETE /api/shopping-lists/{id}/remove-item/ - Elimina item de lista
    - POST /api/shopping-lists/optimize/ - Optimiza una lista de compras
    """
    queryset = ShoppingList.objects.all().prefetch_related('items__product__sustainability')
    serializer_class = ShoppingListSerializer
    
    def create(self, request, *args, **kwargs):
        """Crea una nueva lista de compras"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Agrega un item a la lista de compras.
        
        Body:
        {
            "product_id": 1,
            "quantity": 2
        }
        """
        shopping_list = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'error': 'product_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si el item ya existe
        item, created = ShoppingListItem.objects.get_or_create(
            shopping_list=shopping_list,
            product=product,
            defaults={
                'quantity': quantity,
                'price_at_addition': product.price,
            }
        )
        
        if not created:
            # Si ya existe, actualizar cantidad
            item.quantity += quantity
            item.save()
        
        # Recalcular totales de la lista
        self._update_shopping_list_totals(shopping_list)
        
        serializer = ShoppingListItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """
        Elimina un item de la lista.
        
        Body:
        {
            "item_id": 1
        }
        """
        shopping_list = self.get_object()
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'error': 'item_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = ShoppingListItem.objects.get(
                id=item_id,
                shopping_list=shopping_list
            )
            item.delete()
            
            # Recalcular totales
            self._update_shopping_list_totals(shopping_list)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingListItem.DoesNotExist:
            return Response(
                {'error': 'Item no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def optimize(self, request):
        """
        Optimiza una lista de compras usando el algoritmo de mochila.
        
        Body:
        {
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2
                },
                ...
            ],
            "budget": 50000
        }
        """
        items_data = request.data.get('items', [])
        budget = request.data.get('budget')
        
        if not items_data:
            return Response(
                {'error': 'Lista de items es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not budget:
            return Response(
                {'error': 'Presupuesto es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Preparar datos para el algoritmo
        products_data = []
        for item in items_data:
            try:
                product = Product.objects.select_related('sustainability').get(
                    id=item['product_id']
                )
                
                sustainability_score = (
                    product.sustainability.total_score
                    if hasattr(product, 'sustainability')
                    else 50
                )
                
                products_data.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': item.get('quantity', 1),
                    'sustainability_score': sustainability_score,
                    'weight': product.weight,
                })
            except Product.DoesNotExist:
                continue
        
        # Ejecutar algoritmo de optimización
        result = knapsack_multi_objective(products_data, float(budget))
        
        return Response(result)
    
    def _update_shopping_list_totals(self, shopping_list):
        """Actualiza los totales calculados de una lista"""
        items = shopping_list.items.all().select_related('product__sustainability')
        
        total_price = sum(item.subtotal for item in items)
        total_items = sum(item.quantity for item in items)
        
        # Calcular promedio de score
        scores = [
            item.product.sustainability.total_score
            for item in items
            if hasattr(item.product, 'sustainability')
        ]
        average_score = sum(scores) / len(scores) if scores else 0
        
        shopping_list.total_price = total_price
        shopping_list.total_items = total_items
        shopping_list.average_score = average_score
        shopping_list.save()