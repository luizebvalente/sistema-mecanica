import os
from flask import Flask, send_from_directory, send_file
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

def create_app():
    # Configurar diretório estático
    static_dir = os.path.join(os.path.dirname(__file__), 'src', 'static')
    app = Flask(__name__, static_folder=static_dir)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    
    # Banco de dados SQLite (simples para Render)
    database_path = os.path.join(os.path.dirname(__file__), 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Habilitar CORS
    CORS(app, origins=["*"])
    
    # Registrar blueprints da API
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(mecanico_bp, url_prefix='/api')
    app.register_blueprint(box_bp, url_prefix='/api')
    app.register_blueprint(tipo_servico_bp, url_prefix='/api')
    app.register_blueprint(servico_execucao_bp, url_prefix='/api')
    app.register_blueprint(fila_servico_bp, url_prefix='/api')
    app.register_blueprint(painel_bp, url_prefix='/api')
    
    # Inicializar banco de dados
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    # Rota para servir o frontend React
    @app.route('/')
    def serve_frontend():
        return send_file(os.path.join(static_dir, 'index.html'))
    
    # Rota para servir assets do frontend
    @app.route('/<path:path>')
    def serve_static(path):
        # Se for uma rota da API, deixa passar
        if path.startswith('api/'):
            return {'error': 'API route not found'}, 404
            
        # Tenta servir o arquivo estático
        try:
            return send_from_directory(static_dir, path)
        except:
            # Se não encontrar, serve o index.html (SPA routing)
            return send_file(os.path.join(static_dir, 'index.html'))
    
    # Health check para Render
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy', 
            'message': 'Sistema de Mecânica - Render Deploy',
            'database': 'SQLite',
            'version': '1.0.0'
        }
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

