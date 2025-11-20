from django.db import models
from decimal import Decimal


class Product(models.Model):
    """Modelo de Producto con datos reales de sostenibilidad"""
    
    # Información básica
    barcode = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100)
    
    # Precio y medidas
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.IntegerField(help_text="Peso en gramos")
    unit = models.CharField(max_length=10, default='g')
    
    # Scores oficiales (letras)
    nutriscore = models.CharField(max_length=1, null=True, blank=True)
    ecoscore = models.CharField(max_length=1, null=True, blank=True)
    
    # Origen y certificaciones
    origin = models.CharField(max_length=200, blank=True)
    is_organic = models.BooleanField(default=False)
    is_fairtrade = models.BooleanField(default=False)
    is_local = models.BooleanField(default=False)
    
    # Media
    image_url = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    
    # Huella de carbono
    carbon_footprint = models.FloatField(
        null=True,
        blank=True,
        help_text='Huella de carbono en g CO2e por 100g de producto (dato real de Open Food Facts / Agribalyse)'
    )
    
    # Environmental Impact Score (PEF - Product Environmental Footprint)
    environmental_impact_score = models.FloatField(
        null=True,
        blank=True,
        help_text='PEF score - Análisis de ciclo de vida completo (menor = mejor)'
    )
    
    # Green Score (0-100)
    green_score = models.IntegerField(
        null=True,
        blank=True,
        help_text='Green Score de 0-100 calculado por Open Food Facts (mayor = mejor)'
    )
    
    # Packaging Impact
    packaging_score = models.IntegerField(
        null=True,
        blank=True,
        help_text='Impacto del empaquetado calculado por Open Food Facts'
    )
    
    # Ecoscore
    ecoscore_data = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos completos del Eco-Score de Open Food Facts (JSON)'
    )
    
    # Origen de los datos
    data_source = models.CharField(
        max_length=50,
        default='manual',
        help_text='Origen: openfoodfacts, manual, hybrid'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return f"{self.name} ({self.brand})"
    
    @property
    def has_real_environmental_data(self):
        """Verifica si tiene datos reales de impacto ambiental"""
        return bool(
            self.carbon_footprint or 
            self.environmental_impact_score or 
            self.green_score
        )
    
    @property
    def environmental_quality(self):
        """Retorna categoría de calidad ambiental basada en datos reales"""
        if not self.has_real_environmental_data:
            return 'Desconocido'
        
        # Si tenemos Green Score (0-100, mayor = mejor)
        if self.green_score:
            if self.green_score >= 80:
                return 'Excelente'
            elif self.green_score >= 60:
                return 'Bueno'
            elif self.green_score >= 40:
                return 'Medio'
            elif self.green_score >= 20:
                return 'Bajo'
            else:
                return 'Muy Bajo'
        
        # Si tenemos Eco-Score
        if self.ecoscore:
            mapping = {'A': 'Excelente', 'B': 'Bueno', 'C': 'Medio', 'D': 'Bajo', 'E': 'Muy Bajo'}
            return mapping.get(self.ecoscore, 'Desconocido')
        
        return 'Desconocido'
    
    @property
    def carbon_footprint_display(self):
        """Retorna la huella de carbono formateada"""
        if self.carbon_footprint:
            return f"{self.carbon_footprint:.0f}g CO₂e/100g"
        return None