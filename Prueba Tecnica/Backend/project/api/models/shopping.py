from django.db import models
from django.core.validators import MinValueValidator
from api.models.product import Product

class ShoppingList(models.Model):
    """Listas de compras del usuario"""
    
    name = models.CharField(max_length=255, default='Mi Lista')
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_optimized = models.BooleanField(default=False)
    
    # Totales calculados
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - ${self.total_price}"


class ShoppingListItem(models.Model):
    """Items individuales de una lista de compras"""
    
    shopping_list = models.ForeignKey(
        ShoppingList, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Información al momento de agregar
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['shopping_list', 'product']
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calcular subtotal automáticamente"""
        self.subtotal = self.price_at_addition * self.quantity
        super().save(*args, **kwargs)