from rest_framework import serializers
from api.models.sustainability import SustainabilityScore

class SustainabilityScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SustainabilityScore
        fields = [
            'economic_score',
            'environmental_score',
            'social_score',
            'total_score',
            'calculated_at'
        ]