# Sistema de Mecânica - Deploy Render (Simples)

Sistema completo de mecânica com painel em tempo real, otimizado para deploy simples no Render.

## 🚀 Características

- **Aplicação única**: Frontend + Backend integrados
- **Banco SQLite**: Sem configuração adicional
- **Deploy automático**: Via GitHub
- **Gratuito**: Plano Render gratuito

## 📁 Estrutura

```
├── app.py              # Aplicação Flask principal
├── render.yaml         # Configuração Render
├── requirements.txt    # Dependências Python
└── src/
    ├── static/         # Frontend React (build)
    ├── models/         # Modelos do banco
    └── routes/         # APIs REST
```

## 🌐 Deploy no Render

### Pré-requisitos
- Conta no [Render](https://render.com)
- Repositório no GitHub

### Passos Simples

1. **Criar Repositório GitHub**
   ```bash
   git init
   git add .
   git commit -m "Sistema de Mecânica - Render"
   git remote add origin https://github.com/SEU_USUARIO/sistema-mecanica.git
   git push -u origin main
   ```

2. **Deploy no Render**
   - Acesse [Render](https://render.com)
   - Clique em "New Web Service"
   - Conecte seu repositório GitHub
   - Configurações automáticas:
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`

3. **Pronto!**
   - Render detecta automaticamente as configurações
   - Deploy em ~3 minutos
   - URL automática: `https://seu-app.onrender.com`

## ✅ Funcionalidades

- ✅ Painel em tempo real
- ✅ Cronômetros automáticos
- ✅ Cadastro de mecânicos
- ✅ Cadastro de boxes
- ✅ Cadastro de tipos de serviço
- ✅ Iniciar/finalizar serviços
- ✅ Modal de detalhes
- ✅ Interface responsiva

## 🔧 Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python app.py

# Acessar: http://localhost:5000
```

## 📊 Banco de Dados

- **SQLite**: Arquivo local `database.db`
- **Criação automática**: Tabelas criadas no primeiro acesso
- **Persistência**: Dados mantidos entre deploys

## 🌐 URLs da Aplicação

- **Frontend**: `/` (interface principal)
- **API**: `/api/*` (endpoints REST)
- **Health**: `/health` (status da aplicação)

## 💰 Custos

- **Render Gratuito**: 750 horas/mês
- **Render Pago**: $7/mês (quando necessário)

## 🔄 Atualizações

Para atualizar o sistema:
1. Faça alterações no código
2. Commit e push para GitHub
3. Render faz deploy automático

## 🆘 Suporte

- Logs disponíveis no dashboard Render
- Health check em `/health`
- Banco SQLite simples e confiável

**Sistema pronto para produção em minutos!** 🚀

