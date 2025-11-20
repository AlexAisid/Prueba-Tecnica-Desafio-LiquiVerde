from rest_framework import serializers
from api.models.product import Product
from api.serializers.sustainability_serializer import SustainabilityScoreSerializer

class ProductSerializer(serializers.ModelSerializer):
    """Serializer completo con todos los datos reales"""
    
    sustainability = SustainabilityScoreSerializer(read_only=True)
    
    # Campos calculados
    carbon_footprint_display = serializers.CharField(read_only=True)
    environmental_quality = serializers.CharField(read_only=True)
    has_real_data = serializers.BooleanField(source='has_real_environmental_data', read_only=True)
    
    # Detalles reales completos
    environmental_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            # Básicos
            'id',
            'barcode',
            'name',
            'brand',
            'category',
            'price',
            'weight',
            'unit',
            
            # Scores oficiales
            'nutriscore',
            'ecoscore',
            
            # Origen y certificaciones
            'origin',
            'is_organic',
            'is_fairtrade',
            'is_local',
            
            # Media
            'image_url',
            'description',
            
            # Datos reales
            'carbon_footprint',
            'carbon_footprint_display',
            'environmental_impact_score',
            'green_score',
            'packaging_score',
            'data_source',
            'environmental_quality',
            'has_real_data',
            
            # Sostenibilidad calculada
            'sustainability',
            
            # Detalles completos
            'environmental_data',
            
            # Timestamps
            'created_at',
            'updated_at',
        ]
    
    def get_environmental_data(self, obj):
        """
        Retorna información detallada sobre datos ambientales.
        
        Incluye:
        - Fuente de datos (real vs calculado)
        - Breakdown del score ambiental
        - Datos reales disponibles
        """
        data = {
            'source': obj.data_source,
            'has_real_data': obj.has_real_environmental_data,
            'quality': obj.environmental_quality,
        }
        
        # Datos reales disponibles
        if obj.carbon_footprint:
            data['carbon_footprint'] = {
                'value': obj.carbon_footprint,
                'display': obj.carbon_footprint_display,
                'source': 'Agribalyse (Open Food Facts)',
                'description': 'Huella de carbono basada en análisis de ciclo de vida completo'
            }
        
        if obj.green_score:
            data['green_score'] = {
                'value': obj.green_score,
                'max': 100,
                'source': 'Open Food Facts',
                'description': 'Score que considera producción, transporte, empaquetado y reciclaje'
            }
        
        if obj.ecoscore:
            data['ecoscore'] = {
                'grade': obj.ecoscore,
                'source': 'Open Food Facts',
                'description': 'Evaluación oficial del impacto ambiental (A=mejor, E=peor)'
            }
        
        if obj.environmental_impact_score:
            data['pef_score'] = {
                'value': obj.environmental_impact_score,
                'source': 'Product Environmental Footprint',
                'description': 'Puntuación de impacto ambiental del ciclo de vida completo'
            }
        
        # Si tenemos el JSON completo de ecoscore
        if obj.ecoscore_data:
            data['detailed_data_available'] = True
            data['ecoscore_details_url'] = f'/api/products/{obj.id}/ecoscore-details/'
        
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    
    sustainability_score = serializers.SerializerMethodField()
    
    # Datos básicos
    carbon_footprint_display = serializers.CharField(read_only=True)
    environmental_quality = serializers.CharField(read_only=True)
    has_real_data = serializers.BooleanField(source='has_real_environmental_data', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'barcode',
            'name',
            'brand',
            'category',
            'price',
            'image_url',
            'nutriscore',
            'ecoscore',
            'is_organic',
            'is_local',
            'sustainability_score',
            'carbon_footprint_display',
            'environmental_quality',
            'has_real_data',
        ]
    
    def get_sustainability_score(self, obj):
        if hasattr(obj, 'sustainability'):
            return obj.sustainability.total_score
        return None
    
class ProductDetailedEnvironmentalSerializer(serializers.ModelSerializer):
    """Serializer SOLO para datos ambientales detallados"""
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'carbon_footprint',
            'green_score',
            'environmental_impact_score',
            'packaging_score',
            'ecoscore_data',
            'data_source',
        ]

class EnrichedProductSerializer(ProductSerializer):
    """
    Serializer enriquecido que incluye comparaciones y contexto.
    
    Útil para mostrar al usuario qué tan bueno es el producto
    en comparación con alternativas.
    """
    
    category_average = serializers.SerializerMethodField()
    carbon_comparison = serializers.SerializerMethodField()
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'category_average',
            'carbon_comparison',
        ]
    
    def get_category_average(self, obj):
        """Score promedio de la categoría"""
        from django.db.models import Avg
        
        avg_score = Product.objects.filter(
            category=obj.category,
            sustainability__isnull=False
        ).aggregate(
            avg=Avg('sustainability__total_score')
        )['avg']
        
        if avg_score and hasattr(obj, 'sustainability'):
            return {
                'category_avg': round(avg_score, 1),
                'product_score': obj.sustainability.total_score,
                'difference': round(obj.sustainability.total_score - avg_score, 1),
                'better_than_average': obj.sustainability.total_score > avg_score
            }
        return None
    
    def get_carbon_comparison(self, obj):
        """Comparación de huella de carbono con promedio de categoría"""
        if not obj.carbon_footprint:
            return None
        
        from django.db.models import Avg
        
        avg_carbon = Product.objects.filter(
            category=obj.category,
            carbon_footprint__isnull=False
        ).aggregate(
            avg=Avg('carbon_footprint')
        )['avg']
        
        if avg_carbon:
            return {
                'product': obj.carbon_footprint,
                'category_avg': round(avg_carbon, 1),
                'percentage_vs_avg': round((obj.carbon_footprint / avg_carbon - 1) * 100, 1),
                'better_than_average': obj.carbon_footprint < avg_carbon,
                'description': self._get_carbon_description(obj.carbon_footprint)
            }
        return None
    
    def _get_carbon_description(self, carbon_footprint):
        """Descripción cualitativa de la huella de carbono"""
        if carbon_footprint < 100:
            return 'Huella de carbono muy baja - excelente para el ambiente'
        elif carbon_footprint < 300:
            return 'Huella de carbono baja - buena opción sustentable'
        elif carbon_footprint < 500:
            return 'Huella de carbono moderada'
        elif carbon_footprint < 1000:
            return 'Huella de carbono significativa'
        else:
            return 'Huella de carbono alta - considere alternativas más sustentables'