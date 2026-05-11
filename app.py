#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVIDOR FLASK - AGENDADOR DE FILMES NAS SALAS
Com Interface Web Completa
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict
import heapq

app = Flask(__name__)


@dataclass
class Filme:
    """Representa um filme em uma sessão"""
    nome: str
    inicio: str
    fim: str

    def get_inicio_time(self):
        return datetime.strptime(self.inicio, "%H:%M").time()

    def get_fim_time(self):
        return datetime.strptime(self.fim, "%H:%M").time()

    def sobrepoe(self, outro: 'Filme') -> bool:
        """Verifica se este filme se sobrepõe com outro"""
        return not (self.get_fim_time() <= outro.get_inicio_time())

    def duracao_minutos(self) -> int:
        """Calcula duração em minutos"""
        inicio_min = self.get_inicio_time().hour * 60 + self.get_inicio_time().minute
        fim_min = self.get_fim_time().hour * 60 + self.get_fim_time().minute
        return fim_min - inicio_min


@dataclass
class Sala:
    """Representa uma sala de cinema"""
    numero: int
    filmes: List[Filme] = None

    def __post_init__(self):
        if self.filmes is None:
            self.filmes = []

    def adicionar_filme(self, filme: Filme) -> bool:
        """Tenta adicionar um filme à sala"""
        for filme_existente in self.filmes:
            if filme.sobrepoe(filme_existente):
                return False

        self.filmes.append(filme)
        return True


class AgendadorFilmes:
    """Agendador de filmes usando Interval Partitioning"""

    def __init__(self):
        self.filmes_disponiveis: List[Filme] = []
        self.salas: Dict[int, Sala] = {}

    def adicionar_filme(self, nome: str, inicio: str, fim: str) -> Dict:
        """Adiciona um novo filme"""
        try:
            h_inicio = datetime.strptime(inicio, "%H:%M").time()
            h_fim = datetime.strptime(fim, "%H:%M").time()

            if h_fim <= h_inicio:
                return {"sucesso": False, "mensagem": "Horário de término deve ser após o início!"}

            filme = Filme(nome, inicio, fim)
            self.filmes_disponiveis.append(filme)
            return {"sucesso": True, "mensagem": f"Filme '{nome}' adicionado com sucesso!"}
        except ValueError:
            return {"sucesso": False, "mensagem": "Formato de horário inválido. Use HH:MM"}

    def interval_partitioning(self) -> Dict[int, Sala]:
        """Algoritmo Greedy - Interval Partitioning (heap otimizado)"""
        if not self.filmes_disponiveis:
            return {}

        filmes_ordenados = sorted(self.filmes_disponiveis, key=lambda f: f.get_inicio_time())
        heap = []
        salas_resultado: Dict[int, Sala] = {}
        num_sala_atual = 0

        for filme in filmes_ordenados:
            inicio_min = filme.get_inicio_time().hour * 60 + filme.get_inicio_time().minute

            if heap and heap[0][0] <= inicio_min:
                _, numero_sala = heapq.heappop(heap)
                sala = salas_resultado[numero_sala]
                sala.filmes.append(filme)
                fim_atual = filme.get_fim_time().hour * 60 + filme.get_fim_time().minute
                heapq.heappush(heap, (fim_atual, numero_sala))
            else:
                num_sala_atual += 1
                nova_sala = Sala(num_sala_atual)
                nova_sala.filmes.append(filme)
                salas_resultado[num_sala_atual] = nova_sala
                fim_atual = filme.get_fim_time().hour * 60 + filme.get_fim_time().minute
                heapq.heappush(heap, (fim_atual, num_sala_atual))

        return salas_resultado

    def otimizar_agenda(self):
        self.salas = self.interval_partitioning()
        return self.get_resultado()

    def get_resultado(self) -> Dict:
        if not self.salas:
            return {
                "sucesso": False,
                "salas": [],
                "total_filmes": len(self.filmes_disponiveis),
                "salas_necessarias": 0
            }

        salas_data = []
        for numero_sala in sorted(self.salas.keys()):
            sala = self.salas[numero_sala]
            filmes_ordenados = sorted(sala.filmes, key=lambda f: f.get_inicio_time())

            filmes_data = []
            for filme in filmes_ordenados:
                filmes_data.append({
                    "nome": filme.nome,
                    "inicio": filme.inicio,
                    "fim": filme.fim,
                    "duracao": filme.duracao_minutos()
                })

            salas_data.append({
                "numero": numero_sala,
                "filmes": filmes_data,
                "total_filmes": len(filmes_data)
            })

        return {
            "sucesso": True,
            "salas": salas_data,
            "total_filmes": len(self.filmes_disponiveis),
            "salas_necessarias": len(self.salas),
            "media_filmes_sala": round(len(self.filmes_disponiveis) / len(self.salas), 1),
            "profundidade_maxima": self.calcular_profundidade_maxima(),
            "valido_otimo": (len(self.salas) == self.calcular_profundidade_maxima())
        }

    def listar_filmes(self) -> List[Dict]:
        filmes_ordenados = sorted(self.filmes_disponiveis, key=lambda f: f.get_inicio_time())
        return [
            {
                "nome": f.nome,
                "inicio": f.inicio,
                "fim": f.fim,
                "duracao": f.duracao_minutos()
            }
            for f in filmes_ordenados
        ]

    def calcular_profundidade_maxima(self) -> int:
        eventos = []
        for f in self.filmes_disponiveis:
            inicio_min = f.get_inicio_time().hour * 60 + f.get_inicio_time().minute
            fim_min = f.get_fim_time().hour * 60 + f.get_fim_time().minute
            eventos.append((inicio_min, 1))
            eventos.append((fim_min, -1))

        if not eventos:
            return 0

        eventos.sort(key=lambda x: (x[0], x[1]))
        contador = 0
        profundidade_max = 0
        for _, delta in eventos:
            contador += delta
            profundidade_max = max(profundidade_max, contador)

        return profundidade_max

    def limpar_agenda(self):
        self.filmes_disponiveis.clear()
        self.salas.clear()

    def carregar_exemplo(self):
        filmes_exemplo = [
            ("Homem-Aranha", "10:00", "12:30"),
            ("Avatar 3", "10:30", "13:00"),
            ("Mário", "12:00", "13:30"),
            ("Homem-Aranha", "14:00", "16:30"),
            ("Avatar 3", "15:00", "17:30"),
            ("Mário", "17:00", "18:30"),
        ]

        for nome, inicio, fim in filmes_exemplo:
            self.adicionar_filme(nome, inicio, fim)


agendador = AgendadorFilmes()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/filmes', methods=['GET'])
def get_filmes():
    return jsonify(agendador.listar_filmes())


@app.route('/api/filmes', methods=['POST'])
def add_filme():
    data = request.json
    resultado = agendador.adicionar_filme(data['nome'], data['inicio'], data['fim'])
    return jsonify(resultado)


@app.route('/api/otimizar', methods=['POST'])
def otimizar():
    resultado = agendador.otimizar_agenda()
    return jsonify(resultado)


@app.route('/api/resultado', methods=['GET'])
def get_resultado():
    return jsonify(agendador.get_resultado())


@app.route('/api/exemplo', methods=['POST'])
def carregar_exemplo():
    agendador.carregar_exemplo()
    return jsonify({"sucesso": True, "mensagem": "Exemplo carregado!"})


@app.route('/api/limpar', methods=['POST'])
def limpar():
    agendador.limpar_agenda()
    return jsonify({"sucesso": True, "mensagem": "Agenda limpa!"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)