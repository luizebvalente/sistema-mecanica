from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.box import Box

box_bp = Blueprint('box', __name__)

@box_bp.route('/boxes', methods=['GET'])
def get_boxes():
    try:
        boxes = Box.query.all()
        return jsonify([box.to_dict() for box in boxes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@box_bp.route('/boxes', methods=['POST'])
def create_box():
    try:
        data = request.get_json()
        box = Box(
            numero=data['numero'],
            tipo=data['tipo'],
            status=data.get('status', 'livre')
        )
        db.session.add(box)
        db.session.commit()
        return jsonify(box.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@box_bp.route('/boxes/<int:id>', methods=['GET'])
def get_box(id):
    try:
        box = Box.query.get_or_404(id)
        return jsonify(box.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@box_bp.route('/boxes/<int:id>', methods=['PUT'])
def update_box(id):
    try:
        box = Box.query.get_or_404(id)
        data = request.get_json()
        
        box.numero = data.get('numero', box.numero)
        box.tipo = data.get('tipo', box.tipo)
        box.status = data.get('status', box.status)
        
        db.session.commit()
        return jsonify(box.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@box_bp.route('/boxes/<int:id>', methods=['DELETE'])
def delete_box(id):
    try:
        box = Box.query.get_or_404(id)
        db.session.delete(box)
        db.session.commit()
        return jsonify({'message': 'Box deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

