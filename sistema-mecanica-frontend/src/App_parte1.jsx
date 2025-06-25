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
  Save
} from 'lucide-react';
import './App.css';

// Configuração da API
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://sistema-mecanica.onrender.com/api' 
  : 'http://localhost:5000/api';

// Componente de Cadastro de Boxes/Elevadores
const CadastroBoxes = () => {
  const [boxes, setBoxes] = useState([]);
  const [novoBox, setNovoBox] = useState({ numero: '' });
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
        setNovoBox({ numero: '' });
        carregarBoxes();
      } else {
        alert('Erro ao cadastrar box');
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

      {/* Formulário de Cadastro */}
      <Card>
        <CardHeader>
          <CardTitle>Novo Box/Elevador</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={salvarBox} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Número/Nome do Box *
              </label>
              <Input
                type="text"
                placeholder="Ex: Box 01, Elevador A, Vaga 1"
                value={novoBox.numero}
                onChange={(e) => setNovoBox({...novoBox, numero: e.target.value})}
                required
              />
            </div>
            <Button type="submit" className="w-full">
              <Plus className="w-4 h-4 mr-2" />
              Cadastrar Box
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Lista de Boxes */}
      <Card>
        <CardHeader>
          <CardTitle>Boxes Cadastrados ({boxes.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {boxes.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Nenhum box cadastrado ainda. Cadastre o primeiro box acima.
            </p>
          ) : (
            <div className="space-y-2">
              {boxes.map((box) => (
                <div key={box.id} className="flex items-center justify-between p-3 border rounded-lg">
                  {editandoBox === box.id ? (
                    <div className="flex items-center gap-2 flex-1">
                      <Input
                        defaultValue={box.numero}
                        onBlur={(e) => editarBox(box.id, { numero: e.target.value })}
                        className="flex-1"
                      />
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
                        <Building className="w-5 h-5 text-blue-600" />
                        <div>
                          <div className="font-medium">{box.numero}</div>
                          <div className="text-sm text-gray-500">
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

      {/* Formulário de Cadastro */}
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

      {/* Lista de Mecânicos */}
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

      {/* Formulário de Cadastro */}
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

      {/* Lista de Tipos de Serviço */}
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

