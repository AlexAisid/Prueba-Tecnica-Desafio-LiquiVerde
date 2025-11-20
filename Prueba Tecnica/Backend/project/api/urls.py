from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.product_views import ProductViewSet
from api.views.shopping_views import ShoppingListViewSet
from api.views.stats_views import StatsViewSet

# Crear router
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'shopping-lists', ShoppingListViewSet, basename='shopping-list')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]