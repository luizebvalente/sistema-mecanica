# TODO - Correções Sistema de Mecânica

## Fase 1: Análise do problema ✅
- [x] Analisar estrutura do projeto
- [x] Examinar modelos de dados (FilaServico, ServicoExecucao)
- [x] Examinar rotas da API
- [x] Identificar problemas:
  - Serviços pausados não aparecem na gestão da fila
  - Falta contador de tempo real (cronômetro)
  - Falta indicação de tempo negativo para atrasos

## Fase 2: Correção do backend - Gestão da fila ✅
- [x] Modificar rota GET /fila-servicos para incluir serviços pausados
- [x] Criar nova rota para buscar todos os serviços (fila + pausados)
- [x] Atualizar lógica de status para distinguir serviços pausados na fila

## Fase 3: Implementação do contador de tempo real ✅
- [x] Adicionar campos de tempo real no modelo ServicoExecucao
- [x] Criar endpoint para obter tempo atual de execução
- [x] Implementar cálculo de tempo negativo (atraso)
- [x] Adicionar WebSocket ou polling para tempo real

## Fase 4: Atualização do frontend ✅
- [x] Analisar código React atual
- [x] Implementar componente de cronômetro
- [x] Adicionar exibição de serviços pausados na gestão da fila
- [x] Implementar atualização em tempo real
- [x] Adicionar indicação visual para atrasos

## Fase 5: Teste e empacotamento ✅
- [x] Testar funcionalidades corrigidas
- [x] Verificar se serviços pausados aparecem na fila
- [x] Verificar cronômetro em tempo real
- [x] Criar arquivo ZIP para GitHub

## Correções Implementadas:

### 1. ✅ Serviços pausados agora aparecem na gestão da fila
**Solução implementada**: 
- Nova rota `/api/fila-servicos/gestao` que combina serviços agendados (FilaServico) e pausados (ServicoExecucao)
- Frontend atualizado para usar a nova rota e exibir serviços pausados com destaque visual
- Botões de ação específicos para cada tipo de serviço (Iniciar, Retomar, Pausar, Finalizar)

### 2. ✅ Contador de tempo real implementado
**Solução implementada**:
- Novo método `calcular_tempo_real_atual()` no modelo ServicoExecucao
- Nova rota `/api/servicos-execucao/tempo-real` para obter dados em tempo real
- Frontend com cronômetro que atualiza a cada segundo
- Exibição de tempo decorrido, tempo restante e percentual de conclusão

### 3. ✅ Indicação de tempo negativo (atraso) implementada
**Solução implementada**:
- Cálculo de tempo restante permite valores negativos
- Indicação visual de atraso com cor vermelha
- Exibição separada do tempo de atraso
- Barra de progresso que muda de cor quando há atraso

### 4. ✅ Melhorias adicionais implementadas:
- Interface moderna com Tailwind CSS e shadcn/ui
- Atualização automática dos dados a cada 30 segundos
- Cronômetro em tempo real atualizado a cada segundo
- Indicações visuais claras para diferentes status
- Informações detalhadas sobre pausas e motivos
- Layout responsivo para desktop e mobile

## Arquivos Modificados:

### Backend:
- `src/routes/fila_servico.py` - Nova rota `/gestao` para combinar fila e pausados
- `src/routes/servico_execucao.py` - Novas rotas de tempo real
- `src/models/servico_execucao.py` - Novo método para cálculo de tempo real

### Frontend:
- `frontend-mecanica/` - Nova aplicação React completa
- Dashboard moderno com cronômetro em tempo real
- Gestão completa de serviços pausados e na fila

