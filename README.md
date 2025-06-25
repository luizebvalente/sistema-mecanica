# Sistema de Mecânica Profissional - Versão Melhorada

Sistema completo de gestão para oficinas mecânicas com frontend React moderno e backend Flask robusto.

## 🚀 Melhorias Implementadas

### ✅ 1. Contador de Tempo com Atraso
- **Cronômetro vermelho** quando o serviço está em atraso
- **Tempo negativo** exibido (ex: -01:30)
- **Texto "EM ATRASO"** destacado em vermelho
- **Animação pulsante** para chamar atenção

### ✅ 2. Agendamento por Data e Hora
- **Seletor de data** para agendamentos futuros
- **Seletor de horário** específico
- **Filtro automático** - painel mostra apenas serviços do dia atual
- **Lógica inteligente** de posicionamento na fila por data

### ✅ 3. Sistema de Relatórios Completo
- **Dashboard geral** com estatísticas em tempo real
- **Relatório de serviços concluídos** com filtros
- **Relatório de filas futuras** agrupadas por data
- **Relatório de produtividade** dos mecânicos
- **Interface moderna** com abas e gráficos

### ✅ 4. Exibição de Telefone
- **Telefone do cliente** visível no painel principal
- **Telefone na fila** de espera
- **Formatação adequada** e destaque visual
- **Ícone de telefone** para fácil identificação

### ✅ 5. Interface Moderna
- **Design responsivo** para desktop e mobile
- **Navegação intuitiva** com React Router
- **Atualização em tempo real** do painel
- **Componentes modernos** com shadcn/ui
- **Cores e ícones** profissionais

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados
- **Flask-CORS** - Suporte a CORS
- **Python 3.11** - Linguagem de programação

### Frontend
- **React 18** - Framework JavaScript
- **React Router** - Navegação SPA
- **Tailwind CSS** - Framework CSS
- **shadcn/ui** - Componentes UI
- **Lucide Icons** - Ícones modernos
- **Vite** - Build tool

## 📦 Estrutura do Projeto

```
sistema-mecanica-main3/
├── app.py                          # Aplicação Flask principal
├── requirements.txt                # Dependências Python
├── render.yaml                     # Configuração para deploy no Render
├── src/
│   ├── models/                     # Modelos de dados
│   │   ├── fila_servico.py        # ✨ Modelo atualizado com data/hora
│   │   ├── servico_execucao.py    # Modelo de execução de serviços
│   │   └── ...
│   ├── routes/                     # Rotas da API
│   │   ├── painel.py              # ✨ Rota atualizada com atraso
│   │   ├── relatorio.py           # ✨ Nova rota de relatórios
│   │   └── ...
│   └── static/                     # Frontend React compilado
├── sistema-mecanica-frontend/      # Código fonte React
│   ├── src/
│   │   ├── App.jsx                # ✨ Aplicação React completa
│   │   ├── App.css                # ✨ Estilos personalizados
│   │   └── components/
│   ├── package.json
│   └── ...
└── MELHORIAS_IMPLEMENTADAS.md     # Documentação detalhada
```

## 🚀 Deploy no Render

### Opção 1: Deploy Automático
1. Faça upload do projeto para um repositório GitHub
2. Conecte o repositório ao Render
3. O arquivo `render.yaml` configurará automaticamente:
   - Instalação das dependências Python
   - Build do frontend React
   - Integração frontend + backend
   - Inicialização do servidor

### Opção 2: Deploy Manual
1. Crie um novo Web Service no Render
2. Configure as seguintes variáveis:
   - **Build Command**: `pip install -r requirements.txt && cd sistema-mecanica-frontend && npm install && npm run build && cp -r dist/* ../src/static/`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3.11

## 💻 Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- npm ou pnpm

### Instalação

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd sistema-mecanica-main3
```

2. **Instale dependências Python**
```bash
pip install -r requirements.txt
```

3. **Instale dependências Node.js**
```bash
cd sistema-mecanica-frontend
npm install
```

4. **Build do frontend**
```bash
npm run build
cp -r dist/* ../src/static/
```

5. **Execute o servidor**
```bash
cd ..
python app.py
```

6. **Acesse o sistema**
```
http://localhost:5000
```

### Desenvolvimento do Frontend

Para desenvolvimento ativo do frontend:

```bash
cd sistema-mecanica-frontend
npm run dev
```

O frontend estará disponível em `http://localhost:5173` e se conectará automaticamente ao backend em `http://localhost:5000`.

## 📱 Como Usar

### 1. Painel Principal
- **Visualização em tempo real** de todos os boxes
- **Cronômetro com atraso** em vermelho quando necessário
- **Telefone dos clientes** visível
- **Fila de espera** com posições
- **Atualização automática** a cada segundo

### 2. Iniciar Serviço
- **Agendamento por data/hora** específica
- **Formulário completo** com todos os dados
- **Validação automática** de campos obrigatórios
- **Integração com API** de marcas/modelos

### 3. Relatórios
- **Dashboard**: Visão geral do dia
- **Serviços Concluídos**: Histórico com estatísticas
- **Filas Futuras**: Agendamentos por data
- **Produtividade**: Métricas dos mecânicos

## 🔧 APIs Disponíveis

### Painel
- `GET /api/painel` - Dados do painel em tempo real

### Relatórios
- `GET /api/relatorios/dashboard` - Dashboard geral
- `GET /api/relatorios/servicos-concluidos` - Serviços finalizados
- `GET /api/relatorios/filas-futuras` - Agendamentos futuros
- `GET /api/relatorios/produtividade-mecanicos` - Métricas dos mecânicos

### Agendamento
- `POST /api/fila-servicos` - Criar novo agendamento

## 🎨 Personalização

### Cores e Temas
Edite `sistema-mecanica-frontend/src/App.css` para personalizar:
- Cores do cronômetro de atraso
- Estilos dos cards de status
- Animações e transições

### Configuração da API
Edite `sistema-mecanica-frontend/src/App.jsx`:
```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://seu-backend.onrender.com/api' 
  : 'http://localhost:5000/api';
```

## 📊 Funcionalidades Principais

### ⏰ Cronômetro Inteligente
- Conta regressiva em verde quando no prazo
- Muda para vermelho com tempo negativo quando atrasado
- Texto "EM ATRASO" piscante para alertar
- Atualização em tempo real

### 📅 Agendamento Avançado
- Seleção de data futura
- Horário específico
- Fila organizada por data
- Painel filtra apenas o dia atual

### 📈 Relatórios Detalhados
- Estatísticas de produtividade
- Histórico de serviços
- Agendamentos futuros
- Métricas por mecânico

### 📱 Interface Responsiva
- Funciona em desktop, tablet e mobile
- Design moderno e profissional
- Navegação intuitiva
- Componentes acessíveis

## 🔒 Segurança

- CORS configurado para produção
- Validação de dados no frontend e backend
- Sanitização de inputs
- Tratamento de erros robusto

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `MELHORIAS_IMPLEMENTADAS.md`
2. Consulte os logs do servidor
3. Teste as APIs individualmente

## 🎯 Próximas Melhorias Sugeridas

- [ ] Notificações push para atrasos
- [ ] Integração com WhatsApp para clientes
- [ ] Backup automático de dados
- [ ] Relatórios em PDF
- [ ] Sistema de usuários e permissões
- [ ] Integração com sistemas de pagamento

---

**Sistema desenvolvido com ❤️ para oficinas mecânicas profissionais**

