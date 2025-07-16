// CORREÇÃO COMPLETA - Sistema de Mecânica
// Arquivo: src/static/frontend-fix-v2.js

// ===== CORREÇÃO 1: FUNÇÃO SEGURA PARA FORMATAÇÃO DE TEMPO =====
function formatarTempoSeguro(minutos) {
    try {
        // Converter para número e validar
        let min = parseFloat(minutos);
        
        // Verificar se é um número válido
        if (isNaN(min) || min === null || min === undefined) {
            return "0min";
        }
        
        // Garantir que seja positivo
        min = Math.max(0, Math.floor(min));
        
        if (min < 60) {
            return `${min}min`;
        } else {
            const horas = Math.floor(min / 60);
            const mins = min % 60;
            if (mins === 0) {
                return `${horas}h`;
            } else {
                return `${horas}h ${mins}min`;
            }
        }
    } catch (error) {
        console.error('Erro ao formatar tempo:', error);
        return "0min";
    }
}

// ===== CORREÇÃO 2: FUNÇÃO PARA ATUALIZAR TEMPOS NO DASHBOARD =====
function atualizarTemposNoDOM() {
    try {
        // Procurar por elementos que mostram tempo
        const elementosComTempo = document.querySelectorAll(
            '[data-tempo], .tempo-decorrido, .tempo-restante, .tempo-estimado, ' +
            '.progress-time, .service-time, .remaining-time'
        );
        
        elementosComTempo.forEach(elemento => {
            const textoAtual = elemento.textContent;
            
            // Se contém "NaN" ou está vazio, corrigir
            if (textoAtual.includes('NaN') || textoAtual.includes('undefined') || 
                textoAtual.trim() === '' || textoAtual === 'NaNm') {
                
                // Tentar extrair valor numérico do elemento ou usar 0
                const valorTempo = elemento.dataset.tempo || 
                                 elemento.dataset.minutos || 
                                 elemento.getAttribute('data-value') || 
                                 0;
                
                elemento.textContent = formatarTempoSeguro(valorTempo);
            }
        });
        
        // Corrigir elementos de progresso
        const progressBars = document.querySelectorAll('.progress-bar, [role="progressbar"]');
        progressBars.forEach(bar => {
            const valor = bar.getAttribute('aria-valuenow') || bar.style.width || '0';
            const valorNum = parseFloat(valor.replace('%', ''));
            
            if (isNaN(valorNum)) {
                bar.style.width = '0%';
                bar.setAttribute('aria-valuenow', '0');
            }
        });
        
    } catch (error) {
        console.error('Erro ao atualizar tempos no DOM:', error);
    }
}

