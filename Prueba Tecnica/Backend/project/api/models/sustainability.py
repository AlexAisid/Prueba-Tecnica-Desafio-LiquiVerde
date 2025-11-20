from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from api.models.product import Product

class SustainabilityScore(models.Model):
    """Puntuaciones de sostenibilidad calculadas para cada producto"""
    
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE, 
        related_name='sustainability'
    )
    
    # Scores individuales (0-100)
    economic_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    environmental_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    social_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Score total ponderado
    total_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sustainability Score'
        verbose_name_plural = 'Sustainability Scores'
    
    def __str__(self):
        return f"{self.product.name} - Score: {self.total_score:.2f}"