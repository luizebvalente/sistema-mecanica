from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.carro import MarcaCarro, ModeloCarro

carro_bp = Blueprint('carro', __name__)

# Rotas para Marcas
@carro_bp.route('/marcas-carro', methods=['GET'])
def get_marcas():
    try:
        marcas = MarcaCarro.query.order_by(MarcaCarro.nome).all()
        return jsonify([marca.to_dict() for marca in marcas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@carro_bp.route('/marcas-carro', methods=['POST'])
def create_marca():
    try:
        data = request.get_json()
        marca = MarcaCarro(nome=data['nome'])
        db.session.add(marca)
        db.session.commit()
        return jsonify(marca.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Modelos
@carro_bp.route('/modelos-carro', methods=['GET'])
def get_modelos():
    try:
        marca_id = request.args.get('marca_id')
        if marca_id:
            modelos = ModeloCarro.query.filter_by(marca_id=marca_id).order_by(ModeloCarro.nome).all()
        else:
            modelos = ModeloCarro.query.order_by(ModeloCarro.nome).all()
        return jsonify([modelo.to_dict() for modelo in modelos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@carro_bp.route('/modelos-carro', methods=['POST'])
def create_modelo():
    try:
        data = request.get_json()
        modelo = ModeloCarro(
            nome=data['nome'],
            marca_id=data['marca_id']
        )
        db.session.add(modelo)
        db.session.commit()
        return jsonify(modelo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rota para popular dados iniciais
@carro_bp.route('/marcas-carro/popular', methods=['POST'])
def popular_marcas_modelos():
    try:
        # Dados iniciais de marcas e modelos populares no Brasil
        marcas_modelos = {
            'Volkswagen': ['Gol', 'Fox', 'Polo', 'Jetta', 'Passat', 'Tiguan', 'T-Cross'],
            'Chevrolet': ['Onix', 'Prisma', 'Cruze', 'Tracker', 'S10', 'Spin', 'Cobalt'],
            'Fiat': ['Uno', 'Palio', 'Siena', 'Strada', 'Toro', 'Argo', 'Cronos'],
            'Ford': ['Ka', 'Fiesta', 'Focus', 'EcoSport', 'Ranger', 'Edge'],
            'Hyundai': ['HB20', 'Creta', 'Tucson', 'Santa Fe', 'Azera', 'i30'],
            'Toyota': ['Corolla', 'Etios', 'Hilux', 'RAV4', 'Camry', 'Prius'],
            'Honda': ['Civic', 'Fit', 'City', 'HR-V', 'CR-V', 'Accord'],
            'Nissan': ['March', 'Versa', 'Sentra', 'Kicks', 'Frontier', 'X-Trail'],
            'Renault': ['Sandero', 'Logan', 'Duster', 'Captur', 'Fluence'],
            'Peugeot': ['208', '2008', '3008', '5008', '308', '408']
        }
        
        for marca_nome, modelos_lista in marcas_modelos.items():
            # Verificar se a marca já existe
            marca = MarcaCarro.query.filter_by(nome=marca_nome).first()
            if not marca:
                marca = MarcaCarro(nome=marca_nome)
                db.session.add(marca)
                db.session.flush()  # Para obter o ID
            
            # Adicionar modelos
            for modelo_nome in modelos_lista:
                modelo_existente = ModeloCarro.query.filter_by(
                    nome=modelo_nome, 
                    marca_id=marca.id
                ).first()
                if not modelo_existente:
                    modelo = ModeloCarro(nome=modelo_nome, marca_id=marca.id)
                    db.session.add(modelo)
        
        db.session.commit()
        return jsonify({'message': 'Marcas e modelos populados com sucesso'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas compatíveis com o frontend React
@carro_bp.route('/carros/popular-marcas', methods=['POST'])
def popular_marcas():
    """Rota compatível com o frontend - popula e retorna marcas"""
    try:
        # Primeiro popula os dados
        popular_marcas_modelos()
        
        # Depois retorna as marcas
        marcas = MarcaCarro.query.order_by(MarcaCarro.nome).all()
        marcas_lista = [marca.nome for marca in marcas]
        
        return jsonify({
            'success': True,
            'marcas': marcas_lista,
            'message': 'Marcas carregadas com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'marcas': []
        }), 500

@carro_bp.route('/carros/modelos/<marca>', methods=['GET'])
def get_modelos_por_marca(marca):
    """Retorna os modelos de uma marca específica"""
    try:
        marca_obj = MarcaCarro.query.filter_by(nome=marca).first()
        if not marca_obj:
            return jsonify({
                'success': False,
                'error': 'Marca não encontrada',
                'modelos': []
            }), 404
        
        modelos = ModeloCarro.query.filter_by(marca_id=marca_obj.id).order_by(ModeloCarro.nome).all()
        modelos_lista = [modelo.nome for modelo in modelos]
        
        return jsonify({
            'success': True,
            'modelos': modelos_lista,
            'marca': marca,
            'message': f'Modelos da {marca} carregados com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'modelos': []
        }), 500

