# prueba-tecnica

Descripción General

Este proyecto consiste en una aplicación compuesta por un frontend en React + Vite (con mantine UI) y un backend en Python con Django, que integra algoritmos personalizados para optimización de selección (Knapsack) y cálculo de puntajes (Scoring) con el fin de procesar datos de productos recopilados con una api externa.

Tecnologías Utilizadas

Backend
Django 5.0.1 - Framework web
Django REST Framework 3.14.0 - API REST
SQLite - Base de datos
Requests - Cliente HTTP para APIs externas
Django CORS Headers - Manejo de CORS

Frontend

React 19.2.0 - Biblioteca UI
Vite 7.2.2 - Build tool y dev server
Mantine UI 7.15.2 - Sistema de componentes
React Router DOM 7.9.6 - Enrutamiento
Axios 1.13.2 - Cliente HTTP
Recharts 3.4.1 - Gráficos y visualizaciones
Tabler Icons - Iconografía

APIs Externas

Open Food Facts API - Datos de productos alimenticios
Agribalyse (vía Open Food Facts) - Datos de huella de carbono

La arquitectura está separada en:

project-frontend/ → Interfaz construida con React + Mantine

project-backend/ → API en Python con algoritmos ubicados en algorithms/

Despliegue local
creamos una carpeta con el nombre de Prueba Tecnica (o cualquier otro nombre) luego creamos dentro de ella las carpetas Frontend y Backend , para instalar el backend y el frontend, dare los pasos a continuación 
1. Frontend (React + Vite)
Instalación inicial
accedemos a la carpeta del frontend utilizando la terminal (o desde la carpeta anterior con cd Frontend)
utilizamos los siguientes comandos
npm create vite@latest project-frontend -- --template react
(nos saldrá  Use rolldown-vite (Experimental)?: y debemos poner no, luego saldra Install with npm and start now?
│  ● Yes / ○ No y debemos poner yes y esperamos a que se termine de instalar, al terminar se levantara el server y lo cerramos con ctrl + c )
luego ponemos en la terminal
cd project-frontend
y luego ejecutamos los siguientes comandos
npm install
npm install @mantine/core@7.15.2 @mantine/hooks@7.15.2 @mantine/notifications@7.15.2 @mantine/charts@7.15.2 @tabler/icons-react react-router-dom axios recharts

luego de esto podemos copiar el contenido de la carpeta Frontend que viene en github y esta remplazara algunos archivos recién creados pero también pondrá los archivos de las paginas
luego iniciamos el frontend con el siguiente comando
npm run dev

2. Backend (Python Django)
primero accedemos a la carpeta Backend en la terminal con cd backend
luego creamos el entorno virtual
py -3.11 -m venv venv
una vez hecho esto instalamos el contenido de la carpeta backend de github, en ella viene la carpeta project
ahora activamos el entorno
Windows:
venv\Scripts\activate
Linux/MacOS:
source venv/bin/activate
luego en la terminal accedemos a la carpeta projecto con cd project
y utilizamos el siguiente comando para instalar dependencias
pip install -r requirements.txt
luego ejecutamos el servidor de django

python manage.py runserver 

si no se ven productos pueden utilizar el siguiente comando para poblar la lista de productos

python manage.py fetch_products --limit 300 --clear

(el comando deberia estar en este nivel Prueba Tecnica\Backend\project> python manage.py fetch_products --limit 300 --clear)

Variables de entorno y Configuración

En el frontend estara el archivo .env que tendra lo siguiente:

.env
VITE_API_URL=http://localhost:8000

y el setting.py del backend que esta en github ya viene configurado

Explicación de Algoritmos

1. Mochila Multi-objetivo (Multi-objective Knapsack)
Ubicación: Backend/project/api/algorithms/knapsack.py
Descripción
Optimiza una lista de compras considerando múltiples objetivos simultáneamente:

Maximizar valor nutricional/sostenibilidad
Minimizar costo total
Respetar presupuesto máximo

Funcionamiento
El algoritmo utiliza una estrategia greedy con programación dinámica adaptada para criterios múltiples:

Cálculo de Valor por Producto:

valor = (score_sostenibilidad / 100) * 0.7 - (precio_normalizado) * 0.3

70% peso a la sostenibilidad
30% peso al precio (invertido, menor precio = mayor valor)


Ordenamiento: Los productos se ordenan por su relación valor/precio

