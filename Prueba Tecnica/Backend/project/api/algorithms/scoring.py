"""
Sistema de Scoring de Sostenibilidad multi-criterio híbrido:

1. PRIORIZAR datos  reales de Open Food Facts (Agribalyse)
2. USAR fórmulas propias como FALLBACK cuando no hay datos reales
3. COMBINAR ambos para un score final robusto

"""
from typing import Dict


def calculate_environmental_score(product) -> Dict[str, any]:
    """
    Calcula score ambiental.
    
    PRIORIDAD:
    1. Datos reales de Open Food Facts / Agribalyse
    2. Fórmulas propias basadas en características del producto
    
    Returns:
        dict: {
            'score': float (0-100),
            'source': str ('real_data' | 'calculated' | 'hybrid'),
            'details': dict con breakdown
        }
    """
    
    # ============================================
    # OPCIÓN 1: USAR DATOS CIENTÍFICOS REALES
    # ============================================
    
    if product.has_real_environmental_data:
        return _calculate_from_real_data(product)
    
    # ============================================
    # OPCIÓN 2: CALCULAR CON FÓRMULAS PROPIAS
    # ============================================
    
    return _calculate_from_characteristics(product)


def _calculate_from_real_data(product) -> Dict:
    """
    Calcula score usando datos reales de Open Food Facts.
    
    Fuentes de datos:
    - Green Score (0-100) de Open Food Facts
    - Huella de carbono de Agribalyse
    - Eco-Score oficial
    """
    score = 0
    details = {}
    source = 'real_data'
    
    # 1. GREEN SCORE - 40%
    if product.green_score is not None:
        # Green Score ya está en escala 0-100
        green_contribution = product.green_score * 0.40
        score += green_contribution
        details['green_score'] = {
            'value': product.green_score,
            'contribution': green_contribution,
            'weight': '40%',
            'source': 'Open Food Facts'
        }
    
    # 2. HUELLA DE CARBONO (basado en Agribalyse) - 30%
    if product.carbon_footprint is not None:
        # Convertir huella de carbono a score (0-100)
        # Rangos típicos: 0-100g = Excelente, 100-500g = Bueno, 500-1000g = Medio, >1000g = Malo
        carbon_score = _carbon_footprint_to_score(product.carbon_footprint)
        carbon_contribution = carbon_score * 0.30
        score += carbon_contribution
        details['carbon_footprint'] = {
            'value': f'{product.carbon_footprint:.0f}g CO₂e/100g',
            'score': carbon_score,
            'contribution': carbon_contribution,
            'weight': '30%',
            'source': 'Agribalyse'
        }
    
    # 3. ECO-SCORE (letra A-E) - 20%
    if product.ecoscore:
        ecoscore_map = {'A': 100, 'B': 75, 'C': 50, 'D': 25, 'E': 10}
        ecoscore_score = ecoscore_map.get(product.ecoscore, 50)
        ecoscore_contribution = ecoscore_score * 0.20
        score += ecoscore_contribution
        details['ecoscore'] = {
            'grade': product.ecoscore,
            'score': ecoscore_score,
            'contribution': ecoscore_contribution,
            'weight': '20%',
            'source': 'Open Food Facts'
        }
    
    # 4. CARACTERÍSTICAS ADICIONALES - 10%
    bonus_score = 0
    if product.is_organic:
        bonus_score += 5
        details['organic_bonus'] = '+5 puntos'
    if product.is_local:
        bonus_score += 3
        details['local_bonus'] = '+3 puntos'
    if product.is_fairtrade:
        bonus_score += 2
        details['fairtrade_bonus'] = '+2 puntos'
    
    score += bonus_score * 0.10
    
    # Si solo tenemos datos parciales, marcar como híbrido
    has_green = product.green_score is not None
    has_carbon = product.carbon_footprint is not None
    has_eco = product.ecoscore is not None
    
    if not (has_green or has_carbon or has_eco):
        # No hay datos reales, usar fórmulas
        return _calculate_from_characteristics(product)
    
    if not (has_green and has_carbon and has_eco):
        source = 'hybrid'
        # Completar con datos calculados si faltan algunos
        if not has_green:
            calculated_score = _calculate_from_characteristics(product)
            missing_weight = 0.40 if not has_green else 0
            score += calculated_score['score'] * missing_weight
            details['calculated_component'] = f'{missing_weight*100}% calculado'
    
    return {
        'score': round(min(100, max(0, score)), 2),
        'source': source,
        'details': details
    }


def _calculate_from_characteristics(product) -> Dict:
    """
    Calcula score usando formulas propias basadas en características.
    
    Usado como fallback cuando no hay datos reales.
    """
    score = 0
    details = {}
    
    # NutriScore como proxy de calidad general (20 puntos)
    if product.nutriscore:
        nutriscore_map = {'A': 20, 'B': 15, 'C': 10, 'D': 5, 'E': 0}
        nutriscore_score = nutriscore_map.get(product.nutriscore, 10)
        score += nutriscore_score
        details['nutriscore'] = f'{product.nutriscore} ({nutriscore_score} pts)'
    
    # Eco-Score si está disponible (30 puntos)
    if product.ecoscore:
        ecoscore_map = {'A': 30, 'B': 23, 'C': 15, 'D': 8, 'E': 3}
        ecoscore_score = ecoscore_map.get(product.ecoscore, 15)
        score += ecoscore_score
        details['ecoscore'] = f'{product.ecoscore} ({ecoscore_score} pts)'
    
    # Orgánico (30 puntos)
    if product.is_organic:
        score += 30
        details['organic'] = '+30 pts (orgánico)'
    
    # Local (15 puntos)
    if product.is_local:
        score += 15
        details['local'] = '+15 pts (local)'
    
    # Comercio justo (5 puntos)
    if product.is_fairtrade:
        score += 5
        details['fairtrade'] = '+5 pts (comercio justo)'
    
    return {
        'score': round(min(100, max(0, score)), 2),
        'source': 'calculated',
        'details': details
    }


