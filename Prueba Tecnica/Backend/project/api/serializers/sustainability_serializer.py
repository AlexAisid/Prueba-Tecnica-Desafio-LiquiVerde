from rest_framework import serializers
from api.models.sustainability import SustainabilityScore

class SustainabilityScoreSerializer(serializers.ModelSerializer):
    """Serializer para scores de sostenibilidad CON detalles"""
    
    # Campos calculados
    economic_category = serializers.SerializerMethodField()
    environmental_category = serializers.SerializerMethodField()
    social_category = serializers.SerializerMethodField()
    total_category = serializers.SerializerMethodField()
    
    # Origen de los datos
    data_quality = serializers.SerializerMethodField()
    
    class Meta:
        model = SustainabilityScore
        fields = [
            'economic_score',
            'economic_category',
            'environmental_score',
            'environmental_category',
            'social_score',
            'social_category',
            'total_score',
            'total_category',
            'data_quality',
        ]
    
    def get_economic_category(self, obj):
        return self._get_category(obj.economic_score)
    
    def get_environmental_category(self, obj):
        return self._get_category(obj.environmental_score)
    
    def get_social_category(self, obj):
        return self._get_category(obj.social_score)
    
    def get_total_category(self, obj):
        return self._get_category(obj.total_score)
    
    def get_data_quality(self, obj):
        """Indica si los datos son reales o calculados"""
        product = obj.product
        if product.has_real_environmental_data:
            if product.carbon_footprint and product.green_score:
                return 'real_data'
            else:
                return 'hybrid'
        return 'calculated'
    
    def _get_category(self, score):
        if score >= 80:
            return 'Excelente'
        elif score >= 60:
            return 'Bueno'
        elif score >= 40:
            return 'Medio'
        elif score >= 20:
            return 'Bajo'
        else:
            return 'Muy Bajo'