ratio = valor_total / precio_total

Selección Greedy:

Selecciona productos en orden de mayor a menor ratio
Respeta el presupuesto máximo
Si un producto completo no cabe, intenta agregar cantidad parcial


Resultado:

Lista optimizada dentro del presupuesto
Cálculo de ahorros vs lista original
Mejora en score promedio de sostenibilidad



Ejemplo de Uso
from api.algorithms.knapsack import knapsack_multi_objective

products = [
    {
        'product_id': 1,
        'name': 'Arroz integral orgánico',
        'price': 2500,
        'quantity': 2,
        'sustainability_score': 85,
        'weight': 1000
    },
    # ... más productos
]

budget = 15000  # CLP

result = knapsack_multi_objective(products, budget)

result contiene:
- original_list: Lista original
- optimized_list: Lista optimizada
- savings: Ahorro en CLP
- savings_percentage: % de ahorro
- average_score_optimized: Score promedio mejorado

Complejidad

Tiempo: O(n log n) por el ordenamiento + O(n) para la selección greedy = O(n log n)
Espacio: O(n) para almacenar los productos ordenados


2. Sistema de Scoring de Sostenibilidad
Ubicación: Backend/project/api/algorithms/scoring.py
Descripción
Sistema híbrido que calcula scores de sostenibilidad priorizando datos científicos reales cuando están disponibles, y usando fórmulas propias como fallback.
Componentes del Score
El score total (0-100) se compone de tres dimensiones:

Score Económico (33.3%)

Relación precio/peso
Comparación con promedio de categoría



score_económico = 100 - min((precio / peso_kg) / precio_promedio * 100, 100)

Score Ambiental (33.3%) - Sistema Híbrido
A) Con Datos Reales de Open Food Facts:

    40% Green Score (Open Food Facts)
   green_contribution = green_score * 0.40
   
   30% Huella de Carbono (Agribalyse)
   carbon_score = 100 - min(carbon_footprint / 10, 100)
   carbon_contribution = carbon_score * 0.30
   
   20% Eco-Score (A=100, B=75, C=50, D=25, E=10)
   ecoscore_contribution = ecoscore_score * 0.20
   
    10% Bonificaciones (orgánico +5, local +3, comercio justo +2)
   bonus_contribution = bonus_points * 0.10
B) Sin Datos Reales (Fórmulas Propias):
    Basado en características del producto
   score = 50  # Base
   if is_organic: score += 15
   if is_local: score += 20
   if is_fairtrade: score += 10
    Ajuste por categoría
    Ajuste por empaquetado

Score Social (33.3%)

Certificaciones de comercio justo
Origen local/nacional
Prácticas laborales



Fórmula Final
total_score = (
    score_económico * 0.333 +
    score_ambiental * 0.333 +
    score_social * 0.334
)
Ventajas del Sistema Híbrido

Datos Reales: Cuando Open Food Facts tiene datos de Agribalyse (base de datos del gobierno francés), usa esos datos científicos
Fallback Inteligente: Si no hay datos reales, calcula usando características del producto
Transparencia: Indica la fuente de cada componente del score (real_data, calculated, hybrid)

Ejemplo de Resultado
json{
  "economic_score": 72.5,
  "environmental_score": 81.3,
  "environmental_details": {
    "score": 81.3,
    "source": "real_data",
    "details": {
      "green_score": {
        "value": 85,
        "contribution": 34.0,
        "weight": "40%",
        "source": "Open Food Facts"
      },
      "carbon_footprint": {
        "value": "120g CO₂e/100g",
        "score": 88,
        "contribution": 26.4,
        "weight": "30%",
        "source": "Agribalyse"
      }
    }
  },
  "social_score": 65.0,
  "total_score": 72.9,
  "data_quality": "real_data"
}

3. Sustitución Inteligente de Productos
Ubicación: Backend/project/api/algorithms/knapsack.py (función optimize_by_substitution)
Descripción
Busca alternativas más económicas o sostenibles dentro de la misma categoría de productos.
Algoritmo

Para cada producto en la lista:

Busca alternativas en la misma categoría
Excluye el producto original


Evaluación de alternativas:

    Score de precio (más barato = mejor)
   price_score = 100 - min((precio_alternativa / precio_original) * 100, 100)
   
    Score de sostenibilidad
   sustainability_score = alternativa.sustainability.total_score
   
    Score combinado (50% precio + 50% sostenibilidad)
   combined_score = (price_score * 0.5) + (sustainability_score * 0.5)