// ===== CORREÇÃO 3: FUNÇÕES DOS BOTÕES (PAUSAR, FINALIZAR, RETOMAR) =====
async function pausarServicoCorrigido(servicoId) {
    if (!servicoId) {
        alert('ID do serviço não encontrado');
        return;
    }
    
    try {
        console.log(`Pausando serviço ${servicoId}`);
        
        const response = await fetch(`/api/servicos-execucao/${servicoId}/pausar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                motivo: 'Pausado pelo operador'
            })
        });
        
        const data = await response.json();
        
        if (response.ok && (data.success || data.message)) {
            alert('Serviço pausado com sucesso!');
            // Recarregar dados sem reload da página
            await atualizarDashboard();
        } else {
            alert('Erro ao pausar serviço: ' + (data.error || data.message || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao pausar serviço:', error);
        alert('Erro de conexão ao pausar serviço');
    }
}

async function finalizarServicoCorrigido(servicoId) {
    if (!servicoId) {
        alert('ID do serviço não encontrado');
        return;
    }
    
    if (!confirm('Tem certeza que deseja finalizar este serviço?')) {
        return;
    }
    
    try {
        console.log(`Finalizando serviço ${servicoId}`);
        
        const response = await fetch(`/api/servicos-execucao/${servicoId}/finalizar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                observacoes_finais: 'Finalizado pelo operador'
            })
        });
        
        const data = await response.json();
        
        if (response.ok && (data.success || data.message)) {
            alert('Serviço finalizado com sucesso!');
            // Recarregar dados sem reload da página
            await atualizarDashboard();
        } else {
            alert('Erro ao finalizar serviço: ' + (data.error || data.message || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao finalizar serviço:', error);
        alert('Erro de conexão ao finalizar serviço');
    }
}

async function retomarServicoCorrigido(servicoId) {
    if (!servicoId) {
        alert('ID do serviço não encontrado');
        return;
    }
    
    try {
        console.log(`Retomando serviço ${servicoId}`);
        
        const response = await fetch(`/api/servicos-execucao/${servicoId}/retomar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && (data.success || data.message)) {
            alert('Serviço retomado com sucesso!');
            // Recarregar dados sem reload da página
            await atualizarDashboard();
        } else {
            alert('Erro ao retomar serviço: ' + (data.error || data.message || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao retomar serviço:', error);
        alert('Erro de conexão ao retomar serviço');
    }
}

// ===== CORREÇÃO 4: FUNÇÃO PARA IDENTIFICAR E CORRIGIR BOTÕES =====
function corrigirBotoesNoDOM() {
    try {
        // Procurar por todos os botões relacionados a serviços
        const botoes = document.querySelectorAll(
            'button[onclick*="pausar"], button[onclick*="finalizar"], button[onclick*="retomar"], ' +
            '.btn-pause, .btn-finish, .btn-resume, .btn-finalizar, .btn-pausar, .btn-retomar'
        );
        
        botoes.forEach(botao => {
            // Encontrar o ID do serviço no elemento ou elemento pai
            let servicoId = null;
            
            // Método 1: Procurar em data attributes
            servicoId = botao.dataset.servicoId || 
                       botao.dataset.id || 
                       botao.getAttribute('data-servico-id');
            
            // Método 2: Procurar no elemento pai
            if (!servicoId) {
                let elemento = botao.parentElement;
                while (elemento && !servicoId) {
                    servicoId = elemento.dataset.servicoId || 
                               elemento.dataset.id ||
                               elemento.getAttribute('data-servico-id');
                    elemento = elemento.parentElement;
                }
            }
            
            // Método 3: Extrair do onclick existente
            if (!servicoId && botao.getAttribute('onclick')) {
                const match = botao.getAttribute('onclick').match(/\d+/);
                if (match) {
                    servicoId = match[0];
                }
            }
            
            // Método 4: Procurar por ID em classes ou IDs do elemento
            if (!servicoId) {
                const classList = Array.from(botao.classList);
                const idMatch = classList.find(cls => cls.match(/servico-\d+/));
                if (idMatch) {
                    servicoId = idMatch.replace('servico-', '');
                }
            }
            
            if (servicoId) {
                // Remover event listeners antigos
                botao.removeAttribute('onclick');
                
                // Adicionar novos event listeners baseados no tipo do botão
                const texto = botao.textContent.toLowerCase();
                const classes = botao.className.toLowerCase();
                
                if (texto.includes('pausar') || classes.includes('pause')) {
                    botao.onclick = () => pausarServicoCorrigido(servicoId);
                } else if (texto.includes('finalizar') || classes.includes('finish') || classes.includes('finalizar')) {
                    botao.onclick = () => finalizarServicoCorrigido(servicoId);
                } else if (texto.includes('retomar') || classes.includes('resume') || classes.includes('retomar')) {
                    botao.onclick = () => retomarServicoCorrigido(servicoId);
                }
                
                // Adicionar data attribute para futuras referências
                botao.dataset.servicoId = servicoId;
                
                console.log(`Botão corrigido: ${texto} para serviço ${servicoId}`);
            }
        });
        
    } catch (error) {
        console.error('Erro ao corrigir botões:', error);
    }
}

// ===== CORREÇÃO 5: FUNÇÃO PARA ATUALIZAR DASHBOARD SEM RELOAD =====
async function atualizarDashboard() {
    try {
        // Atualizar serviços em execução
        const responseExecucao = await fetch('/api/servicos-execucao');
        if (responseExecucao.ok) {
            const servicosExecucao = await responseExecucao.json();
            // Processar dados de execução
            atualizarServicosExecucao(servicosExecucao);
        }
        
        // Atualizar serviços pausados
        const responsePausados = await fetch('/api/fila-servicos/pausados');
        if (responsePausados.ok) {
            const dadosPausados = await responsePausados.json();
            // Processar dados de pausados
            atualizarServicosPausados(dadosPausados.servicos_pausados || []);
        }
        
        // Atualizar fila
        const responseFila = await fetch('/api/fila-servicos');
        if (responseFila.ok) {
            const fila = await responseFila.json();
            // Processar dados da fila
            atualizarFilaServicos(fila);
        }
        
        // Aplicar correções após atualização
        setTimeout(() => {
            atualizarTemposNoDOM();
            corrigirBotoesNoDOM();
        }, 500);
        
    } catch (error) {
        console.error('Erro ao atualizar dashboard:', error);
    }
}

// ===== CORREÇÃO 6: FUNÇÕES AUXILIARES PARA ATUALIZAÇÃO DE DADOS =====
function atualizarServicosExecucao(servicos) {
    // Implementar atualização dos cards de serviços em execução
    servicos.forEach(servico => {
        const elemento = document.querySelector(`[data-servico-id="${servico.id}"]`);
        if (elemento) {
            // Atualizar tempo decorrido
            const tempoElement = elemento.querySelector('.tempo-decorrido');
            if (tempoElement && servico.tempo_decorrido_formatado) {
                tempoElement.textContent = servico.tempo_decorrido_formatado;
            }
            
            // Atualizar percentual
            const progressElement = elemento.querySelector('.progress-bar');
            if (progressElement && servico.percentual_conclusao !== undefined) {
                progressElement.style.width = `${servico.percentual_conclusao}%`;
                progressElement.setAttribute('aria-valuenow', servico.percentual_conclusao);
            }
        }
    });
}

function atualizarServicosPausados(servicosPausados) {
    let container = document.getElementById('servicos-pausados-container');
    
    if (servicosPausados.length === 0) {
        if (container) {
            container.style.display = 'none';
        }
        return;
    }
    
    if (!container) {
        container = criarContainerServicosPausados();
    }
    
    container.style.display = 'block';
    
    // Atualizar lista de pausados
    const lista = container.querySelector('.servicos-pausados-list');
    if (lista) {
        lista.innerHTML = '';
        
        servicosPausados.forEach(servico => {
            const item = criarItemServicoPausado(servico);
            lista.appendChild(item);
        });
    }
}

function atualizarFilaServicos(filaServicos) {
    // Implementar atualização da fila se necessário
    console.log('Fila atualizada:', filaServicos.length, 'serviços');
}

// ===== CORREÇÃO 7: FUNÇÕES PARA CRIAR ELEMENTOS =====
function criarContainerServicosPausados() {
    const container = document.createElement('div');
    container.id = 'servicos-pausados-container';
    container.className = 'servicos-pausados-section';
    
    const titulo = document.createElement('h3');
    titulo.textContent = 'Serviços Pausados';
    titulo.style.color = '#ff6b35';
    titulo.style.marginBottom = '15px';
    
    const lista = document.createElement('div');
    lista.className = 'servicos-pausados-list';
    lista.style.cssText = `
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    `;
    
    container.appendChild(titulo);
    container.appendChild(lista);
    
    // Inserir no topo da página
    const mainContent = document.querySelector('.main-content') || 
                       document.querySelector('#root') || 
                       document.body;
    mainContent.insertBefore(container, mainContent.firstChild);
    
    return container;
}

function criarItemServicoPausado(servico) {
    const item = document.createElement('div');
    item.className = 'servico-pausado-item';
    item.dataset.servicoId = servico.id;
    item.style.cssText = `
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        margin-bottom: 10px;
        background: white;
        border-radius: 5px;
        border-left: 4px solid #ff6b35;
    `;
    
    const info = document.createElement('div');
    info.innerHTML = `
        <strong>Box ${servico.box_id}</strong> - ${servico.nome_cliente}<br>
        <small>
            Pausado há: ${formatarTempoSeguro(servico.tempo_pausa_atual_minutos)} | 
            Urgência: ${servico.urgencia_pausa || 'normal'}
        </small>
    `;
    
    const acoes = document.createElement('div');
    acoes.style.display = 'flex';
    acoes.style.gap = '10px';
    
    // Botão Retomar
    const btnRetomar = document.createElement('button');
    btnRetomar.textContent = 'Retomar';
    btnRetomar.className = 'btn btn-success btn-sm';
    btnRetomar.dataset.servicoId = servico.id;
    btnRetomar.onclick = () => retomarServicoCorrigido(servico.id);
    
    // Botão Finalizar
    const btnFinalizar = document.createElement('button');
    btnFinalizar.textContent = 'Finalizar';
    btnFinalizar.className = 'btn btn-primary btn-sm';
    btnFinalizar.dataset.servicoId = servico.id;
    btnFinalizar.onclick = () => finalizarServicoCorrigido(servico.id);
    
    acoes.appendChild(btnRetomar);
    acoes.appendChild(btnFinalizar);
    
    item.appendChild(info);
    item.appendChild(acoes);
    
    return item;
}

// ===== CORREÇÃO 8: OBSERVER PARA MONITORAR MUDANÇAS =====
function iniciarObserver() {
    const observer = new MutationObserver((mutations) => {
        let shouldUpdate = false;
        
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Verificar se foram adicionados elementos relevantes
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.querySelector && (
                            node.querySelector('[data-tempo]') ||
                            node.querySelector('button[onclick]') ||
                            node.classList.contains('servico-item') ||
                            node.classList.contains('service-card')
                        )) {
                            shouldUpdate = true;
                        }
                    }
                });
            }
        });
        
        if (shouldUpdate) {
            setTimeout(() => {
                atualizarTemposNoDOM();
                corrigirBotoesNoDOM();
            }, 100);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    return observer;
}

// ===== CORREÇÃO 9: INTERCEPTAR ATUALIZAÇÕES DE REACT/FRAMEWORKS =====
function interceptarAtualizacoes() {
    // Interceptar setInterval que pode estar causando NaN
    const originalSetInterval = window.setInterval;
    window.setInterval = function(callback, delay) {
        const wrappedCallback = function() {
            try {
                callback.apply(this, arguments);
                // Corrigir após cada atualização automática
                atualizarTemposNoDOM();
            } catch (error) {
                console.error('Erro em callback de setInterval:', error);
            }
        };
        return originalSetInterval.call(this, wrappedCallback, delay);
    };
    
    // Interceptar setTimeout também
    const originalSetTimeout = window.setTimeout;
    window.setTimeout = function(callback, delay) {
        const wrappedCallback = function() {
            try {
                callback.apply(this, arguments);
                // Corrigir após timeouts que podem atualizar o DOM
                if (delay > 1000) { // Apenas para timeouts maiores
                    atualizarTemposNoDOM();
                }
            } catch (error) {
                console.error('Erro em callback de setTimeout:', error);
            }
        };
        return originalSetTimeout.call(this, wrappedCallback, delay);
    };
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de correção carregado');
    
    // Aplicar correções iniciais
    setTimeout(() => {
        atualizarTemposNoDOM();
        corrigirBotoesNoDOM();
        atualizarDashboard();
    }, 1000);
    
    // Iniciar monitoramento
    iniciarObserver();
    interceptarAtualizacoes();
    
    // Atualizar periodicamente
    setInterval(() => {
        atualizarTemposNoDOM();
        corrigirBotoesNoDOM();
    }, 5000);
    
    // Atualizar dados completos a cada 30 segundos
    setInterval(atualizarDashboard, 30000);
    
    console.log('Todas as correções foram aplicadas');
});

// ===== ESTILOS CSS =====
const style = document.createElement('style');
style.textContent = `
    .servicos-pausados-section {
        margin-bottom: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    .btn {
        padding: 5px 10px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        text-decoration: none;
        display: inline-block;
        transition: all 0.2s;
    }
    
    .btn-sm {
        padding: 3px 8px;
        font-size: 11px;
    }
    
    .btn-success {
        background-color: #28a745;
        color: white;
    }
    
    .btn-primary {
        background-color: #007bff;
        color: white;
    }
    
    .btn-warning {
        background-color: #ffc107;
        color: black;
    }
    
    .btn:hover {
        opacity: 0.8;
        transform: translateY(-1px);
    }
    
    .btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    .servico-pausado-item {
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Correção para textos com erro */
    .tempo-erro {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Destaque para botões corrigidos */
    .btn[data-servico-id] {
        border: 1px solid rgba(0,0,0,0.1);
    }
`;
document.head.appendChild(style);

// Exportar funções para uso global se necessário
window.formatarTempoSeguro = formatarTempoSeguro;
window.pausarServicoCorrigido = pausarServicoCorrigido;
window.finalizarServicoCorrigido = finalizarServicoCorrigido;
window.retomarServicoCorrigido = retomarServicoCorrigido;
window.atualizarDashboard = atualizarDashboard;
