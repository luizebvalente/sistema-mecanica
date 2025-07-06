# Changelog - Sistema de Mecânica

## [2.0.0] - 2025-07-06

### 🚀 Melhorias Principais

#### Gestão Avançada de Filas
- **NOVO**: Botão "Iniciar" para serviços específicos da fila
- **NOVO**: Controles de pausa/retomada para serviços em andamento
- **NOVO**: Reordenação de filas com drag-and-drop visual
- **NOVO**: Sistema de prioridades (Baixa, Normal, Média, Alta, Urgente)
- **MELHORADO**: Interface visual para gestão de filas por box

#### Controle de Serviços
- **NOVO**: Status "pausado" e "interrompido" para serviços
- **NOVO**: Histórico de pausas com motivos e durações
- **NOVO**: Cálculo automático de tempo pausado
- **NOVO**: Controle de tempo extra com justificativa
- **MELHORADO**: Cálculo preciso de tempo restante e progresso

#### Interface do Usuário
- **NOVO**: Dashboard moderno com React + Tailwind CSS
- **NOVO**: Navegação por abas (Dashboard, Fila, Execução, etc.)
- **NOVO**: Indicadores visuais de progresso em tempo real
- **NOVO**: Cards informativos para cada box
- **NOVO**: Modal avançado para adicionar serviços
- **MELHORADO**: Design responsivo para mobile e desktop

#### Dados e Funcionalidades
- **NOVO**: Campos completos do cliente (nome, telefone)
- **NOVO**: Dados completos do veículo (marca, modelo, cor, placa)
- **NOVO**: Sistema de observações expandido
- **NOVO**: Estatísticas em tempo real
- **NOVO**: Cálculo de tempo médio de conclusão

### 🔧 Melhorias Técnicas

#### Backend (Flask)
- **NOVO**: Endpoints para iniciar serviços específicos (`POST /api/fila-servicos/{id}/iniciar`)
- **NOVO**: Endpoints para pausar/retomar (`PUT /api/servicos-execucao/{id}/pausar|retomar`)
- **NOVO**: Endpoint para reordenar fila (`PUT /api/fila-servicos/reordenar`)
- **NOVO**: Endpoints de estatísticas (`GET /api/servicos-execucao/estatisticas`)
- **MELHORADO**: Modelos de dados com campos adicionais
- **MELHORADO**: Validação de dados mais robusta

#### Frontend (React)
- **NOVO**: Aplicação React moderna com componentes reutilizáveis
- **NOVO**: Gerenciamento de estado com hooks
- **NOVO**: Sistema de notificações (toasts)
- **NOVO**: Tema claro/escuro
- **NOVO**: Ícones Lucide para melhor UX
- **MELHORADO**: Performance com lazy loading

#### Banco de Dados
- **NOVO**: Campo `posicao_fila` para ordenação
- **NOVO**: Campos de cliente e veículo
- **NOVO**: Controle de pausas e histórico
- **NOVO**: Timestamps de atualização
- **MELHORADO**: Relacionamentos entre tabelas

### 🐛 Correções
- **CORRIGIDO**: Cálculo incorreto de tempo estimado
- **CORRIGIDO**: Problemas de sincronização entre fila e execução
- **CORRIGIDO**: Status inconsistente dos boxes
- **CORRIGIDO**: Validação de dados obrigatórios

### 📋 APIs Adicionadas

#### Gestão de Filas
```
POST /api/fila-servicos/{id}/iniciar     # Iniciar serviço específico
PUT  /api/fila-servicos/reordenar        # Reordenar itens da fila
GET  /api/fila-servicos/estatisticas/{box_id}  # Estatísticas por box
```

#### Controle de Execução
```
PUT /api/servicos-execucao/{id}/pausar      # Pausar serviço
PUT /api/servicos-execucao/{id}/retomar     # Retomar serviço
PUT /api/servicos-execucao/{id}/interromper # Interromper serviço
GET /api/servicos-execucao/estatisticas     # Estatísticas gerais
GET /api/servicos-execucao/{id}/historico-pausas  # Histórico de pausas
```

### 🔄 Migrações Necessárias

#### Modelos Atualizados
- `FilaServico`: Novos campos para cliente, veículo e controle
- `ServicoExecucao`: Campos de pausa e histórico
- `Box`: Status "pausado" adicionado

#### Dados Existentes
- Serviços existentes mantêm compatibilidade
- Novos campos têm valores padrão apropriados
- Migração automática no primeiro acesso

### 📱 Compatibilidade
- **Navegadores**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile**: iOS 14+, Android 8+
- **Backend**: Python 3.11+, Flask 3.1+
- **Deploy**: Render, Heroku, VPS

### 🎯 Próximas Funcionalidades (Roadmap)
- [ ] Relatórios avançados com gráficos
- [ ] Sistema de notificações push
- [ ] Integração com WhatsApp para clientes
- [ ] Backup automático de dados
- [ ] Sistema de usuários e permissões
- [ ] App mobile nativo

---

## [1.0.0] - 2024-06-24

### Funcionalidades Iniciais
- Sistema básico de boxes
- Gestão simples de serviços
- Interface web básica
- Deploy no Render

