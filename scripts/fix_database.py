# scripts/fix_database.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.box import Box
from datetime import datetime
import json

def fix_database():
    """Corrige problemas comuns no banco de dados"""
    print("🔧 Iniciando correções no banco de dados...")
    
    try:
        # Correções (use o conteúdo do script de correção fornecido)
        # ... (copie o conteúdo da função fix_database do artifact)
        
        print("✅ Correções aplicadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante correção: {str(e)}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    # Executar correções
    fix_database()
