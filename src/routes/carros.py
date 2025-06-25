from flask import Blueprint, jsonify, request
import requests

carros_bp = Blueprint('carros', __name__)

# Lista de marcas populares (pode ser expandida)
MARCAS_POPULARES = [
    'Chevrolet', 'Volkswagen', 'Fiat', 'Ford', 'Hyundai', 'Toyota', 'Honda', 
    'Nissan', 'Renault', 'Peugeot', 'Citroën', 'Jeep', 'BMW', 'Mercedes-Benz', 
    'Audi', 'Volvo', 'Mitsubishi', 'Kia', 'Suzuki', 'Subaru'
]

# Dicionário de modelos por marca (versão simplificada)
MODELOS_POR_MARCA = {
    'Chevrolet': ['Onix', 'Prisma', 'Cruze', 'Tracker', 'Equinox', 'S10', 'Spin', 'Cobalt', 'Celta', 'Corsa'],
    'Volkswagen': ['Gol', 'Polo', 'Virtus', 'T-Cross', 'Tiguan', 'Amarok', 'Fox', 'Up!', 'Jetta', 'Passat'],
    'Fiat': ['Uno', 'Argo', 'Cronos', 'Mobi', 'Toro', 'Strada', 'Pulse', 'Fastback', 'Palio', 'Siena'],
    'Ford': ['Ka', 'Fiesta', 'Focus', 'EcoSport', 'Ranger', 'Edge', 'Fusion', 'Territory', 'Mustang'],
    'Hyundai': ['HB20', 'Creta', 'Tucson', 'Santa Fe', 'Azera', 'Elantra', 'i30', 'ix35'],
    'Toyota': ['Etios', 'Yaris', 'Corolla', 'RAV4', 'Hilux', 'SW4', 'Prius', 'Camry', 'Corolla Cross'],
    'Honda': ['Fit', 'City', 'Civic', 'HR-V', 'CR-V', 'Accord', 'WR-V'],
    'Nissan': ['March', 'Versa', 'Sentra', 'Kicks', 'X-Trail', 'Frontier', 'Altima'],
    'Renault': ['Kwid', 'Sandero', 'Logan', 'Duster', 'Captur', 'Fluence', 'Oroch'],
    'Peugeot': ['208', '2008', '308', '3008', '5008', '508', 'Partner'],
    'Citroën': ['C3', 'C4 Cactus', 'Aircross', 'Berlingo', 'C4 Lounge'],
    'Jeep': ['Renegade', 'Compass', 'Commander', 'Wrangler', 'Grand Cherokee'],
    'BMW': ['Série 1', 'Série 3', 'Série 5', 'X1', 'X3', 'X5', 'X6'],
    'Mercedes-Benz': ['Classe A', 'Classe C', 'Classe E', 'GLA', 'GLC', 'GLE'],
    'Audi': ['A3', 'A4', 'A6', 'Q3', 'Q5', 'Q7', 'Q8'],
    'Volvo': ['XC40', 'XC60', 'XC90', 'S60', 'V40'],
    'Mitsubishi': ['Lancer', 'ASX', 'Outlander', 'Pajero', 'L200'],
    'Kia': ['Picanto', 'Rio', 'Cerato', 'Sportage', 'Sorento', 'Stinger'],
    'Suzuki': ['Jimny', 'Vitara', 'S-Cross', 'Swift'],
    'Subaru': ['Impreza', 'Legacy', 'Outback', 'Forester', 'XV']
}

@carros_bp.route('/popular-marcas', methods=['POST'])
def popular_marcas():
    """Popula a lista de marcas de carros"""
    try:
        return jsonify({
            'success': True,
            'marcas': sorted(MARCAS_POPULARES),
            'message': 'Marcas carregadas com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'marcas': []
        }), 500

@carros_bp.route('/modelos/<marca>', methods=['GET'])
def get_modelos(marca):
    """Retorna os modelos de uma marca específica"""
    try:
        modelos = MODELOS_POR_MARCA.get(marca, [])
        return jsonify({
            'success': True,
            'modelos': sorted(modelos),
            'marca': marca,
            'message': f'Modelos da {marca} carregados com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'modelos': []
        }), 500

@carros_bp.route('/marcas', methods=['GET'])
def get_marcas():
    """Retorna todas as marcas disponíveis"""
    try:
        return jsonify({
            'success': True,
            'marcas': sorted(MARCAS_POPULARES),
            'total': len(MARCAS_POPULARES)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'marcas': []
        }), 500