Selección:

Elige la alternativa con mejor score combinado
Solo si es más barata O más sostenible que el original
Verifica que quepa en el presupuesto


Resultado:

Lista de sustituciones realizadas
Ahorro total generado
Productos optimizados



Ejemplo
from api.algorithms.knapsack import optimize_by_substitution
from api.models.product import Product

products = [
    {
        'product_id': 1,
        'name': 'Leche entera marca premium',
        'price': 1500,
        'quantity': 2,
        'sustainability_score': 60
    }
]

all_products = Product.objects.all()
budget = 5000

result = optimize_by_substitution(products, all_products, budget)

 result contiene:
 - substitutions: [
     {
       'original': {'name': 'Leche entera marca premium', 'price': 1500},
       'substitute': {'name': 'Leche entera marca económica', 'price': 1100},
       'savings_per_unit': 400
     }
   ]
 - optimized_list: Lista con productos sustituidos
 - savings: 800 (2 unidades × 400 CLP)

Dataset de Productos
El proyecto incluye productos chilenos obtenidos de Open Food Facts, una base de datos colaborativa mundial de productos alimenticios.
Importación de Productos
Para poblar la base de datos con productos reales:
cd Backend/project
python manage.py fetch_products --limit 50
Parámetros disponibles:

--limit N: Número máximo de productos a importar (default: 200)
--clear: Limpiar productos existentes antes de importar

Uso de IA en este Proyecto

Este proyecto incorporó activamente herramientas de IA para aumentar la productividad y asegurar buenas prácticas de desarrollo.

Herramientas de IA Utilizadas
Durante el desarrollo de este proyecto, utilicé las siguientes herramientas de inteligencia artificial integradas en Visual Studio Code:

GitHub Copilot
Claude (Anthropic)

utilice la IA para las siguientes actividades 
1. Revisión de Documentación

Consulta rápida de sintaxis de Django, Django REST Framework
Búsqueda de mejores prácticas para configuración de Vite + React
Revisión de la documentación oficial de Mantine UI

2. Elaboración de Funciones y Componentes

Backend: Generación de funciones base para algoritmos (knapsack, scoring)
Frontend: Creación de componentes React con estructura inicial
Sugerencias de estructuras de datos eficientes
Implementación de serializers de Django REST Framework

3. Corrección de Errores de Código

Debugging de errores de importación y rutas en Django
Corrección de errores en llamadas a la API de Open Food Facts
Resolución de problemas de renderizado en componentes React

4. Revisión de Sintaxis y Estilo

Sugerencias de autocompletado inteligente en Python y JavaScript
Formateo consistente de código
Detección de código duplicado o ineficiente
Mejoras en la legibilidad del código

5. Documentación Rápida en el Código

Generación de docstrings en Python
Comentarios explicativos en funciones complejas
JSDoc para funciones JavaScript
Documentación de endpoints de la API

6. Planificación y Gestión del Tiempo

Creación de planes de desarrollo paso a paso
Estimación de tiempos para cada módulo
Priorización de funcionalidades

7. Guardado de Pasos del Desarrollo

Documentación de decisiones técnicas
Registro de problemas encontrados y soluciones aplicadas
Asistencia en la creación del README con toda la información del proyecto

Justificación del Uso de IA
El uso de estas herramientas de IA fue recomendado en mi anterior empresa como una práctica actual de desarrollo de software para:

Mejorar la productividad: Reducir tiempo en tareas repetitivas o de búsqueda de documentación
Acortar tiempos de desarrollo: Acelerar la implementación de funcionalidades estándar
Reducir errores: Detección temprana de bugs y problemas de sintaxis
Mejorar la calidad del código: Sugerencias de mejores prácticas y código más limpio
Facilitar el aprendizaje: Exploración rápida de nuevas tecnologías y frameworks

Transparencia
Es importante destacar que las estructuras de la app fueron hechas por mí, el diseño de algoritmos fue desarrollado con asistencia de la IA a pesar de que hice la estructura inicial, y también utilice estructuras de proyectos anteriores que he desarrollado para ahorrar un poco de tiempo ya que el desarrollo de esta prueba técnica lo lleve a cabo solo de noche, ya que de dia tenia que asistir a mi trabajo de medio tiempo que tengo temporalmente
