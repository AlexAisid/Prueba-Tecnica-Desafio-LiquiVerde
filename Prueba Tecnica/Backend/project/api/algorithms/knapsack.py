"""
Algoritmo de Mochila Multi-objetivo (Multi-objective Knapsack)

Este algoritmo optimiza una lista de compras considerando múltiples objetivos:
1. Maximizar valor nutricional/sostenibilidad
2. Minimizar costo total
3. Respetar presupuesto máximo

Usa programación dinámica con enfoque greedy adaptado para multi-criterio.
"""

from typing import List, Dict, Any
from decimal import Decimal


def calculate_product_value(price, weight, sustainability_score):
    """
    Calcula el "valor" de un producto considerando múltiples factores.
    
    Fórmula: valor = (score_sostenibilidad * peso_score) - (precio_normalizado * peso_precio)
    
    Args:
        price: Precio del producto
        weight: Peso del producto en gramos
        sustainability_score: Score de sostenibilidad del producto (0-100)
        
    Returns:
        float: Valor calculado del producto
    """
    # Normalizar precio (asumiendo rango de precios típicos)
    max_expected_price = 10000  # CLP
    normalized_price = min(float(price) / max_expected_price, 1.0)
    
    # Ponderaciones
    weight_sustainability = 0.7  # 70% sostenibilidad
    weight_price = 0.3          # 30% precio
    
    # Calcular valor (mayor sostenibilidad y menor precio = mayor valor)
    value = (
        (sustainability_score / 100) * weight_sustainability -
        normalized_price * weight_price
    )
    
    return value


