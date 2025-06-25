import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Settings, 
  Users, 
  Car, 
  Wrench, 
  Plus, 
  Clock, 
  Phone,
  Calendar,
  BarChart3,
  Home,
  CheckCircle,
  Building,
  UserCheck,
  Cog,
  Edit,
  Trash2,
  Save,
  Database
} from 'lucide-react';
import './App.css';

// Configuração da API
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://sistema-mecanica.onrender.com/api' 
  : 'http://localhost:5000/api';

// Componente do Painel Principal
const PainelPrincipal = () => {
  const [painelData, setPainelData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPainelData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/painel`);
        const data = await response.json();
        setPainelData(data);
      } catch (error) {
        console.error('Erro ao buscar dados do painel:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPainelData();
    const interval = setInterval(fetchPainelData, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatarTempo = (segundos, emAtraso) => {
    const absSegundos = Math.abs(segundos);
    const minutos = Math.floor(absSegundos / 60);
    const segs = absSegundos % 60;
    const tempo = `${String(minutos).padStart(2, '0')}:${String(segs).padStart(2, '0')}`;
    
    if (emAtraso) {
      return `-${tempo}`;
    }
    return tempo;
  };

  const finalizarServico = async (servicoId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/servicos-execucao/${servicoId}/finalizar`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Atualizar dados do painel imediatamente
        const painelResponse = await fetch(`${API_BASE_URL}/painel`);
        const data = await painelResponse.json();
        setPainelData(data);
        
        alert('Serviço finalizado com sucesso!');
      } else {
        throw new Error('Erro ao finalizar serviço');
      }
    } catch (error) {
      console.error('Erro ao finalizar serviço:', error);
      alert('Erro ao finalizar serviço. Tente novamente.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando painel...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Painel em Tempo Real</h1>
        <Badge variant="outline" className="text-green-600">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          Atualização automática
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {painelData.map((box) => (
          <Card key={box.box.id} className={`${
            box.servico_atual ? 'border-orange-500 bg-orange-50' : 'border-green-500 bg-green-50'
          }`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-bold">
                  {box.box.numero}
                </CardTitle>
                <Badge variant={box.servico_atual ? 'destructive' : 'secondary'}>
                  {box.servico_atual ? 'Ocupado' : 'Livre'}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {box.servico_atual ? (
                <>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      <span className="font-medium">{box.servico_atual.mecanico.nome}</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Wrench className="w-4 h-4" />
                      <span>{box.servico_atual.tipo_servico.nome}</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Car className="w-4 h-4" />
                      <span>{box.servico_atual.nome_cliente}</span>
                    </div>

                    {box.servico_atual.telefone_cliente && (
                      <div className="flex items-center gap-2">
                        <Phone className="w-4 h-4" />
                        <span className="text-blue-600 font-medium">
                          {box.servico_atual.telefone_cliente}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="text-center p-4 rounded-lg bg-white border">
                    {box.em_atraso ? (
                      <>
                        <div className={`text-3xl font-bold text-red-600 mb-2 cronometro-atraso`}>
                          {formatarTempo(box.tempo_restante_segundos, true)}
                        </div>
                        <div className="text-red-600 font-bold text-sm">
                          EM ATRASO
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="text-3xl font-bold text-green-600 mb-2 cronometro-normal">
                          {formatarTempo(box.tempo_restante_segundos, false)}
                        </div>
                        <div className="text-gray-600 text-sm">
                          Tempo restante
                        </div>
                      </>
                    )}
                  </div>

                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Início: {box.horario_inicio}</span>
                    <span>Fim: {box.horario_fim_previsto}</span>
                  </div>

                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => finalizarServico(box.servico_atual.id)}
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Finalizar Serviço
                  </Button>
                </>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Car className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Box disponível</p>
                </div>
              )}

              {box.fila_servicos && box.fila_servicos.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Fila ({box.total_fila})
                  </h4>
                  <div className="space-y-2">
                    {box.fila_servicos.slice(0, 3).map((fila, index) => (
                      <div key={fila.id} className="text-sm p-2 bg-gray-50 rounded">
                        <div className="flex justify-between items-center">
                          <span className="font-medium">{fila.nome_cliente}</span>
                          <Badge variant="outline" className="text-xs">
                            #{index + 1}
                          </Badge>
                        </div>
                        {fila.telefone_cliente && (
                          <div className="flex items-center gap-1 mt-1">
                            <Phone className="w-3 h-3" />
                            <span className="text-blue-600">{fila.telefone_cliente}</span>
                          </div>
                        )}
                        <div className="text-gray-600">{fila.tipo_servico?.nome}</div>
                      </div>
                    ))}
                    {box.total_fila > 3 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{box.total_fila - 3} mais na fila
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Componente de Cadastro de Boxes/Elevadores
const CadastroBoxes = () => {
  const [boxes, setBoxes] = useState([]);
  const [novoBox, setNovoBox] = useState({ numero: '', tipo: 'box' });
  const [editandoBox, setEditandoBox] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarBoxes();
  }, []);

  const carregarBoxes = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/boxes`);
      const data = await response.json();
      setBoxes(data);
    } catch (error) {
      console.error('Erro ao carregar boxes:', error);
    } finally {
      setLoading(false);
    }
  };

  const salvarBox = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/boxes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(novoBox)
      });

      if (response.ok) {
        alert('Box cadastrado com sucesso!');
        setNovoBox({ numero: '', tipo: 'box' });
        carregarBoxes();
      } else {
        const errorData = await response.json();
        alert(`Erro ao cadastrar box: ${errorData.error || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro ao salvar box:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  const editarBox = async (id, dadosAtualizados) => {
    try {
      const response = await fetch(`${API_BASE_URL}/boxes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dadosAtualizados)
      });

      if (response.ok) {
        alert('Box atualizado com sucesso!');
        setEditandoBox(null);
        carregarBoxes();
      } else {
        alert('Erro ao atualizar box');
      }
    } catch (error) {
      console.error('Erro ao editar box:', error);
    }
  };

  const excluirBox = async (id) => {
    if (confirm('Tem certeza que deseja excluir este box?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/boxes/${id}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          alert('Box excluído com sucesso!');
          carregarBoxes();
        } else {
          alert('Erro ao excluir box');
        }
      } catch (error) {
        console.error('Erro ao excluir box:', error);
      }
    }
  };

  const getCorPorTipo = (tipo) => {
    return tipo === 'elevador' 
      ? 'border-purple-500 bg-purple-50' 
      : 'border-blue-500 bg-blue-50';
  };

  const getIconePorTipo = (tipo) => {
    return tipo === 'elevador' ? '🏗️' : '🏢';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Carregando...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Building className="w-8 h-8" />
          Cadastro de Boxes/Elevadores
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Novo Box/Elevador</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={salvarBox} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Número/Nome *
                </label>
                <Input
                  type="text"
                  placeholder="Ex: Box 01, Elevador A, Vaga 1"
                  value={novoBox.numero}
                  onChange={(e) => setNovoBox({...novoBox, numero: e.target.value})}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Tipo *
                </label>
                <select
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={novoBox.tipo}
                  onChange={(e) => setNovoBox({...novoBox, tipo: e.target.value})}
                  required
                >
                  <option value="box">🏢 Box</option>
                  <option value="elevador">🏗️ Elevador</option>
                </select>
              </div>
            </div>
            <Button type="submit" className="w-full">
              <Plus className="w-4 h-4 mr-2" />
              Cadastrar {novoBox.tipo === 'elevador' ? 'Elevador' : 'Box'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Boxes/Elevadores Cadastrados ({boxes.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {boxes.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Nenhum box cadastrado ainda. Cadastre o primeiro box acima.
            </p>
          ) : (
            <div className="space-y-2">
              {boxes.map((box) => (
                <div key={box.id} className={`flex items-center justify-between p-4 border-2 rounded-lg ${getCorPorTipo(box.tipo)}`}>
                  {editandoBox === box.id ? (
                    <div className="flex items-center gap-2 flex-1">
                      <Input
                        defaultValue={box.numero}
                        onBlur={(e) => editarBox(box.id, { numero: e.target.value, tipo: box.tipo })}
                        className="flex-1"
                      />
                      <select
                        defaultValue={box.tipo}
                        onChange={(e) => editarBox(box.id, { numero: box.numero, tipo: e.target.value })}
                        className="p-2 border border-gray-300 rounded-md"
                      >
                        <option value="box">🏢 Box</option>
                        <option value="elevador">🏗️ Elevador</option>
                      </select>
                      <Button
                        size="sm"
                        onClick={() => setEditandoBox(null)}
                        variant="outline"
                      >
                        <Save className="w-4 h-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-3">
                        <div className="text-2xl">{getIconePorTipo(box.tipo)}</div>
                        <div>
                          <div className="font-medium text-lg">{box.numero}</div>
                          <div className="text-sm text-gray-600">
                            <Badge variant={box.tipo === 'elevador' ? 'secondary' : 'default'} className="mr-2">
                              {box.tipo === 'elevador' ? 'Elevador' : 'Box'}
                            </Badge>
                            Status: {box.status === 'livre' ? 'Livre' : 'Ocupado'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditandoBox(box.id)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => excluirBox(box.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Componente de Cadastro de Mecânicos
const CadastroMecanicos = () => {
  const [mecanicos, setMecanicos] = useState([]);
  const [novoMecanico, setNovoMecanico] = useState({ nome: '', especialidade: '' });
  const [editandoMecanico, setEditandoMecanico] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarMecanicos();
  }, []);

  const carregarMecanicos = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/mecanicos`);
      const data = await response.json();
      setMecanicos(data);
    } catch (error) {
      console.error('Erro ao carregar mecânicos:', error);
    } finally {
      setLoading(false);
    }
  };

  const salvarMecanico = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/mecanicos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(novoMecanico)
      });

      if (response.ok) {
        alert('Mecânico cadastrado com sucesso!');
        setNovoMecanico({ nome: '', especialidade: '' });
        carregarMecanicos();
      } else {
        alert('Erro ao cadastrar mecânico');
      }
    } catch (error) {
      console.error('Erro ao salvar mecânico:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  const editarMecanico = async (id, dadosAtualizados) => {
    try {
      const response = await fetch(`${API_BASE_URL}/mecanicos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dadosAtualizados)
      });

      if (response.ok) {
        alert('Mecânico atualizado com sucesso!');
        setEditandoMecanico(null);
        carregarMecanicos();
      } else {
        alert('Erro ao atualizar mecânico');
      }
    } catch (error) {
      console.error('Erro ao editar mecânico:', error);
    }
  };

  const excluirMecanico = async (id) => {
    if (confirm('Tem certeza que deseja excluir este mecânico?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/mecanicos/${id}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          alert('Mecânico excluído com sucesso!');
          carregarMecanicos();
        } else {
          alert('Erro ao excluir mecânico');
        }
      } catch (error) {
        console.error('Erro ao excluir mecânico:', error);
      }
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Carregando...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <UserCheck className="w-8 h-8" />
          Cadastro de Mecânicos
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Novo Mecânico</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={salvarMecanico} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Nome Completo *
                </label>
                <Input
                  type="text"
                  placeholder="Ex: João Silva"
                  value={novoMecanico.nome}
                  onChange={(e) => setNovoMecanico({...novoMecanico, nome: e.target.value})}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Especialidade
                </label>
                <Input
                  type="text"
                  placeholder="Ex: Motor, Freios, Suspensão"
                  value={novoMecanico.especialidade}
                  onChange={(e) => setNovoMecanico({...novoMecanico, especialidade: e.target.value})}
                />
              </div>
            </div>
            <Button type="submit" className="w-full">
              <Plus className="w-4 h-4 mr-2" />
              Cadastrar Mecânico
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Mecânicos Cadastrados ({mecanicos.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {mecanicos.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Nenhum mecânico cadastrado ainda. Cadastre o primeiro mecânico acima.
            </p>
          ) : (
            <div className="space-y-2">
              {mecanicos.map((mecanico) => (
                <div key={mecanico.id} className="flex items-center justify-between p-3 border rounded-lg">
                  {editandoMecanico === mecanico.id ? (
                    <div className="flex items-center gap-2 flex-1">
                      <Input
                        defaultValue={mecanico.nome}
                        placeholder="Nome"
                        className="flex-1"
                        onBlur={(e) => editarMecanico(mecanico.id, { 
                          nome: e.target.value, 
                          especialidade: mecanico.especialidade 
                        })}
                      />
                      <Input
                        defaultValue={mecanico.especialidade}
                        placeholder="Especialidade"
                        className="flex-1"
                        onBlur={(e) => editarMecanico(mecanico.id, { 
                          nome: mecanico.nome, 
                          especialidade: e.target.value 
                        })}
                      />
                      <Button
                        size="sm"
                        onClick={() => setEditandoMecanico(null)}
                        variant="outline"
                      >
                        <Save className="w-4 h-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-3">
                        <UserCheck className="w-5 h-5 text-green-600" />
                        <div>
                          <div className="font-medium">{mecanico.nome}</div>
                          <div className="text-sm text-gray-500">
                            {mecanico.especialidade || 'Sem especialidade definida'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditandoMecanico(mecanico.id)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => excluirMecanico(mecanico.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Componente de Cadastro de Tipos de Serviço
const CadastroTiposServico = () => {
  const [tiposServico, setTiposServico] = useState([]);
  const [novoTipo, setNovoTipo] = useState({ 
    nome: '', 
    tempo_estimado: '', 
    descricao: '' 
  });
  const [editandoTipo, setEditandoTipo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarTiposServico();
  }, []);

  const carregarTiposServico = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tipos-servico`);
      const data = await response.json();
      setTiposServico(data);
    } catch (error) {
      console.error('Erro ao carregar tipos de serviço:', error);
    } finally {
      setLoading(false);
    }
  };

  const salvarTipoServico = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/tipos-servico`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...novoTipo,
          tempo_estimado: parseInt(novoTipo.tempo_estimado)
        })
      });

      if (response.ok) {
        alert('Tipo de serviço cadastrado com sucesso!');
        setNovoTipo({ nome: '', tempo_estimado: '', descricao: '' });
        carregarTiposServico();
      } else {
        alert('Erro ao cadastrar tipo de serviço');
      }
    } catch (error) {
      console.error('Erro ao salvar tipo de serviço:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  const editarTipoServico = async (id, dadosAtualizados) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tipos-servico/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...dadosAtualizados,
          tempo_estimado: parseInt(dadosAtualizados.tempo_estimado)
        })
      });

      if (response.ok) {
        alert('Tipo de serviço atualizado com sucesso!');
        setEditandoTipo(null);
        carregarTiposServico();
      } else {
        alert('Erro ao atualizar tipo de serviço');
      }
    } catch (error) {
      console.error('Erro ao editar tipo de serviço:', error);
    }
  };

  const excluirTipoServico = async (id) => {
    if (confirm('Tem certeza que deseja excluir este tipo de serviço?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/tipos-servico/${id}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          alert('Tipo de serviço excluído com sucesso!');
          carregarTiposServico();
        } else {
          alert('Erro ao excluir tipo de serviço');
        }
      } catch (error) {
        console.error('Erro ao excluir tipo de serviço:', error);
      }
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Carregando...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Cog className="w-8 h-8" />
          Cadastro de Tipos de Serviço
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Novo Tipo de Serviço</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={salvarTipoServico} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Nome do Serviço *
                </label>
                <Input
                  type="text"
                  placeholder="Ex: Troca de Óleo, Alinhamento"
                  value={novoTipo.nome}
                  onChange={(e) => setNovoTipo({...novoTipo, nome: e.target.value})}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Tempo Estimado (minutos) *
                </label>
                <Input
                  type="number"
                  placeholder="Ex: 30, 60, 120"
                  value={novoTipo.tempo_estimado}
                  onChange={(e) => setNovoTipo({...novoTipo, tempo_estimado: e.target.value})}
                  required
                  min="1"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Descrição
              </label>
              <Textarea
                placeholder="Descrição detalhada do serviço..."
                value={novoTipo.descricao}
                onChange={(e) => setNovoTipo({...novoTipo, descricao: e.target.value})}
                rows={3}
              />
            </div>
            <Button type="submit" className="w-full">
              <Plus className="w-4 h-4 mr-2" />
              Cadastrar Tipo de Serviço
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tipos de Serviço Cadastrados ({tiposServico.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {tiposServico.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Nenhum tipo de serviço cadastrado ainda. Cadastre o primeiro tipo acima.
            </p>
          ) : (
            <div className="space-y-2">
              {tiposServico.map((tipo) => (
                <div key={tipo.id} className="flex items-center justify-between p-3 border rounded-lg">
                  {editandoTipo === tipo.id ? (
                    <div className="space-y-2 flex-1">
                      <div className="flex gap-2">
                        <Input
                          defaultValue={tipo.nome}
                          placeholder="Nome do serviço"
                          className="flex-1"
                        />
                        <Input
                          defaultValue={tipo.tempo_estimado}
                          placeholder="Tempo (min)"
                          type="number"
                          className="w-32"
                        />
                      </div>
                      <Textarea
                        defaultValue={tipo.descricao}
                        placeholder="Descrição"
                        rows={2}
                      />
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => setEditandoTipo(null)}
                          variant="outline"
                        >
                          <Save className="w-4 h-4 mr-1" />
                          Salvar
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => setEditandoTipo(null)}
                          variant="ghost"
                        >
                          Cancelar
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-3 flex-1">
                        <Cog className="w-5 h-5 text-purple-600" />
                        <div className="flex-1">
                          <div className="font-medium">{tipo.nome}</div>
                          <div className="text-sm text-gray-500">
                            Tempo estimado: {tipo.tempo_estimado} minutos
                          </div>
                          {tipo.descricao && (
                            <div className="text-sm text-gray-600 mt-1">
                              {tipo.descricao}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditandoTipo(tipo.id)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => excluirTipoServico(tipo.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Componente de Agendamento com Data/Hora
const IniciarServico = () => {
  const [formData, setFormData] = useState({
    box_id: '',
    mecanico_id: '',
    tipo_servico_id: '',
    nome_cliente: '',
    telefone_cliente: '',
    marca_carro: '',
    modelo_carro: '',
    cor_carro: '',
    placa_carro: '',
    data_agendamento: '',
    horario_agendamento: '',
    tempo_extra_minutos: 0,
    motivo_tempo_extra: '',
    observacoes: ''
  });

  const [boxes, setBoxes] = useState([]);
  const [mecanicos, setMecanicos] = useState([]);
  const [tiposServico, setTiposServico] = useState([]);
  const [marcas, setMarcas] = useState([]);
  const [modelos, setModelos] = useState([]);

  useEffect(() => {
    const carregarDados = async () => {
      try {
        const [boxesRes, mecanicosRes, tiposRes] = await Promise.all([
          fetch(`${API_BASE_URL}/boxes`),
          fetch(`${API_BASE_URL}/mecanicos`),
          fetch(`${API_BASE_URL}/tipos-servico`)
        ]);

        setBoxes(await boxesRes.json());
        setMecanicos(await mecanicosRes.json());
        setTiposServico(await tiposRes.json());
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      }
    };

    carregarDados();
  }, []);

  const carregarMarcas = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/carros/popular-marcas`, {
        method: 'POST'
      });
      const data = await response.json();
      setMarcas(data.marcas || []);
    } catch (error) {
      console.error('Erro ao carregar marcas:', error);
    }
  };

  const carregarModelos = async (marca) => {
    try {
      const response = await fetch(`${API_BASE_URL}/carros/modelos/${marca}`);
      const data = await response.json();
      setModelos(data.modelos || []);
    } catch (error) {
      console.error('Erro ao carregar modelos:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/fila-servicos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Serviço iniciado/agendado com sucesso!');
        setFormData({
          box_id: '',
          mecanico_id: '',
          tipo_servico_id: '',
          nome_cliente: '',
          telefone_cliente: '',
          marca_carro: '',
          modelo_carro: '',
          cor_carro: '',
          placa_carro: '',
          data_agendamento: '',
          horario_agendamento: '',
          tempo_extra_minutos: 0,
          motivo_tempo_extra: '',
          observacoes: ''
        });
      } else {
        alert('Erro ao iniciar serviço');
      }
    } catch (error) {
      console.error('Erro ao enviar dados:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Iniciar Novo Serviço</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Dados do Serviço</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Box/Elevador</label>
              <select 
                className="w-full p-2 border rounded-md"
                value={formData.box_id}
                onChange={(e) => setFormData({...formData, box_id: e.target.value})}
                required
              >
                <option value="">Selecione o box</option>
                {boxes.map(box => (
                  <option key={box.id} value={box.id}>
                    {box.numero} - {box.status === 'livre' ? 'Livre' : 'Ocupado'}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Mecânico</label>
              <select 
                className="w-full p-2 border rounded-md"
                value={formData.mecanico_id}
                onChange={(e) => setFormData({...formData, mecanico_id: e.target.value})}
                required
              >
                <option value="">Selecione o mecânico</option>
                {mecanicos.map(mecanico => (
                  <option key={mecanico.id} value={mecanico.id}>
                    {mecanico.nome}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Tipo de Serviço</label>
              <select 
                className="w-full p-2 border rounded-md"
                value={formData.tipo_servico_id}
                onChange={(e) => setFormData({...formData, tipo_servico_id: e.target.value})}
                required
              >
                <option value="">Selecione o serviço</option>
                {tiposServico.map(tipo => (
                  <option key={tipo.id} value={tipo.id}>
                    {tipo.nome} ({tipo.tempo_estimado} min)
                  </option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Agendamento (Opcional)
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Data do Agendamento</label>
              <input 
                type="date"
                className="w-full p-2 border rounded-md"
                value={formData.data_agendamento}
                onChange={(e) => setFormData({...formData, data_agendamento: e.target.value})}
                min={new Date().toISOString().split('T')[0]}
              />
              <p className="text-xs text-gray-500 mt-1">
                Deixe vazio para agendar para hoje
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Horário do Agendamento</label>
              <input 
                type="time"
                className="w-full p-2 border rounded-md"
                value={formData.horario_agendamento}
                onChange={(e) => setFormData({...formData, horario_agendamento: e.target.value})}
              />
              <p className="text-xs text-gray-500 mt-1">
                Deixe vazio para agendamento automático
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dados do Cliente</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Nome do Cliente *</label>
              <input 
                type="text"
                className="w-full p-2 border rounded-md"
                value={formData.nome_cliente}
                onChange={(e) => setFormData({...formData, nome_cliente: e.target.value})}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Telefone</label>
              <input 
                type="tel"
                className="w-full p-2 border rounded-md"
                placeholder="(11) 99999-9999"
                value={formData.telefone_cliente}
                onChange={(e) => setFormData({...formData, telefone_cliente: e.target.value})}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dados do Veículo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2 mb-4">
              <Button 
                type="button" 
                onClick={carregarMarcas}
                variant="outline"
                className="mb-4"
              >
                Popular Marcas e Modelos
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Marca do Carro *</label>
                <select 
                  className="w-full p-2 border rounded-md"
                  value={formData.marca_carro}
                  onChange={(e) => {
                    setFormData({...formData, marca_carro: e.target.value, modelo_carro: ''});
                    if (e.target.value) carregarModelos(e.target.value);
                  }}
                  required
                >
                  <option value="">Selecione a marca</option>
                  {marcas.map(marca => (
                    <option key={marca} value={marca}>{marca}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Modelo do Carro *</label>
                <select 
                  className="w-full p-2 border rounded-md"
                  value={formData.modelo_carro}
                  onChange={(e) => setFormData({...formData, modelo_carro: e.target.value})}
                  required
                >
                  <option value="">Selecione o modelo</option>
                  {modelos.map(modelo => (
                    <option key={modelo} value={modelo}>{modelo}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Cor do Carro</label>
                <input 
                  type="text"
                  className="w-full p-2 border rounded-md"
                  placeholder="Ex: Branco, Preto, Prata"
                  value={formData.cor_carro}
                  onChange={(e) => setFormData({...formData, cor_carro: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Placa</label>
                <input 
                  type="text"
                  className="w-full p-2 border rounded-md"
                  placeholder="ABC-1234"
                  value={formData.placa_carro}
                  onChange={(e) => setFormData({...formData, placa_carro: e.target.value})}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tempo Adicional</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tempo Extra (minutos)</label>
              <input 
                type="number"
                className="w-full p-2 border rounded-md"
                placeholder="0"
                value={formData.tempo_extra_minutos}
                onChange={(e) => setFormData({...formData, tempo_extra_minutos: parseInt(e.target.value) || 0})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Motivo do Tempo Extra</label>
              <input 
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="Ex: Almoço, Pausa, Peça especial"
                value={formData.motivo_tempo_extra}
                onChange={(e) => setFormData({...formData, motivo_tempo_extra: e.target.value})}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Observações</CardTitle>
          </CardHeader>
          <CardContent>
            <textarea 
              className="w-full p-2 border rounded-md"
              rows="3"
              placeholder="Observações adicionais sobre o serviço..."
              value={formData.observacoes}
              onChange={(e) => setFormData({...formData, observacoes: e.target.value})}
            />
          </CardContent>
        </Card>

        <Button type="submit" className="w-full" size="lg">
          <Plus className="w-4 h-4 mr-2" />
          Iniciar Serviço / Adicionar na Fila
        </Button>
      </form>
    </div>
  );
};

// Componente de Relatórios (mantido igual)
const Relatorios = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [servicosConcluidos, setServicosConcluidos] = useState([]);
  const [filasFuturas, setFilasFuturas] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregarRelatorios = async () => {
      try {
        const [dashboardRes, servicosRes, filasRes] = await Promise.all([
          fetch(`${API_BASE_URL}/relatorios/dashboard`),
          fetch(`${API_BASE_URL}/relatorios/servicos-concluidos`),
          fetch(`${API_BASE_URL}/relatorios/filas-futuras`)
        ]);

        setDashboardData(await dashboardRes.json());
        setServicosConcluidos(await servicosRes.json());
        setFilasFuturas(await filasRes.json());
      } catch (error) {
        console.error('Erro ao carregar relatórios:', error);
      } finally {
        setLoading(false);
      }
    };

    carregarRelatorios();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando relatórios...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold flex items-center gap-2">
        <BarChart3 className="w-8 h-8" />
        Relatórios
      </h1>

      <Tabs defaultValue="dashboard" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="concluidos">Serviços Concluídos</TabsTrigger>
          <TabsTrigger value="futuras">Filas Futuras</TabsTrigger>
          <TabsTrigger value="produtividade">Produtividade</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          {dashboardData && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Serviços Hoje</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">
                      {dashboardData.resumo_hoje.servicos_iniciados}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Em Andamento</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-orange-600">
                      {dashboardData.resumo_hoje.servicos_em_andamento}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Filas Agendadas</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-600">
                      {dashboardData.resumo_hoje.filas_agendadas}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Boxes Ocupados</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">
                      {dashboardData.resumo_hoje.boxes_ocupados}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Boxes Livres</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">
                      {dashboardData.resumo_hoje.boxes_livres}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Serviços em Andamento</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {dashboardData.servicos_em_andamento.length > 0 ? (
                      <div className="space-y-2">
                        {dashboardData.servicos_em_andamento.map(servico => (
                          <div key={servico.id} className="p-3 border rounded-lg">
                            <div className="font-medium">{servico.nome_cliente}</div>
                            <div className="text-sm text-gray-600">
                              {servico.tipo_servico?.nome} - {servico.mecanico?.nome}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">Nenhum serviço em andamento</p>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Próximas Filas</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {dashboardData.proximas_filas.length > 0 ? (
                      <div className="space-y-2">
                        {dashboardData.proximas_filas.map(fila => (
                          <div key={fila.id} className="p-3 border rounded-lg">
                            <div className="font-medium">{fila.nome_cliente}</div>
                            <div className="text-sm text-gray-600">
                              {fila.tipo_servico?.nome}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">Nenhuma fila agendada</p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="concluidos">
          <Card>
            <CardHeader>
              <CardTitle>Serviços Concluídos</CardTitle>
            </CardHeader>
            <CardContent>
              {servicosConcluidos.estatisticas && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {servicosConcluidos.estatisticas.total_servicos}
                    </div>
                    <div className="text-sm text-gray-600">Total de Serviços</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {servicosConcluidos.estatisticas.servicos_no_prazo}
                    </div>
                    <div className="text-sm text-gray-600">No Prazo</div>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {servicosConcluidos.estatisticas.servicos_atrasados}
                    </div>
                    <div className="text-sm text-gray-600">Atrasados</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {servicosConcluidos.estatisticas.percentual_no_prazo.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">% No Prazo</div>
                  </div>
                </div>
              )}
              
              {servicosConcluidos.servicos && servicosConcluidos.servicos.length > 0 ? (
                <div className="space-y-2">
                  {servicosConcluidos.servicos.slice(0, 10).map(servico => (
                    <div key={servico.id} className="p-3 border rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium">{servico.nome_cliente}</div>
                          <div className="text-sm text-gray-600">
                            {servico.tipo_servico?.nome} - {servico.mecanico?.nome}
                          </div>
                        </div>
                        <Badge variant={servico.status === 'concluido' ? 'default' : 'secondary'}>
                          {servico.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Nenhum serviço concluído encontrado</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="futuras">
          <Card>
            <CardHeader>
              <CardTitle>Filas Agendadas para Datas Futuras</CardTitle>
            </CardHeader>
            <CardContent>
              {filasFuturas.filas_por_data && Object.keys(filasFuturas.filas_por_data).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(filasFuturas.filas_por_data).map(([data, filas]) => (
                    <div key={data} className="border rounded-lg p-4">
                      <h3 className="font-bold mb-3">
                        {data === 'sem_data' ? 'Sem data específica' : new Date(data).toLocaleDateString('pt-BR')}
                        <Badge variant="outline" className="ml-2">
                          {filas.length} agendamento(s)
                        </Badge>
                      </h3>
                      <div className="space-y-2">
                        {filas.map(fila => (
                          <div key={fila.id} className="p-3 bg-gray-50 rounded">
                            <div className="flex justify-between items-start">
                              <div>
                                <div className="font-medium">{fila.nome_cliente}</div>
                                <div className="text-sm text-gray-600">
                                  {fila.tipo_servico?.nome}
                                </div>
                                {fila.telefone_cliente && (
                                  <div className="text-sm text-blue-600">
                                    📞 {fila.telefone_cliente}
                                  </div>
                                )}
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-gray-500">
                                  Posição: #{fila.posicao_fila}
                                </div>
                                {fila.horario_agendamento && (
                                  <div className="text-sm text-gray-500">
                                    {fila.horario_agendamento}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Nenhuma fila agendada para datas futuras</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="produtividade">
          <Card>
            <CardHeader>
              <CardTitle>Produtividade dos Mecânicos</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-500">Relatório de produtividade em desenvolvimento...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Componente de Navegação Atualizado
const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Painel Principal', icon: Home },
    { path: '/iniciar-servico', label: 'Iniciar Serviço', icon: Plus },
    { path: '/relatorios', label: 'Relatórios', icon: BarChart3 },
  ];

  const cadastroItems = [
    { path: '/cadastros/boxes', label: 'Boxes/Elevadores', icon: Building },
    { path: '/cadastros/mecanicos', label: 'Mecânicos', icon: UserCheck },
    { path: '/cadastros/tipos-servico', label: 'Tipos de Serviço', icon: Cog },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-8 h-8 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">
              Sistema de Mecânica
            </h1>
          </div>
          <Badge variant="outline" className="text-green-600">
            Sistema Online
          </Badge>
        </div>

        <div className="flex space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
          
          {/* Dropdown de Cadastros */}
          <div className="relative group">
            <button className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100">
              <Database className="w-4 h-4" />
              <span>Cadastros</span>
            </button>
            
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              {cadastroItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-100 ${
                      isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Componente Principal da Aplicação
function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<PainelPrincipal />} />
            <Route path="/iniciar-servico" element={<IniciarServico />} />
            <Route path="/relatorios" element={<Relatorios />} />
            <Route path="/cadastros/boxes" element={<CadastroBoxes />} />
            <Route path="/cadastros/mecanicos" element={<CadastroMecanicos />} />
            <Route path="/cadastros/tipos-servico" element={<CadastroTiposServico />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