def _carbon_footprint_to_score(carbon_footprint: float) -> float:
    """
    Convierte huella de carbono (g CO2e/100g) a score 0-100.
    
    Rangos basados en estudios de Agribalyse:
    - 0-100g: Excelente (90-100 pts)
    - 100-300g: Muy bueno (70-90 pts)
    - 300-500g: Bueno (50-70 pts)
    - 500-1000g: Medio (30-50 pts)
    - 1000-2000g: Bajo (10-30 pts)
    - >2000g: Muy bajo (0-10 pts)
    """
    if carbon_footprint <= 100:
        return 90 + (100 - carbon_footprint) / 10
    elif carbon_footprint <= 300:
        return 70 + (300 - carbon_footprint) / 200 * 20
    elif carbon_footprint <= 500:
        return 50 + (500 - carbon_footprint) / 200 * 20
    elif carbon_footprint <= 1000:
        return 30 + (1000 - carbon_footprint) / 500 * 20
    elif carbon_footprint <= 2000:
        return 10 + (2000 - carbon_footprint) / 1000 * 20
    else:
        return max(0, 10 - (carbon_footprint - 2000) / 1000)


def calculate_economic_score(product) -> float:
    """
    Calcula score económico (relación calidad-precio).
    
    Criterios:
    - Precio por kilo
    - Calidad nutricional
    - Valor agregado (orgánico, certificaciones)
    """
    score = 0
    
    # Precio base (40 puntos) - inversamente proporcional
    if product.weight > 0:
        price_per_kg = float(product.price) / (product.weight / 1000)
        
        # Rangos típicos CLP por kg
        if price_per_kg < 2000:
            score += 40
        elif price_per_kg < 5000:
            score += 30
        elif price_per_kg < 10000:
            score += 20
        elif price_per_kg < 20000:
            score += 10
        else:
            score += 5
    
    # Nutri-Score (30 puntos) - mejor nutrición = mejor value
    if product.nutriscore:
        nutriscore_map = {'A': 30, 'B': 23, 'C': 15, 'D': 8, 'E': 3}
        score += nutriscore_map.get(product.nutriscore, 15)
    
    # Certificaciones añaden valor (30 puntos)
    if product.is_organic:
        score += 15
    if product.is_fairtrade:
        score += 10
    if product.is_local:
        score += 5
    
    return max(0, min(100, score))


def calculate_social_score(product) -> float:
    """
    Calcula score social (impacto en comunidades).
    
    Criterios:
    - Comercio justo
    - Producción local
    - Origen
    - Orgánico (condiciones laborales)
    """
    score = 0
    
    # Comercio justo (40 puntos)
    if product.is_fairtrade:
        score += 40
    
    # Producción local (30 puntos)
    if product.is_local:
        score += 30
    
    # Origen chileno (30 puntos adicionales si es local)
    if product.origin and 'Chile' in product.origin:
        score += 30
    
    # Orgánico (bonus 20 puntos - mejores condiciones laborales)
    if product.is_organic:
        score += 20
    
    return max(0, min(100, score))


def calculate_total_score(economic, environmental, social) -> float:
    """
    Calcula score total ponderado.
    
    Ponderaciones:
    - Económico: 30%
    - Ambiental: 40% (prioridad sostenibilidad)
    - Social: 30%
    """
    weights = {
        'economic': 0.30,
        'environmental': 0.40,
        'social': 0.30,
    }
    
    total = (
        economic * weights['economic'] +
        environmental * weights['environmental'] +
        social * weights['social']
    )
    
    return round(total, 2)


def calculate_sustainability_scores(product) -> Dict:
    """
    Calcula todos los scores de sostenibilidad.
    
    Usa sistema híbrido: datos reales cuando existen, fórmulas como fallback.
    
    Returns:
        dict: {
            'economic_score': float,
            'environmental_score': float,
            'environmental_details': dict,  # NUEVO: detalles del cálculo
            'social_score': float,
            'total_score': float,
            'data_quality': str  # 'real_data' | 'calculated' | 'hybrid'
        }
    """
    economic = calculate_economic_score(product)
    
    # Score ambiental CON detalles
    environmental_result = calculate_environmental_score(product)
    environmental = environmental_result['score']
    
    social = calculate_social_score(product)
    total = calculate_total_score(economic, environmental, social)
    
    return {
        'economic_score': round(economic, 2),
        'environmental_score': round(environmental, 2),
        'environmental_details': environmental_result,  # Incluye source y details
        'social_score': round(social, 2),
        'total_score': total,
        'data_quality': environmental_result['source'],
    }


def get_score_category(score: float) -> str:
    """Categoría textual del score"""
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