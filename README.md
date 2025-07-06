# Sistema de Mecânica - Gestão de Filas

Sistema completo para gestão de oficina mecânica com foco na gestão inteligente de filas de serviços.

## 🚀 Melhorias Implementadas

### ✅ Gestão Avançada de Filas
- **Iniciar Serviços da Fila**: Botão para iniciar qualquer serviço específico da fila
- **Controle de Pausa/Retomada**: Pausar e retomar serviços em andamento
- **Reordenação de Fila**: Mover serviços para cima/baixo na fila
- **Status Expandidos**: Novos status (pausado, interrompido) para melhor controle

### ✅ Interface Moderna
- **Dashboard Interativo**: Visão geral em tempo real de todos os boxes
- **Gestão Visual de Filas**: Interface intuitiva para gerenciar filas por box
- **Controles de Serviço**: Botões para pausar, retomar, finalizar e interromper
- **Indicadores Visuais**: Progresso, tempo restante e status coloridos

### ✅ Funcionalidades Avançadas
- **Dados Completos do Cliente**: Nome, telefone, veículo completo
- **Controle de Tempo**: Tempo extra, pausas, histórico de interrupções
- **Priorização**: Sistema de prioridades para serviços urgentes
- **Estatísticas**: Tempo médio, serviços concluídos, produtividade

## 🛠️ Tecnologias

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados (fácil deploy)
- **Flask-CORS** - Suporte a CORS

### Frontend
- **React** - Interface moderna e responsiva
- **Tailwind CSS** - Estilização utilitária
- **Shadcn/UI** - Componentes de alta qualidade
- **Lucide Icons** - Ícones modernos
- **React Router** - Navegação SPA

## 📦 Estrutura do Projeto

```
sistema-mecanica-main/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── render.yaml           # Configuração Render
├── src/
│   ├── models/           # Modelos de dados
│   │   ├── box.py
│   │   ├── fila_servico.py
│   │   ├── servico_execucao.py
│   │   ├── mecanico.py
│   │   ├── tipo_servico.py
│   │   └── user.py
│   ├── routes/           # Rotas da API
│   │   ├── box.py
│   │   ├── fila_servico.py
│   │   ├── servico_execucao.py
│   │   ├── mecanico.py
│   │   ├── tipo_servico.py
│   │   ├── painel.py
│   │   ├── relatorio.py
│   │   └── user.py
│   └── static/           # Frontend React (build)
│       ├── index.html
│       └── assets/
└── database.db          # Banco SQLite (criado automaticamente)
```

## 🚀 Deploy no Render

### 1. Preparação
```bash
# Clone o repositório
git clone <seu-repositorio>
cd sistema-mecanica-main

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração no Render
1. Conecte seu repositório GitHub ao Render
2. Configure como **Web Service**
3. Use as seguintes configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3.11

### 3. Variáveis de Ambiente (Opcional)
```
SECRET_KEY=sua_chave_secreta_aqui
PORT=5000
```

## 🔧 Desenvolvimento Local

### Backend
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python app.py
```

### Frontend (para desenvolvimento)
```bash
# Navegar para o diretório do frontend
cd sistema-mecanica-frontend

# Instalar dependências
pnpm install

# Executar em modo desenvolvimento
pnpm run dev
```

## 📋 APIs Principais

### Gestão de Filas
- `GET /api/fila-servicos` - Listar serviços na fila
- `POST /api/fila-servicos` - Adicionar serviço à fila
- `POST /api/fila-servicos/{id}/iniciar` - Iniciar serviço específico
- `PUT /api/fila-servicos/reordenar` - Reordenar fila
- `DELETE /api/fila-servicos/{id}` - Remover da fila

### Controle de Execução
- `GET /api/servicos-execucao` - Listar serviços em execução
- `PUT /api/servicos-execucao/{id}/pausar` - Pausar serviço
- `PUT /api/servicos-execucao/{id}/retomar` - Retomar serviço
- `PUT /api/servicos-execucao/{id}/finalizar` - Finalizar serviço
- `PUT /api/servicos-execucao/{id}/interromper` - Interromper serviço

### Estatísticas
- `GET /api/servicos-execucao/estatisticas` - Estatísticas gerais
- `GET /api/fila-servicos/estatisticas/{box_id}` - Estatísticas por box

## 🎯 Funcionalidades Principais

### Dashboard
- Visão geral de todos os boxes
- Estatísticas em tempo real
- Controles rápidos de pausa/retomada/finalização
- Indicadores de progresso e tempo

### Gestão de Filas
- Adicionar novos serviços
- Reordenar prioridades
- Iniciar serviços específicos
- Visualizar tempo estimado

### Execução de Serviços
- Monitoramento em tempo real
- Controle de pausas
- Histórico de interrupções
- Cálculo automático de tempos

## 🔄 Atualizações Implementadas

### Modelos de Dados
- ✅ Campos adicionais para cliente e veículo
- ✅ Controle de posição na fila
- ✅ Sistema de pausas e histórico
- ✅ Status expandidos (pausado, interrompido)

### APIs
- ✅ Endpoints para iniciar serviços específicos
- ✅ Controles de pausa/retomada
- ✅ Reordenação de filas
- ✅ Estatísticas avançadas

### Interface
- ✅ Dashboard moderno e responsivo
- ✅ Gestão visual de filas
- ✅ Controles intuitivos
- ✅ Indicadores em tempo real

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do Render
2. Confirme se todas as dependências estão instaladas
3. Teste localmente antes do deploy

## 📄 Licença

Este projeto é proprietário e destinado ao uso interno da oficina mecânica.

