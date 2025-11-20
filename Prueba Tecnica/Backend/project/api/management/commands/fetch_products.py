"""
Comando para importar productos reales desde Open Food Facts API

Este script busca productos chilenos en diferentes categorías y los
importa a la base de datos con imágenes reales y precios estimados.

Uso:
    python manage.py fetch_products

Parámetros opcionales:
    --limit N : Número máximo de productos a importar (default: 200)
    --clear   : Limpiar productos existentes antes de importar
"""

from django.core.management.base import BaseCommand
from api.models.product import Product
from api.models.sustainability import SustainabilityScore
from api.algorithms.scoring import calculate_sustainability_scores
import requests
import random
import time
import json
from typing import Optional, Dict, List, Any


class OpenFoodFactsImporter:
    """Importador corregido"""
    
    BASE_URL = "https://world.openfoodfacts.org"
    
    def __init__(self, timeout=30, debug=False):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LiquiVerde/3.1 (Tech Test - Fixed Version)',
        })
        self.timeout = timeout
        self.debug = debug
        self.stats = {
            'api_calls': 0,
            'api_errors': 0,
            'retries': 0,
            'products_with_carbon': 0,
            'products_with_green': 0,
            'products_with_ecoscore': 0,
        }
    
    def search_products(self, query: str, page: int = 1, page_size: int = 50, country: str = 'chile', max_retries: int = 3) -> Dict[str, Any]:
        """Busca productos"""
        url = f"{self.BASE_URL}/api/v2/search"
        params = {
            'search_terms': query,
            'page': page,
            'page_size': page_size,
            'countries_tags_en': country,
            'sort_by': 'unique_scans_n',  # Ordenar por popularidad
            'fields': ','.join([
                'code', 'product_name', 'product_name_es', 'brands',
                'categories_tags', 'quantity', 'image_url', 'image_front_url',
                'nutriscore_grade', 'nutriscore_score',
                'ecoscore_grade', 'ecoscore_score', 'ecoscore_data',
                'origins', 'manufacturing_places', 'labels_tags',
                'ingredients_text_es', 'ingredients_text',
                # Datos ambientales
                'carbon_footprint_from_known_ingredients_100g',
                'climate_change_100g',
                'ecoscore_extended_data',
            ]),
        }
        
        for attempt in range(max_retries):
            try:
                self.stats['api_calls'] += 1
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    products = [self._parse_product_data(p) for p in data.get('products', [])]
                    
                    if self.debug and products:
                        print(f"\n[DEBUG] Ejemplo de producto recibido:")
                        print(f"  Nombre: {products[0]['name']}")
                        print(f"  Carbon: {products[0].get('carbon_footprint')}")
                        print(f"  Green: {products[0].get('green_score')}")
                        print(f"  Eco: {products[0].get('ecoscore')}")
                    
                    return {
                        'products': products,
                        'count': data.get('count', 0),
                        'page': data.get('page', 1),
                    }
                else:
                    raise Exception(f"Status code: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                self.stats['retries'] += 1
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                else:
                    self.stats['api_errors'] += 1
                    return {'products': [], 'count': 0, 'page': 1}
                    
            except Exception as e:
                self.stats['api_errors'] += 1
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    if self.debug:
                        print(f"[DEBUG] Error: {e}")
                    return {'products': [], 'count': 0, 'page': 1}
        
        return {'products': [], 'count': 0, 'page': 1}
    
    def _parse_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de Open Food Facts"""
        
        # Datos básicos
        barcode = product.get('code', '')
        name = product.get('product_name_es') or product.get('product_name', '') or 'Producto sin nombre'
        brand = product.get('brands', '').split(',')[0].strip() if product.get('brands') else 'Sin marca'
        
        categories = product.get('categories_tags', [])
        category = self._map_category(categories)
        
        quantity = product.get('quantity', '')
        weight = self._extract_weight(quantity)
        
        nutriscore = product.get('nutriscore_grade', '').upper() or None
        ecoscore = product.get('ecoscore_grade', '').upper() or None
        
        origin = product.get('origins', '') or product.get('manufacturing_places', '') or 'Desconocido'
        
        labels = product.get('labels_tags', [])
        is_organic = any('organic' in str(label).lower() for label in labels)
        is_fairtrade = any('fair' in str(label).lower() for label in labels)
        
        image_url = product.get('image_url', '') or product.get('image_front_url', '')
        description = product.get('ingredients_text_es', '') or product.get('ingredients_text', '')
        
        # DATOS CIENTÍFICOS
        carbon_footprint = None
        if product.get('climate_change_100g'):
            try:
                carbon_footprint = float(product['climate_change_100g']) * 1000  # kg a g
            except (ValueError, TypeError):
                pass
        elif product.get('carbon_footprint_from_known_ingredients_100g'):
            try:
                carbon_footprint = float(product['carbon_footprint_from_known_ingredients_100g'])
            except (ValueError, TypeError):
                pass
        
        environmental_impact_score = None
        ecoscore_extended = product.get('ecoscore_extended_data', {})
        if isinstance(ecoscore_extended, dict):
            if 'impact' in ecoscore_extended:
                environmental_impact_score = ecoscore_extended['impact'].get('ef_single_score_log_stddev')
        
        green_score = None
        if product.get('ecoscore_score'):
            try:
                green_score = int(product['ecoscore_score'])
            except (ValueError, TypeError):
                pass
        elif ecoscore:
            score_map = {'A': 90, 'B': 70, 'C': 50, 'D': 30, 'E': 10}
            green_score = score_map.get(ecoscore, 50)
        
        packaging_score = None
        if isinstance(ecoscore_extended, dict) and 'agribalyse' in ecoscore_extended:
            agribalyse_data = ecoscore_extended.get('agribalyse', {})
            if 'packaging_impact' in agribalyse_data:
                packaging_score = agribalyse_data['packaging_impact']
        
        ecoscore_data = None
        if product.get('ecoscore_data'):
            ecoscore_data = product['ecoscore_data']
        elif ecoscore_extended:
            ecoscore_data = ecoscore_extended
        
        data_source = 'openfoodfacts' if (carbon_footprint or green_score) else 'manual'
        
        return {
            'barcode': barcode,
            'name': name[:200],
            'brand': brand[:100],
            'category': category,
            'weight': weight,
            'unit': 'g',
            'nutriscore': nutriscore,
            'ecoscore': ecoscore,
            'origin': origin[:200] if origin else 'Desconocido',
            'is_organic': is_organic,
            'is_fairtrade': is_fairtrade,
            'is_local': 'chile' in origin.lower() if origin else False,
            'image_url': image_url,
            'description': description[:500] if description else None,
            'carbon_footprint': carbon_footprint,
            'environmental_impact_score': environmental_impact_score,
            'green_score': green_score,
            'packaging_score': packaging_score,
            'ecoscore_data': ecoscore_data,
            'data_source': data_source,
        }
    
    def record_stats(self, product):
        """Registra estadísticas SOLO cuando se importa exitosamente"""
        if product.carbon_footprint:
            self.stats['products_with_carbon'] += 1
        if product.green_score:
            self.stats['products_with_green'] += 1
        if product.ecoscore:
            self.stats['products_with_ecoscore'] += 1
    
    def _map_category(self, categories_tags: List[str]) -> str:
        """Mapea categorías a grupos simples de la app."""
        category_mapping = {
            # Granos / cereales / legumbres
            'rice': 'granos', 'arroz': 'granos',
            'grain': 'granos', 'grains': 'granos',
            'cereal': 'granos', 'cereales': 'granos',
            'pasta': 'granos', 'fideos': 'granos',
            'legume': 'granos', 'legumes': 'granos', 'legumbre': 'granos', 'legumbres': 'granos',

            # Lácteos
            'dairies': 'lacteos', 'dairy': 'lacteos',
            'milk': 'lacteos', 'milks': 'lacteos',
            'leche': 'lacteos',
            'cheese': 'lacteos', 'queso': 'lacteos',
            'yogurt': 'lacteos', 'yoghurt': 'lacteos',

            # Carnes / pescados
            'meat': 'carnes', 'meats': 'carnes',
            'carne': 'carnes', 'carnes': 'carnes',
            'poultry': 'carnes', 'pollo': 'carnes',
            'fish': 'carnes', 'pescado': 'carnes', 'pescados': 'carnes',
            'seafood': 'carnes', 'mariscos': 'carnes',

            # Frutas y verduras
            'fruit': 'frutas', 'fruits': 'frutas',
            'fruta': 'frutas', 'frutas': 'frutas',
            'vegetable': 'frutas', 'vegetables': 'frutas',
            'verdura': 'frutas', 'verduras': 'frutas',

            # Bebidas
            'beverage': 'bebidas', 'beverages': 'bebidas',
            'bebida': 'bebidas', 'bebidas': 'bebidas',
            'drink': 'bebidas', 'drinks': 'bebidas',
            'juice': 'bebidas', 'juices': 'bebidas',
            'zumo': 'bebidas', 'zumos': 'bebidas',
            'jugo': 'bebidas', 'jugos': 'bebidas',
            'smoothie': 'bebidas', 'smoothies': 'bebidas',

            # Aceites y condimentos
            'oil': 'aceites', 'aceite': 'aceites', 'aceites': 'aceites',
            'sauce': 'condimentos', 'sauces': 'condimentos',
            'salsa': 'condimentos', 'salsas': 'condimentos',

            # Snacks / dulces
            'snack': 'snacks', 'snacks': 'snacks',
            'cookie': 'snacks', 'cookies': 'snacks',
            'biscuit': 'snacks', 'biscuits': 'snacks',
            'chocolate': 'snacks',
            'chips': 'snacks',

            # Panadería
            'bread': 'panaderia', 'breads': 'panaderia',
            'pan': 'panaderia', 'bolleria': 'panaderia',
            'bakery': 'panaderia',
        }

        for tag in categories_tags:
            tag_lower = str(tag).lower()
            for key, value in category_mapping.items():
                if key in tag_lower:
                    return value

        return 'otros'


    
    def _extract_weight(self, quantity_str: str) -> int:
        """Extrae peso en gramos"""
        if not quantity_str:
            return 500
        
        import re
        quantity_str = str(quantity_str).lower().strip()
        
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*g(?:\s|$)', 1),
            (r'(\d+(?:\.\d+)?)\s*kg', 1000),
            (r'(\d+(?:\.\d+)?)\s*l(?:\s|$)', 1000),
            (r'(\d+(?:\.\d+)?)\s*ml', 1),
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, quantity_str)
            if match:
                return int(float(match.group(1)) * multiplier)
        
        return 500


class Command(BaseCommand):
    help = 'Importador CORREGIDO con mejor logging'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=200)
        parser.add_argument('--clear', action='store_true')
        parser.add_argument('--timeout', type=int, default=30)
        parser.add_argument('--debug', action='store_true', help='Modo debug con logs detallados')

    def handle(self, *args, **options):
        limit = options['limit']
        clear = options['clear']
        timeout = options['timeout']
        debug = options['debug']

        self.stdout.write(self.style.SUCCESS(f'\n{"="*70}'))
        self.stdout.write(self.style.SUCCESS(f'IMPORTACIÓN CORREGIDA - V3.1'))
        self.stdout.write(self.style.SUCCESS(f'{"="*70}'))
        self.stdout.write(f'📊 Límite: {limit} | Timeout: {timeout}s | Debug: {debug}')
        
        if clear:
            count = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'✓ Eliminados {count} productos\n'))

        importer = OpenFoodFactsImporter(timeout=timeout, debug=debug)
        
        # Buscar en categorías más amplias y múltiples páginas
        search_configs = [
            ('food', 'otros', 3, 40),  # 3 páginas de 40 = 120 intentos
            ('dairy', 'lacteos', 2, 40),
            ('beverage', 'bebidas', 2, 40),
            ('snack', 'snacks', 2, 30),
        ]

        products_imported = 0
        products_skipped = 0

        self.stdout.write(f'\n📦 Iniciando importación...\n')

        for search_term, category, num_pages, page_size in search_configs:
            if products_imported >= limit:
                break

            self.stdout.write(f'  → Buscando "{search_term}"...')
            
            for page in range(1, num_pages + 1):
                if products_imported >= limit:
                    break
                
                try:
                    result = importer.search_products(
                        query=search_term,
                        page=page,
                        page_size=page_size,
                        country='chile'
                    )

                    products_found = result.get('products', [])
                    self.stdout.write(f'    Página {page}: {len(products_found)} productos')

                    for product_data in products_found:
                        if products_imported >= limit:
                            break

                        if not product_data.get('name') or not product_data.get('barcode'):
                            continue

                        if Product.objects.filter(barcode=product_data['barcode']).exists():
                            products_skipped += 1
                            continue

                        price = self._estimate_price(product_data, category)

                        try:
                            product = Product.objects.create(
                                barcode=product_data['barcode'],
                                name=product_data['name'],
                                brand=product_data['brand'],
                                category=category,
                                price=price,
                                weight=product_data.get('weight', 0),
                                unit=product_data.get('unit', 'g'),
                                nutriscore=product_data.get('nutriscore'),
                                ecoscore=product_data.get('ecoscore'),
                                origin=product_data.get('origin', 'Chile'),
                                is_organic=product_data.get('is_organic', False),
                                is_fairtrade=product_data.get('is_fairtrade', False),
                                is_local=product_data.get('is_local', True),
                                image_url=product_data.get('image_url', ''),
                                description=product_data.get('description'),
                                carbon_footprint=product_data.get('carbon_footprint'),
                                environmental_impact_score=product_data.get('environmental_impact_score'),
                                green_score=product_data.get('green_score'),
                                packaging_score=product_data.get('packaging_score'),
                                ecoscore_data=product_data.get('ecoscore_data'),
                                data_source=product_data.get('data_source', 'manual'),
                            )

                            # CORREGIDO: Registrar stats DESPUÉS de crear
                            importer.record_stats(product)

                            scores = calculate_sustainability_scores(product)
                            SustainabilityScore.objects.create(
                                product=product,
                                economic_score=scores['economic_score'],
                                environmental_score=scores['environmental_score'],
                                social_score=scores['social_score'],
                                total_score=scores['total_score'],
                            )

                            products_imported += 1

                            if products_imported % 25 == 0:
                                self.stdout.write(f'    ✓ Progreso: {products_imported}/{limit}')

                        except Exception as e:
                            if debug:
                                self.stdout.write(f'    ⚠️  Error: {str(e)}')
                            continue

                    time.sleep(0.5)  # Pausa entre páginas

                except Exception as e:
                    self.stdout.write(f'    ✗ Error en página {page}: {str(e)[:50]}')
                    continue
            
            self.stdout.write(f'    ✓ Total importados de "{search_term}": {products_imported}')

        # Resumen
        self.stdout.write(self.style.SUCCESS(f'\n{"="*70}'))
        self.stdout.write(self.style.SUCCESS(f'RESUMEN'))
        self.stdout.write(self.style.SUCCESS(f'{"="*70}'))
        self.stdout.write(f'✓ Productos importados:       {products_imported}')
        self.stdout.write(f'⊘ Productos duplicados:       {products_skipped}')
        self.stdout.write(f'📊 Total en BD:               {Product.objects.count()}')
        self.stdout.write(f'\n🔬 DATOS CIENTÍFICOS:')
        self.stdout.write(f'   Con huella de carbono:     {importer.stats["products_with_carbon"]} ({importer.stats["products_with_carbon"]/max(products_imported, 1)*100:.1f}%)')
        self.stdout.write(f'   Con Green Score:           {importer.stats["products_with_green"]} ({importer.stats["products_with_green"]/max(products_imported, 1)*100:.1f}%)')
        self.stdout.write(f'   Con Eco-Score:             {importer.stats["products_with_ecoscore"]} ({importer.stats["products_with_ecoscore"]/max(products_imported, 1)*100:.1f}%)')
        self.stdout.write(self.style.SUCCESS(f'{"="*70}\n'))

        if products_imported > 0:
            products_with_carbon = Product.objects.filter(carbon_footprint__isnull=False)[:5]
            if products_with_carbon.exists():
                self.stdout.write('\n📊 Ejemplos con huella de carbono:')
                for p in products_with_carbon:
                    self.stdout.write(f'   • {p.name}: {p.carbon_footprint:.0f}g CO₂e/100g')
            
            self.stdout.write(self.style.SUCCESS('\n✓ Importación completada'))
        else:
            self.stdout.write(self.style.ERROR('\n⚠️  No se importaron productos'))

    def _estimate_price(self, product_data, category):
        """Estima precio"""
        weight = product_data.get('weight', 500)
        price_per_100g = {
            'granos': 150, 'lacteos': 200, 'carnes': 800, 'frutas': 300,
            'bebidas': 150, 'aceites': 500, 'condimentos': 200,
            'snacks': 400, 'panaderia': 250, 'otros': 300,
        }
        
        base_price = price_per_100g.get(category, 300)
        price = (weight / 100) * base_price if weight > 0 else base_price * 5
        
        if product_data.get('is_organic'):
            price *= 1.3
        if product_data.get('is_fairtrade'):
            price *= 1.2
        
        price *= random.uniform(0.9, 1.1)
        return max(500, int(round(price / 10) * 10))