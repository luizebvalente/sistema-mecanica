import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Clock, Play, Pause, Square, AlertTriangle, CheckCircle } from 'lucide-react'
import './App.css'

// Configuração da API
const API_BASE_URL = 'http://localhost:5000/api'

function App() {
  const [servicosGestao, setServicosGestao] = useState([])
  const [tempoReal, setTempoReal] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Buscar dados da gestão da fila
  const fetchServicosGestao = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/fila-servicos/gestao`)
      if (!response.ok) throw new Error('Erro ao buscar serviços')
      const data = await response.json()
      setServicosGestao(data)
    } catch (err) {
      setError(err.message)
    }
  }

  // Buscar tempo real dos serviços
  const fetchTempoReal = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/servicos-execucao/tempo-real`)
      if (!response.ok) throw new Error('Erro ao buscar tempo real')
      const data = await response.json()
      
      // Converter array para objeto indexado por ID
      const tempoRealMap = {}
      data.forEach(servico => {
        tempoRealMap[servico.id] = servico.tempo_real
      })
      setTempoReal(tempoRealMap)
    } catch (err) {
      console.error('Erro ao buscar tempo real:', err)
    }
  }

  // Inicializar dados
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await fetchServicosGestao()
      await fetchTempoReal()
      setLoading(false)
    }
    
    loadData()
  }, [])

  // Atualizar tempo real a cada segundo
  useEffect(() => {
    const interval = setInterval(() => {
      fetchTempoReal()
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  // Atualizar lista de serviços a cada 30 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      fetchServicosGestao()
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  // Iniciar serviço da fila
  const iniciarServico = async (servicoId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/fila-servicos/${servicoId}/iniciar`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Erro ao iniciar serviço')
      await fetchServicosGestao()
      await fetchTempoReal()
    } catch (err) {
      alert('Erro ao iniciar serviço: ' + err.message)
    }
  }

  // Retomar serviço pausado
  const retomarServico = async (servicoId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/servicos-execucao/${servicoId}/retomar`, {
        method: 'PUT'
      })
      if (!response.ok) throw new Error('Erro ao retomar serviço')
      await fetchServicosGestao()
      await fetchTempoReal()
    } catch (err) {
      alert('Erro ao retomar serviço: ' + err.message)
    }
  }

  // Pausar serviço
  const pausarServico = async (servicoId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/servicos-execucao/${servicoId}/pausar`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          motivo: 'Pausado pelo dashboard'
        })
      })
      if (!response.ok) throw new Error('Erro ao pausar serviço')
      await fetchServicosGestao()
      await fetchTempoReal()
    } catch (err) {
      alert('Erro ao pausar serviço: ' + err.message)
    }
  }

  // Finalizar serviço
  const finalizarServico = async (servicoId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/servicos-execucao/${servicoId}/finalizar`, {
        method: 'PUT'
      })
      if (!response.ok) throw new Error('Erro ao finalizar serviço')
      await fetchServicosGestao()
      await fetchTempoReal()
    } catch (err) {
      alert('Erro ao finalizar serviço: ' + err.message)
    }
  }

  // Formatar tempo em segundos para HH:MM:SS
  const formatarTempo = (segundos) => {
    const horas = Math.floor(Math.abs(segundos) / 3600)
    const minutos = Math.floor((Math.abs(segundos) % 3600) / 60)
    const segs = Math.abs(segundos) % 60
    const sinal = segundos < 0 ? '-' : ''
    return `${sinal}${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`
  }

  // Obter cor do badge baseado no status
  const getStatusColor = (tipoItem, status) => {
    if (tipoItem === 'fila') return 'secondary'
    if (tipoItem === 'pausado') return 'destructive'
    if (status === 'em_andamento') return 'default'
    return 'secondary'
  }

  // Obter texto do status
  const getStatusText = (tipoItem, status) => {
    if (tipoItem === 'fila') return 'Na Fila'
    if (tipoItem === 'pausado') return 'Pausado'
    if (status === 'em_andamento') return 'Em Andamento'
    return status
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Clock className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-4" />
          <p className="text-destructive">Erro: {error}</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            Tentar Novamente
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Sistema de Mecânica - Dashboard
          </h1>
          <p className="text-muted-foreground">
            Gestão de filas e monitoramento em tempo real
          </p>
        </div>

        {servicosGestao.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <CheckCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Nenhum serviço na fila</h3>
              <p className="text-muted-foreground">
                Todos os boxes estão livres ou não há serviços agendados.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {servicosGestao.map((servico) => {
              const tempoRealServico = tempoReal[servico.id]
              const isEmAndamento = servico.status === 'em_andamento'
              const isPausado = servico.tipo_item === 'pausado'
              
              return (
                <Card key={`${servico.tipo_item}-${servico.id}`} className="overflow-hidden">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <CardTitle className="text-lg">
                          Box {servico.box?.nome || servico.box_id}
                        </CardTitle>
                        <Badge variant={getStatusColor(servico.tipo_item, servico.status)}>
                          {getStatusText(servico.tipo_item, servico.status)}
                        </Badge>
                      </div>
                      
                      {/* Cronômetro em tempo real */}
                      {tempoRealServico && (
                        <div className="text-right">
                          <div className={`text-2xl font-mono font-bold ${
                            tempoRealServico.em_atraso ? 'text-destructive' : 'text-foreground'
                          }`}>
                            {formatarTempo(tempoRealServico.tempo_decorrido_segundos)}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {tempoRealServico.em_atraso ? (
                              <span className="text-destructive">
                                Atraso: {formatarTempo(tempoRealServico.atraso_segundos)}
                              </span>
                            ) : (
                              <span>
                                Restante: {formatarTempo(tempoRealServico.tempo_restante_segundos)}
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <h4 className="font-semibold mb-2">Cliente</h4>
                        <p className="text-sm">{servico.nome_cliente}</p>
                        {servico.telefone_cliente && (
                          <p className="text-sm text-muted-foreground">{servico.telefone_cliente}</p>
                        )}
                      </div>
                      
                      <div>
                        <h4 className="font-semibold mb-2">Veículo</h4>
                        <p className="text-sm">
                          {servico.marca_carro} {servico.modelo_carro}
                        </p>
                        {servico.cor_carro && (
                          <p className="text-sm text-muted-foreground">
                            Cor: {servico.cor_carro}
                          </p>
                        )}
                        {servico.placa_carro && (
                          <p className="text-sm text-muted-foreground">
                            Placa: {servico.placa_carro}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <h4 className="font-semibold mb-2">Serviço</h4>
                        <p className="text-sm">{servico.tipo_servico?.nome || 'N/A'}</p>
                        <p className="text-sm text-muted-foreground">
                          Mecânico: {servico.mecanico?.nome || 'N/A'}
                        </p>
                      </div>
                      
                      {tempoRealServico && (
                        <div>
                          <h4 className="font-semibold mb-2">Progresso</h4>
                          <div className="w-full bg-secondary rounded-full h-2 mb-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-1000 ${
                                tempoRealServico.em_atraso ? 'bg-destructive' : 'bg-primary'
                              }`}
                              style={{ 
                                width: `${Math.min(100, tempoRealServico.percentual_concluido)}%` 
                              }}
                            />
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {tempoRealServico.percentual_concluido}% concluído
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Botões de ação */}
                    <div className="flex gap-2 flex-wrap">
                      {servico.tipo_item === 'fila' && servico.pode_iniciar && (
                        <Button 
                          onClick={() => iniciarServico(servico.id)}
                          size="sm"
                          className="flex items-center gap-2"
                        >
                          <Play className="h-4 w-4" />
                          Iniciar
                        </Button>
                      )}
                      
                      {servico.tipo_item === 'pausado' && servico.pode_retomar && (
                        <Button 
                          onClick={() => retomarServico(servico.id)}
                          size="sm"
                          className="flex items-center gap-2"
                        >
                          <Play className="h-4 w-4" />
                          Retomar
                        </Button>
                      )}
                      
                      {isEmAndamento && (
                        <>
                          <Button 
                            onClick={() => pausarServico(servico.id)}
                            size="sm"
                            variant="outline"
                            className="flex items-center gap-2"
                          >
                            <Pause className="h-4 w-4" />
                            Pausar
                          </Button>
                          
                          <Button 
                            onClick={() => finalizarServico(servico.id)}
                            size="sm"
                            variant="outline"
                            className="flex items-center gap-2"
                          >
                            <Square className="h-4 w-4" />
                            Finalizar
                          </Button>
                        </>
                      )}
                    </div>

                    {/* Informações adicionais para serviços pausados */}
                    {isPausado && servico.tempo_pausa_atual_minutos && (
                      <div className="mt-4 p-3 bg-destructive/10 rounded-lg">
                        <p className="text-sm text-destructive">
                          <Clock className="h-4 w-4 inline mr-1" />
                          Pausado há {servico.tempo_pausa_atual_minutos} minutos
                        </p>
                        {servico.motivo_pausa && (
                          <p className="text-sm text-muted-foreground mt-1">
                            Motivo: {servico.motivo_pausa}
                          </p>
                        )}
                      </div>
                    )}

                    {servico.observacoes && (
                      <div className="mt-4 p-3 bg-muted rounded-lg">
                        <h5 className="font-semibold text-sm mb-1">Observações</h5>
                        <p className="text-sm text-muted-foreground">{servico.observacoes}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default App

