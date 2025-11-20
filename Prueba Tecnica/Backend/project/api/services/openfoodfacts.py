"""
Servicio de integración con Open Food Facts API

Proporciona funciones para buscar y obtener información de productos
desde la API pública de Open Food Facts.
"""

import requests
from typing import Optional, Dict, List, Any


class OpenFoodFactsService:
    """Servicio para interactuar con la API de Open Food Facts"""
    
    BASE_URL = "https://world.openfoodfacts.org"
    API_VERSION = "api/v2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LiquiVerde/1.0 (Tech Test Application)',
        })
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un producto por su código de barras.
        
        Args:
            barcode: Código de barras del producto (EAN-13)
            
        Returns:
            dict: Información del producto o None si no se encuentra
        """
        try:
            url = f"{self.BASE_URL}/api/v0/product/{barcode}.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1:  # Producto encontrado
                    return self._parse_product_data(data.get('product', {}))
                
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar producto {barcode}: {e}")
            return None
    
    def search_products(self, query: str, page: int = 1, page_size: int = 20, country: str = 'chile') -> Dict[str, Any]:
        """
        Busca productos por texto.
        
        Args:
            query: Texto de búsqueda
            page: Número de página (default: 1)
            page_size: Cantidad de resultados por página (default: 20)
            country: País para filtrar (default: 'chile')
            
        Returns:
            dict: Resultados de búsqueda con paginación
        """
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/search"
            params = {
                'search_terms': query,
                'page': page,
                'page_size': page_size,
                'countries_tags_en': country,
                'sort_by': 'popularity',
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                products = [
                    self._parse_product_data(product)
                    for product in data.get('products', [])
                ]
                
                return {
                    'products': products,
                    'count': data.get('count', 0),
                    'page': data.get('page', 1),
                    'page_size': data.get('page_size', page_size),
                    'total_pages': (data.get('count', 0) + page_size - 1) // page_size,
                }
            
            return {
                'products': [],
                'count': 0,
                'page': 1,
                'page_size': page_size,
                'total_pages': 0,
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar productos: {e}")
            return {
                'products': [],
                'count': 0,
                'page': 1,
                'page_size': page_size,
                'total_pages': 0,
            }
    
    def _parse_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea los datos de un producto de Open Food Facts al formato interno.
        
        Args:
            product: Diccionario con datos del producto de la API
            
        Returns:
            dict: Datos del producto en formato estandarizado
        """
        # Extraer información básica
        barcode = product.get('code', '')
        name = product.get('product_name', '') or product.get('product_name_es', '') or 'Producto sin nombre'
        brand = product.get('brands', '') or 'Sin marca'
        
        # Categoría (simplificada)
        categories = product.get('categories_tags', [])
        category = self._map_category(categories)
        
        # Precio (Open Food Facts no tiene precios, asignar uno por defecto)
        # En producción, esto debería venir de otra fuente
        price = 0
        
        # Peso
        quantity = product.get('quantity', '')
        weight = self._extract_weight(quantity)
        
        # Nutri-Score
        nutriscore = product.get('nutriscore_grade', '').upper() or None
        
        # Eco-Score
        ecoscore = product.get('ecoscore_grade', '').upper() or None
        
        # Origen
        origin = product.get('origins', '') or product.get('manufacturing_places', '') or 'Desconocido'
        
        # Certificaciones
        labels = product.get('labels_tags', [])
        is_organic = any('organic' in label.lower() for label in labels)
        is_fairtrade = any('fair-trade' in label.lower() for label in labels)
        
        # Imagen
        image_url = product.get('image_url', '') or product.get('image_front_url', '')
        
        # Descripción
        description = product.get('ingredients_text_es', '') or product.get('ingredients_text', '')
        
        return {
            'barcode': barcode,
            'name': name,
            'brand': brand,
            'category': category,
            'price': price,
            'weight': weight,
            'unit': 'g',
            'nutriscore': nutriscore,
            'ecoscore': ecoscore,
            'origin': origin,
            'is_organic': is_organic,
            'is_fairtrade': is_fairtrade,
            'is_local': 'chile' in origin.lower() or 'chileno' in origin.lower(),
            'image_url': image_url,
            'description': description[:500] if description else None,  # Limitar a 500 caracteres
        }
    
    def _map_category(self, categories_tags: List[str]) -> str:
        """
        Mapea las categorías de Open Food Facts a nuestras categorías internas.
        
        Args:
            categories_tags: Lista de tags de categorías
            
        Returns:
            str: Categoría mapeada
        """
        category_mapping = {
            'grains': 'granos',
            'cereals': 'granos',
            'rice': 'granos',
            'pasta': 'granos',
            'dairies': 'lacteos',
            'milk': 'lacteos',
            'cheese': 'lacteos',
            'yogurt': 'lacteos',
            'meat': 'carnes',
            'poultry': 'carnes',
            'fish': 'carnes',
            'seafood': 'carnes',
            'fruits': 'frutas',
            'vegetables': 'frutas',
            'beverages': 'bebidas',
            'drinks': 'bebidas',
            'juices': 'bebidas',
            'water': 'bebidas',
            'snacks': 'snacks',
            'chips': 'snacks',
            'cookies': 'snacks',
            'bread': 'panaderia',
            'bakery': 'panaderia',
            'cleaning': 'limpieza',
        }
        
        for tag in categories_tags:
            tag_lower = tag.lower()
            for key, value in category_mapping.items():
                if key in tag_lower:
                    return value
        
        return 'otros'
    
    def _extract_weight(self, quantity_str: str) -> int:
        """
        Extrae el peso en gramos de una cadena de cantidad.
        
        Args:
            quantity_str: String con la cantidad (ej: "500g", "1kg", "1.5l")
            
        Returns:
            int: Peso en gramos
        """
        if not quantity_str:
            return 0
        
        # Limpiar string
        quantity_str = quantity_str.lower().strip()
        
        # Buscar patrones comunes
        import re
        
        # Gramos
        match = re.search(r'(\d+(?:\.\d+)?)\s*g', quantity_str)
        if match:
            return int(float(match.group(1)))
        
        # Kilogramos
        match = re.search(r'(\d+(?:\.\d+)?)\s*kg', quantity_str)
        if match:
            return int(float(match.group(1)) * 1000)
        
        # Litros (asumir 1L = 1000g)
        match = re.search(r'(\d+(?:\.\d+)?)\s*l', quantity_str)
        if match:
            return int(float(match.group(1)) * 1000)
        
        # Mililitros
        match = re.search(r'(\d+(?:\.\d+)?)\s*ml', quantity_str)
        if match:
            return int(float(match.group(1)))
        
        return 0


# Instancia global del servicio
openfoodfacts_service = OpenFoodFactsService()