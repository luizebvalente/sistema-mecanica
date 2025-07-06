// Correções para o Frontend - Sistema de Mecânica
// Este arquivo corrige os problemas com serviços pausados e botão finalizar

// Função para carregar e exibir serviços pausados na gestão da fila
async function carregarServicosPausados() {
    try {
        const response = await fetch('/api/fila-servicos/pausados');
        const data = await response.json();
        
        if (data.success && data.servicos_pausados.length > 0) {
            exibirServicosPausados(data.servicos_pausados);
        }
    } catch (error) {
        console.error('Erro ao carregar serviços pausados:', error);
    }
}

// Função para exibir serviços pausados na interface
function exibirServicosPausados(servicosPausados) {
    // Procurar por container de serviços pausados ou criar um
    let container = document.getElementById('servicos-pausados-container');
    
    if (!container) {
        // Criar container se não existir
        container = document.createElement('div');
        container.id = 'servicos-pausados-container';
        container.className = 'servicos-pausados-section';
        
        // Adicionar título
        const titulo = document.createElement('h3');
        titulo.textContent = 'Serviços Pausados';
        titulo.style.color = '#ff6b35';
        titulo.style.marginBottom = '15px';
        container.appendChild(titulo);
        
        // Inserir no início da página de gestão
        const mainContent = document.querySelector('.main-content') || document.body;
        mainContent.insertBefore(container, mainContent.firstChild);
    }
    
    // Limpar conteúdo anterior
    const existingList = container.querySelector('.servicos-pausados-list');
    if (existingList) {
        existingList.remove();
    }
    
    // Criar lista de serviços pausados
    const lista = document.createElement('div');
    lista.className = 'servicos-pausados-list';
    lista.style.cssText = `
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    `;
    
    servicosPausados.forEach(servico => {
        const item = document.createElement('div');
        item.className = 'servico-pausado-item';
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
            <strong>Box ${servico.box_numero}</strong> - ${servico.cliente_nome}<br>
            <small>Pausado há: ${servico.tempo_pausado_formatado} | Urgência: ${servico.urgencia}</small>
        `;
        
        const acoes = document.createElement('div');
        acoes.style.display = 'flex';
        acoes.style.gap = '10px';
        
        // Botão Retomar
        const btnRetomar = document.createElement('button');
        btnRetomar.textContent = 'Retomar';
        btnRetomar.className = 'btn btn-success btn-sm';
        btnRetomar.onclick = () => retomarServico(servico.id);
        
        // Botão Finalizar
        const btnFinalizar = document.createElement('button');
        btnFinalizar.textContent = 'Finalizar';
        btnFinalizar.className = 'btn btn-primary btn-sm';
        btnFinalizar.onclick = () => finalizarServico(servico.id);
        
        acoes.appendChild(btnRetomar);
        acoes.appendChild(btnFinalizar);
        
        item.appendChild(info);
        item.appendChild(acoes);
        lista.appendChild(item);
    });
    
    container.appendChild(lista);
}

// Função para retomar serviço
async function retomarServico(servicoId) {
    try {
        const response = await fetch(`/api/servicos-execucao/${servicoId}/retomar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Serviço retomado com sucesso!');
            // Recarregar a página ou atualizar a lista
            location.reload();
        } else {
            alert('Erro ao retomar serviço: ' + data.message);
        }
    } catch (error) {
        console.error('Erro ao retomar serviço:', error);
        alert('Erro ao retomar serviço');
    }
}

// Função para finalizar serviço
async function finalizarServico(servicoId) {
    if (!confirm('Tem certeza que deseja finalizar este serviço?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/servicos-execucao/${servicoId}/finalizar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Serviço finalizado com sucesso!');
            // Recarregar a página ou atualizar a lista
            location.reload();
        } else {
            alert('Erro ao finalizar serviço: ' + data.message);
        }
    } catch (error) {
        console.error('Erro ao finalizar serviço:', error);
        alert('Erro ao finalizar serviço');
    }
}

// Função para melhorar a seção de execução
function melhorarSecaoExecucao() {
    // Verificar se estamos na seção de execução
    const execucaoSection = document.querySelector('[data-section="execucao"]') || 
                           document.querySelector('.execucao-section');
    
    if (!execucaoSection) return;
    
    // Adicionar botões de ação para serviços em execução
    const servicosEmExecucao = document.querySelectorAll('.servico-em-execucao');
    
    servicosEmExecucao.forEach(servicoElement => {
        // Verificar se já tem botões
        if (servicoElement.querySelector('.acoes-servico')) return;
        
        const acoesDiv = document.createElement('div');
        acoesDiv.className = 'acoes-servico';
        acoesDiv.style.cssText = `
            margin-top: 10px;
            display: flex;
            gap: 10px;
        `;
        
        // Extrair ID do serviço (assumindo que está em um atributo data)
        const servicoId = servicoElement.dataset.servicoId;
        
        if (servicoId) {
            // Botão Pausar
            const btnPausar = document.createElement('button');
            btnPausar.textContent = 'Pausar';
            btnPausar.className = 'btn btn-warning btn-sm';
            btnPausar.onclick = () => pausarServico(servicoId);
            
            // Botão Finalizar
            const btnFinalizar = document.createElement('button');
            btnFinalizar.textContent = 'Finalizar';
            btnFinalizar.className = 'btn btn-success btn-sm';
            btnFinalizar.onclick = () => finalizarServico(servicoId);
            
            acoesDiv.appendChild(btnPausar);
            acoesDiv.appendChild(btnFinalizar);
            
            servicoElement.appendChild(acoesDiv);
        }
    });
}

// Função para pausar serviço
async function pausarServico(servicoId) {
    try {
        const response = await fetch(`/api/servicos-execucao/${servicoId}/pausar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Serviço pausado com sucesso!');
            location.reload();
        } else {
            alert('Erro ao pausar serviço: ' + data.message);
        }
    } catch (error) {
        console.error('Erro ao pausar serviço:', error);
        alert('Erro ao pausar serviço');
    }
}

// Função para monitorar mudanças de seção e aplicar correções
function monitorarSecoes() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                // Verificar se estamos na gestão de fila
                if (document.querySelector('[data-section="gestao"]') || 
                    window.location.hash.includes('gestao') ||
                    document.title.includes('Gestão')) {
                    setTimeout(carregarServicosPausados, 500);
                }
                
                // Verificar se estamos na execução
                if (document.querySelector('[data-section="execucao"]') || 
                    window.location.hash.includes('execucao') ||
                    document.title.includes('Execução')) {
                    setTimeout(melhorarSecaoExecucao, 500);
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Inicializar correções quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('Frontend Fix carregado');
    
    // Aplicar correções imediatamente
    setTimeout(() => {
        carregarServicosPausados();
        melhorarSecaoExecucao();
    }, 1000);
    
    // Monitorar mudanças
    monitorarSecoes();
    
    // Recarregar serviços pausados a cada 30 segundos
    setInterval(carregarServicosPausados, 30000);
});

// Adicionar estilos CSS
const style = document.createElement('style');
style.textContent = `
    .servicos-pausados-section {
        margin-bottom: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .btn {
        padding: 5px 10px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        text-decoration: none;
        display: inline-block;
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
    }
`;
document.head.appendChild(style);

