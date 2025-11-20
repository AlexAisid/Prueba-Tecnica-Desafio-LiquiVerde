from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models.product import Product
from api.models.sustainability import SustainabilityScore


class StatsViewSet(viewsets.ViewSet):
    """
    ViewSet para estadísticas generales.
    """
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Obtiene estadísticas generales del sistema.
        """
        from django.db.models import Avg, Count, Min, Max
        
        total_products = Product.objects.count()
        
        # Estadísticas de sostenibilidad
        sustainability_stats = SustainabilityScore.objects.aggregate(
            avg_total=Avg('total_score'),
            avg_economic=Avg('economic_score'),
            avg_environmental=Avg('environmental_score'),
            avg_social=Avg('social_score'),
        )
        
        # Estadísticas de precios
        price_stats = Product.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
        )
        
        # Productos por categoría
        products_by_category = Product.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_products': total_products,
            'sustainability_stats': sustainability_stats,
            'price_stats': price_stats,
            'products_by_category': list(products_by_category),
        })