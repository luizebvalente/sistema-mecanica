-- Adicionar campos que podem estar faltando
ALTER TABLE servico_execucao 
ADD COLUMN IF NOT EXISTS historico_pausas TEXT,
ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Atualizar registros existentes que não têm timestamp
UPDATE servico_execucao 
SET criado_em = inicio 
WHERE criado_em IS NULL AND inicio IS NOT NULL;

UPDATE servico_execucao 
SET atualizado_em = COALESCE(fim_real, pausado_em, inicio, CURRENT_TIMESTAMP)
WHERE atualizado_em IS NULL;

-- Garantir que tempo_pausado_total não seja NULL
UPDATE servico_execucao 
SET tempo_pausado_total = 0 
WHERE tempo_pausado_total IS NULL;

-- Garantir que tempo_extra_minutos não seja NULL
UPDATE servico_execucao 
SET tempo_extra_minutos = 0 
WHERE tempo_extra_minutos IS NULL;

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_servico_execucao_status ON servico_execucao(status);
CREATE INDEX IF NOT EXISTS idx_servico_execucao_box_status ON servico_execucao(box_id, status);
CREATE INDEX IF NOT EXISTS idx_servico_execucao_fim_real ON servico_execucao(fim_real);
CREATE INDEX IF NOT EXISTS idx_servico_execucao_pausado_em ON servico_execucao(pausado_em);

-- Verificar dados inconsistentes e corrigir
-- Serviços marcados como pausados mas sem data de pausa
UPDATE servico_execucao 
SET status = 'em_andamento', pausado_em = NULL 
WHERE status = 'pausado' AND pausado_em IS NULL;

-- Serviços com data de pausa mas não marcados como pausados
UPDATE servico_execucao 
SET status = 'pausado' 
WHERE pausado_em IS NOT NULL AND status = 'em_andamento' AND fim_real IS NULL;
