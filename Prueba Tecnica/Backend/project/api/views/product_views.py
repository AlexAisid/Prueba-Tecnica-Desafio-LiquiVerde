from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from api.models.product import Product
from api.serializers import ProductSerializer, ProductListSerializer
from api.services.openfoodfacts import openfoodfacts_service


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de productos.
    
    Endpoints:
    - GET /api/products/ - Lista todos los productos
    - GET /api/products/{id}/ - Detalle de un producto
    - GET /api/products/search/ - Búsqueda de productos
    - GET /api/products/{id}/alternatives/ - Alternativas a un producto
    - POST /api/products/scan/ - Escanear código de barras
    """
    queryset = Product.objects.all().select_related('sustainability')
    serializer_class = ProductSerializer
    
    def get_serializer_class(self):
        """Usa serializer ligero para listas"""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Filtrado de productos"""
        queryset = super().get_queryset()
        
        # Filtros desde query params
        category = self.request.query_params.get('category', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        min_score = self.request.query_params.get('min_score', None)
        is_organic = self.request.query_params.get('is_organic', None)
        is_local = self.request.query_params.get('is_local', None)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if min_price:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        
        if min_score:
            queryset = queryset.filter(sustainability__total_score__gte=float(min_score))
        
        if is_organic == 'true':
            queryset = queryset.filter(is_organic=True)
        
        if is_local == 'true':
            queryset = queryset.filter(is_local=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Búsqueda de productos por texto.
        
        Query params:
        - q: texto de búsqueda
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Parámetro "q" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar en base de datos local
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__icontains=query)
        ).select_related('sustainability')[:20]
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'count': products.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def alternatives(self, request, pk=None):
        """
        Obtiene productos alternativos similares.
        
        Busca productos en la misma categoría con mejor precio o score.
        """
        product = self.get_object()
        
        # Buscar alternativas en la misma categoría
        alternatives = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        ).select_related('sustainability')
        
        # Filtrar por precio similar o mejor
        max_price = float(product.price) * 1.2  # Hasta 20% más caro
        alternatives = alternatives.filter(price__lte=max_price)
        
        # Ordenar por score de sostenibilidad
        alternatives = alternatives.order_by('-sustainability__total_score')[:5]
        
        serializer = ProductListSerializer(alternatives, many=True)
        
        return Response({
            'product': ProductSerializer(product).data,
            'alternatives': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def scan(self, request):
        """
        Escanea un código de barras y busca el producto.
        
        Body:
        {
            "barcode": "7802900000001"
        }
        
        Primero busca en la base de datos local, si no encuentra,
        busca en Open Food Facts.
        """
        barcode = request.data.get('barcode', '')
        
        if not barcode:
            return Response(
                {'error': 'Código de barras es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar en base de datos local
        try:
            product = Product.objects.select_related('sustainability').get(barcode=barcode)
            serializer = ProductSerializer(product)
            
            return Response({
                'found': True,
                'source': 'local',
                'product': serializer.data
            })
        except Product.DoesNotExist:
            pass
        
        # Buscar en Open Food Facts
        product_data = openfoodfacts_service.get_product_by_barcode(barcode)
        
        if product_data:
            return Response({
                'found': True,
                'source': 'openfoodfacts',
                'product': product_data,
                'message': 'Producto encontrado en Open Food Facts. Puede agregarlo a la base de datos.'
            })
        
        return Response({
            'found': False,
            'message': 'Producto no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)