def knapsack_multi_objective(products_data: List[Dict[str, Any]], budget: float) -> Dict[str, Any]:
    """
    Resuelve el problema de la mochila multi-objetivo para optimizar lista de compras.
    
    Args:
        products_data: Lista de diccionarios con información de productos
            Cada item debe tener:
            - product_id: ID del producto
            - name: Nombre del producto
            - price: Precio del producto
            - quantity: Cantidad deseada
            - sustainability_score: Score de sostenibilidad
            - weight: Peso del producto (opcional)
            
        budget: Presupuesto máximo disponible
        
    Returns:
        dict: Resultado de la optimización
    """
    
    if not products_data:
        return {
            'original_list': [],
            'optimized_list': [],
            'original_total': 0,
            'optimized_total': 0,
            'savings': 0,
            'savings_percentage': 0,
            'items_removed': 0,
            'items_kept': 0,
            'average_score_original': 0,
            'average_score_optimized': 0,
            'budget_used_percentage': 0,
        }
    
    # Calcular totales originales
    original_total = sum(item['price'] * item['quantity'] for item in products_data)
    original_avg_score = sum(item['sustainability_score'] for item in products_data) / len(products_data)
    
    # Si el total original está dentro del presupuesto, no hay nada que optimizar
    if original_total <= budget:
        return {
            'original_list': products_data,
            'optimized_list': products_data,
            'original_total': original_total,
            'optimized_total': original_total,
            'savings': 0,
            'savings_percentage': 0,
            'items_removed': 0,
            'items_kept': len(products_data),
            'average_score_original': original_avg_score,
            'average_score_optimized': original_avg_score,
            'budget_used_percentage': (original_total / budget * 100) if budget > 0 else 0,
        }
    
    # Calcular valor por peso (precio) para cada producto
    items_with_value = []
    for item in products_data:
        # Calcular valor usando precio, peso y score
        weight = item.get('weight', 1000)  # Default 1000g si no se especifica
        value_per_unit = calculate_product_value(
            item['price'],
            weight,
            item['sustainability_score']
        )
        
        # Valor total considerando cantidad
        total_value = value_per_unit * item['quantity']
        total_price = item['price'] * item['quantity']
        
        items_with_value.append({
            'product_id': item['product_id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'sustainability_score': item['sustainability_score'],
            'value_per_unit': value_per_unit,
            'total_value': total_value,
            'total_price': total_price,
            'value_to_price_ratio': total_value / total_price if total_price > 0 else 0
        })
    
    # ESTRATEGIA: Ordenar por mejor relación valor/precio
    items_sorted = sorted(
        items_with_value,
        key=lambda x: x['value_to_price_ratio'],
        reverse=True
    )
    
    # Selección greedy con programación dinámica simplificada
    optimized_list = []
    current_total = 0
    
    for item in items_sorted:
        # Intentar agregar el item completo
        if current_total + item['total_price'] <= budget:
            optimized_list.append({
                'product_id': item['product_id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'sustainability_score': item['sustainability_score'],
                'subtotal': item['total_price'],
            })
            current_total += item['total_price']
        else:
            # Intentar agregar cantidad parcial
            remaining_budget = budget - current_total
            max_quantity = int(remaining_budget // item['price'])
            
            if max_quantity > 0:
                optimized_list.append({
                    'product_id': item['product_id'],
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': max_quantity,
                    'sustainability_score': item['sustainability_score'],
                    'subtotal': item['price'] * max_quantity,
                })
                current_total += item['price'] * max_quantity
    
    # Calcular métricas finales
    optimized_total = sum(item['subtotal'] for item in optimized_list)
    optimized_avg_score = (
        sum(item['sustainability_score'] for item in optimized_list) / len(optimized_list)
        if optimized_list else 0
    )
    
    savings = original_total - optimized_total
    savings_percentage = (savings / original_total * 100) if original_total > 0 else 0
    
    return {
        'original_list': products_data,
        'optimized_list': optimized_list,
        'original_total': round(original_total, 2),
        'optimized_total': round(optimized_total, 2),
        'savings': round(savings, 2),
        'savings_percentage': round(savings_percentage, 2),
        'items_removed': len(products_data) - len(optimized_list),
        'items_kept': len(optimized_list),
        'average_score_original': round(original_avg_score, 2),
        'average_score_optimized': round(optimized_avg_score, 2),
        'budget_used_percentage': round((optimized_total / budget * 100), 2) if budget > 0 else 0,
    }


def optimize_by_substitution(products_data: List[Dict[str, Any]], all_products, budget: float) -> Dict[str, Any]:
    """
    Estrategia alternativa: optimizar mediante sustitución de productos.
    
    Busca alternativas más baratas o con mejor score en la misma categoría.
    
    Args:
        products_data: Lista de productos deseados
        all_products: QuerySet de todos los productos disponibles
        budget: Presupuesto máximo
        
    Returns:
        dict: Resultado con sustituciones sugeridas
    """
    from api.models.product import Product
    
    substitutions = []
    optimized_list = []
    current_total = 0
    
    for item in products_data:
        product_id = item.get('product_id')
        if not product_id:
            continue
            
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue
        
        # Buscar alternativas en la misma categoría
        alternatives = all_products.filter(
            category=product.category
        ).exclude(
            id=product.id
        ).select_related('sustainability')
        
        best_alternative = None
        best_score = -1
        
        for alt in alternatives:
            # Calcular score combinado (precio + sostenibilidad)
            price_score = 100 - min((float(alt.price) / float(product.price)) * 100, 100)
            sustainability_score = alt.sustainability.total_score if hasattr(alt, 'sustainability') else 50
            
            combined_score = (price_score * 0.5) + (sustainability_score * 0.5)
            
            # Solo considerar si es más barato o tiene mejor score
            if (alt.price < product.price or sustainability_score > item['sustainability_score']) and combined_score > best_score:
                best_alternative = alt
                best_score = combined_score
        
        # Decidir si usar el producto original o la alternativa
        if best_alternative and float(best_alternative.price) < float(product.price):
            subtotal = float(best_alternative.price) * item['quantity']
            
            if current_total + subtotal <= budget:
                substitutions.append({
                    'original': {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                    },
                    'substitute': {
                        'id': best_alternative.id,
                        'name': best_alternative.name,
                        'price': float(best_alternative.price),
                    },
                    'savings_per_unit': float(product.price) - float(best_alternative.price),
                })
                
                optimized_list.append({
                    'product_id': best_alternative.id,
                    'name': best_alternative.name,
                    'price': float(best_alternative.price),
                    'quantity': item['quantity'],
                    'sustainability_score': best_alternative.sustainability.total_score if hasattr(best_alternative, 'sustainability') else 50,
                    'subtotal': subtotal,
                    'is_substitution': True,
                })
                current_total += subtotal
        else:
            # Usar producto original si cabe en el presupuesto
            subtotal = item['price'] * item['quantity']
            if current_total + subtotal <= budget:
                optimized_list.append({
                    'product_id': item['product_id'],
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': item['quantity'],
                    'sustainability_score': item['sustainability_score'],
                    'subtotal': subtotal,
                    'is_substitution': False,
                })
                current_total += subtotal
    
    original_total = sum(item['price'] * item['quantity'] for item in products_data)
    optimized_total = sum(item['subtotal'] for item in optimized_list)
    
    return {
        'original_list': products_data,
        'optimized_list': optimized_list,
        'substitutions': substitutions,
        'original_total': round(original_total, 2),
        'optimized_total': round(optimized_total, 2),
        'savings': round(original_total - optimized_total, 2),
        'savings_percentage': round(((original_total - optimized_total) / original_total * 100), 2) if original_total > 0 else 0,
    }