from django.core.management.base import BaseCommand
from api.models.product import Product
from api.models.sustainability import SustainabilityScore
from api.algorithms.scoring import calculate_sustainability_scores


class Command(BaseCommand):
    help = 'Pobla la base de datos con productos chilenos de ejemplo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando seed de productos...'))
        
        # Eliminar productos existentes si los hay
        Product.objects.all().delete()
        self.stdout.write(self.style.WARNING('Productos existentes eliminados'))
        
        products_data = [
            # GRANOS Y CEREALES
            {
                'barcode': '7802900000001',
                'name': 'Arroz Tucapel Grado 2',
                'brand': 'Tucapel',
                'category': 'granos',
                'price': 1590,
                'weight': 1000,
                'nutriscore': 'A',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Arroz+Tucapel',
                'description': 'Arroz grado 2, ideal para acompañamientos'
            },
            {
                'barcode': '7802900000002',
                'name': 'Fideos Carozzi Corbata',
                'brand': 'Carozzi',
                'category': 'granos',
                'price': 890,
                'weight': 400,
                'nutriscore': 'B',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Fideos+Carozzi',
                'description': 'Fideos corbata, perfectos para toda la familia'
            },
            {
                'barcode': '7802900000003',
                'name': 'Avena Quaker Tradicional',
                'brand': 'Quaker',
                'category': 'granos',
                'price': 2390,
                'weight': 1000,
                'nutriscore': 'A',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Avena+Quaker',
                'description': 'Avena tradicional, rica en fibra'
            },
            {
                'barcode': '7802900000004',
                'name': 'Lentejas Anita',
                'brand': 'Anita',
                'category': 'granos',
                'price': 1290,
                'weight': 500,
                'nutriscore': 'A',
                'ecoscore': 'A',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Lentejas+Anita',
                'description': 'Lentejas orgánicas, excelente fuente de proteína'
            },
            
            # LÁCTEOS
            {
                'barcode': '7802900000005',
                'name': 'Leche Colun Entera 1L',
                'brand': 'Colun',
                'category': 'lacteos',
                'price': 990,
                'weight': 1000,
                'nutriscore': 'B',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Leche+Colun',
                'description': 'Leche entera fresca'
            },
            {
                'barcode': '7802900000006',
                'name': 'Yogurt Natural Quillayes',
                'brand': 'Quillayes',
                'category': 'lacteos',
                'price': 1590,
                'weight': 1000,
                'nutriscore': 'A',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Yogurt+Quillayes',
                'description': 'Yogurt natural orgánico sin azúcar añadida'
            },
            {
                'barcode': '7802900000007',
                'name': 'Queso Gauda Colun',
                'brand': 'Colun',
                'category': 'lacteos',
                'price': 3490,
                'weight': 500,
                'nutriscore': 'C',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Queso+Colun',
                'description': 'Queso Gauda maduro'
            },
            
            # CARNES Y PROTEÍNAS
            {
                'barcode': '7802900000008',
                'name': 'Pechuga de Pollo Super Pollo',
                'brand': 'Super Pollo',
                'category': 'carnes',
                'price': 4990,
                'weight': 1000,
                'nutriscore': 'A',
                'ecoscore': 'D',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Pollo',
                'description': 'Pechuga de pollo fresca'
            },
            {
                'barcode': '7802900000009',
                'name': 'Atún Lomito San José',
                'brand': 'San José',
                'category': 'carnes',
                'price': 1890,
                'weight': 160,
                'nutriscore': 'B',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Atun+San+Jose',
                'description': 'Atún lomito en agua'
            },
            {
                'barcode': '7802900000010',
                'name': 'Huevos Codorniz x12',
                'brand': 'Codorniz',
                'category': 'carnes',
                'price': 2190,
                'weight': 600,
                'nutriscore': 'A',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Huevos',
                'description': 'Huevos orgánicos de gallinas libres'
            },
            
            # FRUTAS Y VERDURAS
            {
                'barcode': '7802900000011',
                'name': 'Tomate Fresco',
                'brand': 'Del Huerto',
                'category': 'frutas',
                'price': 1990,
                'weight': 1000,
                'nutriscore': 'A',
                'ecoscore': 'A',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Tomate',
                'description': 'Tomates frescos orgánicos'
            },
            {
                'barcode': '7802900000012',
                'name': 'Lechuga Hidropónica',
                'brand': 'Verde Fresco',
                'category': 'frutas',
                'price': 1290,
                'weight': 300,
                'nutriscore': 'A',
                'ecoscore': 'A',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Lechuga',
                'description': 'Lechuga hidropónica fresca'
            },
            {
                'barcode': '7802900000013',
                'name': 'Manzana Royal Gala',
                'brand': 'Frutas del Sur',
                'category': 'frutas',
                'price': 2490,
                'weight': 1000,
                'nutriscore': 'A',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Manzana',
                'description': 'Manzanas frescas Royal Gala'
            },
            
            # BEBIDAS
            {
                'barcode': '7802900000014',
                'name': 'Coca Cola 1.5L',
                'brand': 'Coca Cola',
                'category': 'bebidas',
                'price': 1590,
                'weight': 1500,
                'nutriscore': 'E',
                'ecoscore': 'D',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Coca+Cola',
                'description': 'Bebida gaseosa'
            },
            {
                'barcode': '7802900000015',
                'name': 'Jugo Natural Watt\'s Naranja',
                'brand': 'Watt\'s',
                'category': 'bebidas',
                'price': 1290,
                'weight': 1000,
                'nutriscore': 'C',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Jugo+Watts',
                'description': 'Jugo de naranja natural'
            },
            {
                'barcode': '7802900000016',
                'name': 'Agua Mineral Cachantun 1.5L',
                'brand': 'Cachantun',
                'category': 'bebidas',
                'price': 890,
                'weight': 1500,
                'nutriscore': 'A',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Cachantun',
                'description': 'Agua mineral natural'
            },
            
            # SNACKS
            {
                'barcode': '7802900000017',
                'name': 'Papas Fritas Marco Polo',
                'brand': 'Marco Polo',
                'category': 'snacks',
                'price': 990,
                'weight': 180,
                'nutriscore': 'D',
                'ecoscore': 'D',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Papas+Marco+Polo',
                'description': 'Papas fritas sabor original'
            },
            {
                'barcode': '7802900000018',
                'name': 'Galletas Tritón Soda',
                'brand': 'Costa',
                'category': 'snacks',
                'price': 690,
                'weight': 160,
                'nutriscore': 'C',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Triton',
                'description': 'Galletas de soda'
            },
            {
                'barcode': '7802900000019',
                'name': 'Frutos Secos Mix',
                'brand': 'Gvtarra',
                'category': 'snacks',
                'price': 2990,
                'weight': 250,
                'nutriscore': 'B',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': True,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Frutos+Secos',
                'description': 'Mix de frutos secos orgánicos y comercio justo'
            },
            
            # PANADERÍA
            {
                'barcode': '7802900000020',
                'name': 'Pan Integral Ideal',
                'brand': 'Ideal',
                'category': 'panaderia',
                'price': 1490,
                'weight': 500,
                'nutriscore': 'B',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Pan+Ideal',
                'description': 'Pan integral de molde'
            },
            {
                'barcode': '7802900000021',
                'name': 'Hallullas Artesanales',
                'brand': 'Panadería Local',
                'category': 'panaderia',
                'price': 990,
                'weight': 200,
                'nutriscore': 'C',
                'ecoscore': 'A',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Hallullas',
                'description': 'Hallullas artesanales frescas'
            },
            
            # ACEITES Y CONDIMENTOS
            {
                'barcode': '7802900000022',
                'name': 'Aceite Girasol Chef',
                'brand': 'Chef',
                'category': 'otros',
                'price': 2890,
                'weight': 900,
                'nutriscore': 'C',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Aceite+Chef',
                'description': 'Aceite de girasol'
            },
            {
                'barcode': '7802900000023',
                'name': 'Aceite de Oliva Malloa',
                'brand': 'Malloa',
                'category': 'otros',
                'price': 5990,
                'weight': 500,
                'nutriscore': 'B',
                'ecoscore': 'A',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Aceite+Malloa',
                'description': 'Aceite de oliva extra virgen orgánico'
            },
            {
                'barcode': '7802900000024',
                'name': 'Sal de Mar Lobos',
                'brand': 'Lobos',
                'category': 'otros',
                'price': 890,
                'weight': 1000,
                'nutriscore': 'C',
                'ecoscore': 'A',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Sal+Lobos',
                'description': 'Sal de mar natural'
            },
            
            # AZÚCAR Y ENDULZANTES
            {
                'barcode': '7802900000025',
                'name': 'Azúcar Iansa',
                'brand': 'Iansa',
                'category': 'otros',
                'price': 1290,
                'weight': 1000,
                'nutriscore': 'D',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Azucar+Iansa',
                'description': 'Azúcar refinada'
            },
            {
                'barcode': '7802900000026',
                'name': 'Miel Pura de Abeja',
                'brand': 'Apícola del Sur',
                'category': 'otros',
                'price': 4490,
                'weight': 500,
                'nutriscore': 'C',
                'ecoscore': 'A',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Miel',
                'description': 'Miel pura orgánica de producción local'
            },
            
            # PRODUCTOS ADICIONALES
            {
                'barcode': '7802900000027',
                'name': 'Café Instantáneo Nescafé',
                'brand': 'Nescafé',
                'category': 'bebidas',
                'price': 3990,
                'weight': 170,
                'nutriscore': 'B',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Nescafe',
                'description': 'Café instantáneo'
            },
            {
                'barcode': '7802900000028',
                'name': 'Té Verde Supremo',
                'brand': 'Supremo',
                'category': 'bebidas',
                'price': 1890,
                'weight': 40,
                'nutriscore': 'A',
                'ecoscore': 'B',
                'origin': 'Chile',
                'is_organic': True,
                'is_fairtrade': True,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Te+Supremo',
                'description': 'Té verde orgánico de comercio justo'
            },
            {
                'barcode': '7802900000029',
                'name': 'Mantequilla Colun',
                'brand': 'Colun',
                'category': 'lacteos',
                'price': 2490,
                'weight': 250,
                'nutriscore': 'D',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Mantequilla+Colun',
                'description': 'Mantequilla con sal'
            },
            {
                'barcode': '7802900000030',
                'name': 'Mermelada Watts Frutilla',
                'brand': 'Watts',
                'category': 'otros',
                'price': 1990,
                'weight': 500,
                'nutriscore': 'D',
                'ecoscore': 'C',
                'origin': 'Chile',
                'is_organic': False,
                'is_fairtrade': False,
                'is_local': True,
                'image_url': 'https://via.placeholder.com/200x200.png?text=Mermelada+Watts',
                'description': 'Mermelada de frutilla'
            },
        ]
        
        # Crear productos
        products_created = 0
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            products_created += 1
            
            # Calcular y guardar scores de sostenibilidad
            scores = calculate_sustainability_scores(product)
            SustainabilityScore.objects.create(
                product=product,
                **scores
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Creado: {product.name} (Score: {scores["total_score"]:.2f})')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n¡Seed completado! {products_created} productos creados con sus scores de sostenibilidad')
        )