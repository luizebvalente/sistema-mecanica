import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.mecanico import Mecanico
from src.models.box import Box
from src.models.tipo_servico import TipoServico
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from src.routes.user import user_bp
from src.routes.mecanico import mecanico_bp
from src.routes.box import box_bp
from src.routes.tipo_servico import tipo_servico_bp
from src.routes.servico_execucao import servico_execucao_bp
from src.routes.fila_servico import fila_servico_bp
from src.routes.painel import painel_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(mecanico_bp, url_prefix='/api')
app.register_blueprint(box_bp, url_prefix='/api')
app.register_blueprint(tipo_servico_bp, url_prefix='/api')
app.register_blueprint(servico_execucao_bp, url_prefix='/api')
app.register_blueprint(fila_servico_bp, url_prefix='/api')
app.register_blueprint(painel_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
