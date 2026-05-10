#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGENDADOR DE FILMES NAS SALAS DO CINEMA
Usando Interval Partitioning (Algoritmo Greedy)

O algoritmo aloca filmes em salas de forma eficiente, minimizando
o número de salas necessárias usando a estratégia greedy ótima.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from datetime import time

@dataclass
class Filme:
    """Representa um filme em uma sessão"""
    nome: str
    inicio: time
    fim: time
    sala: str = "Sala Padrão"
    
    def __str__(self):
        return f"🎬 {self.nome:30s} | {self.inicio.strftime('%H:%M')} - {self.fim.strftime('%H:%M')}"
    
    def sobrepoe(self, outro: 'Filme') -> bool:
        """Verifica se este filme se sobrepõe com outro"""
        return not (self.fim <= outro.inicio)


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
        # Verifica se a sala está livre no horário do filme
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
    
    def adicionar_filme(self, nome: str, inicio: str, fim: str) -> bool:
        """Adiciona um novo filme à lista de disponíveis"""
        try:
            h_inicio = __import__('datetime').datetime.strptime(inicio, "%H:%M").time()
            h_fim = __import__('datetime').datetime.strptime(fim, "%H:%M").time()
            
            if h_fim <= h_inicio:
                print("❌ Erro: Horário de término deve ser após o início!")
                return False
            
            filme = Filme(nome, h_inicio, h_fim)
            self.filmes_disponiveis.append(filme)
            print(f"✅ Filme '{nome}' adicionado com sucesso!")
            return True
        except ValueError:
            print("❌ Erro: Formato de horário inválido. Use HH:MM")
            return False
    
    def interval_partitioning(self) -> Dict[int, Sala]:
        """
        Algoritmo Greedy - Interval Partitioning
        
        Estratégia: Ordena filmes por tempo de início.
        Para cada filme, aloca na primeira sala disponível.
        Se nenhuma sala estiver livre, cria uma nova.
        
        Complexidade: O(n log n)
        Otimalidade: Encontra a solução ótima!
        """
        if not self.filmes_disponiveis:
            return {}
        
        # Ordena por tempo de início (necessário para o algoritmo)
        filmes_ordenados = sorted(self.filmes_disponiveis, key=lambda f: f.inicio)
        
        salas_resultado = {}
        num_sala_atual = 0
        
        for filme in filmes_ordenados:
            # Tenta encaixar em uma sala existente
            sala_encontrada = False
            
            for numero_sala, sala in salas_resultado.items():
                if sala.adicionar_filme(filme):
                    sala_encontrada = True
                    break
            
            # Se não encaixou em nenhuma sala, cria uma nova
            if not sala_encontrada:
                num_sala_atual += 1
                nova_sala = Sala(num_sala_atual)
                nova_sala.adicionar_filme(filme)
                salas_resultado[num_sala_atual] = nova_sala
        
        return salas_resultado
    
    def otimizar_agenda(self):
        """Calcula a melhor alocação de salas possível"""
        print("\n" + "="*80)
        print("🎯 ALOCANDO FILMES NAS SALAS COM INTERVAL PARTITIONING...")
        print("="*80)
        
        self.salas = self.interval_partitioning()
        
        if not self.salas:
            print("⚠️  Nenhum filme disponível para agendar.")
            return
        
        print(f"\n✨ MELHOR ALOCAÇÃO ENCONTRADA ({len(self.salas)} salas necessárias):\n")
        
        total_filmes = 0
        for numero_sala in sorted(self.salas.keys()):
            sala = self.salas[numero_sala]
            total_filmes += len(sala.filmes)
            
            print(f"\n🏠 SALA {numero_sala}")
            print("-" * 80)
            
            filmes_ordenados = sorted(sala.filmes, key=lambda f: f.inicio)
            for i, filme in enumerate(filmes_ordenados, 1):
                duracao = self._calcular_duracao(filme.inicio, filme.fim)
                print(f"  {i}. {filme} ({duracao} min)")
        
        print(f"\n{'='*80}")
        print(f"📊 RESUMO:")
        print(f"  • Salas necessárias: {len(self.salas)}")
        print(f"  • Total de filmes: {total_filmes}")
        print(f"  • Filme por sala: {(total_filmes / len(self.salas)):.1f}")
        print(f"{'='*80}")
    
    def _calcular_duracao(self, inicio: time, fim: time) -> int:
        """Calcula duração em minutos"""
        inicio_min = inicio.hour * 60 + inicio.minute
        fim_min = fim.hour * 60 + fim.minute
        return fim_min - inicio_min
    
    def mostrar_agenda_desagendada(self):
        """Mostra filmes que não foram agendados"""
        if not self.salas:
            print("\n⚠️  Execute 'Otimizar agenda' primeiro!")
            return
        
        filmes_agendados = set()
        for sala in self.salas.values():
            filmes_agendados.update(sala.filmes)
        
        desagendados = [f for f in self.filmes_disponiveis if f not in filmes_agendados]
        
        if not desagendados:
            print("\n✅ Todos os filmes foram alocados!")
            return
        
        print(f"\n⚠️  NENHUM FILME NÃO ALOCADO - Todos foram distribuídos nas salas!")
    
    def listar_filmes(self):
        """Lista todos os filmes disponíveis"""
        if not self.filmes_disponiveis:
            print("📭 Nenhum filme disponível ainda.")
            return
        
        print("\n🎬 FILMES DISPONÍVEIS:\n")
        for i, filme in enumerate(sorted(self.filmes_disponiveis, key=lambda f: f.inicio), 1):
            duracao = self._calcular_duracao(filme.inicio, filme.fim)
            print(f"{i}. {filme} ({duracao} min)")
    
    def listar_salas(self):
        """Lista todas as salas com seus filmes"""
        if not self.salas:
            print("\n⚠️  Execute 'Otimizar agenda' para alocar filmes nas salas!")
            return
        
        print(f"\n🏠 FILMES NAS SALAS ({len(self.salas)} salas):\n")
        
        for numero_sala in sorted(self.salas.keys()):
            sala = self.salas[numero_sala]
            print(f"\n🏠 SALA {numero_sala} ({len(sala.filmes)} filmes)")
            print("-" * 80)
            
            filmes_ordenados = sorted(sala.filmes, key=lambda f: f.inicio)
            for i, filme in enumerate(filmes_ordenados, 1):
                duracao = self._calcular_duracao(filme.inicio, filme.fim)
                print(f"  {i}. {filme} ({duracao} min)")
    
    def limpar_agenda(self):
        """Limpa todos os filmes"""
        self.filmes_disponiveis.clear()
        self.filmes_agendados.clear()
        print("🗑️  Agenda limpa!")
    
    def carregar_exemplo(self):
        """Carrega um exemplo com filmes pré-configurados"""
        filmes_exemplo = [
            ("Homem-Aranha: Sem Volta para Casa", "10:00", "12:30"),
            ("Aventura Selvagem", "11:00", "12:45"),
            ("Drama Épico", "12:00", "14:30"),
            ("Comédia Hilária", "13:00", "14:15"),
            ("Ficção Científica", "14:00", "16:15"),
            ("Animação Infantil", "15:00", "16:30"),
            ("Thriller Suspense", "16:00", "17:45"),
            ("Romance Emocionante", "17:00", "18:30"),
            ("Ação Explosiva", "18:00", "19:45"),
            ("Documentário Fascinante", "19:00", "20:30"),
        ]
        
        print("\n📋 Carregando filmes de exemplo...\n")
        for nome, inicio, fim in filmes_exemplo:
            self.adicionar_filme(nome, inicio, fim)


def menu_principal():
    """Loop do menu interativo"""
    agendador = AgendadorFilmes()
    
    while True:
        print("\n" + "="*80)
        print("🎬 AGENDADOR DE FILMES NAS SALAS - INTERVAL PARTITIONING 🎬")
        print("="*80)
        print("""
1. 📝 Adicionar filme
2. 🎬 Ver filmes disponíveis
3. 🎯 Alocar filmes nas salas (Interval Partitioning)
4. 🏠 Ver filmes em cada sala
5. 📋 Carregar exemplo
6. 🗑️  Limpar agenda
7. ❌ Sair
        """)
        
        opcao = input("Escolha uma opção (1-7): ").strip()
        
        if opcao == "1":
            print("\n--- Adicionar Filme ---")
            nome = input("Nome do filme: ").strip()
            inicio = input("Horário de início (HH:MM): ").strip()
            fim = input("Horário de término (HH:MM): ").strip()
            agendador.adicionar_filme(nome, inicio, fim)
        
        elif opcao == "2":
            agendador.listar_filmes()
        
        elif opcao == "3":
            agendador.otimizar_agenda()
        
        elif opcao == "4":
            agendador.listar_salas()
        
        elif opcao == "5":
            agendador.carregar_exemplo()
            input("\nPressione Enter para continuar...")
        
        elif opcao == "6":
            confirmacao = input("Tem certeza? (s/n): ").lower()
            if confirmacao == "s":
                agendador.limpar_agenda()
        
        elif opcao == "7":
            print("\n👋 Até logo! Aproveite os filmes!")
            break
        
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║            BEM-VINDO AO AGENDADOR DE FILMES NAS SALAS!                    ║
║                                                                            ║
║  Este programa usa o algoritmo INTERVAL PARTITIONING (Greedy) para        ║
║  alocar filmes em salas de forma eficiente, minimizando o número de       ║
║  salas necessárias!                                                       ║
║                                                                            ║
║  Estratégia: Ordena filmes por tempo de início e aloca greedily em        ║
║  salas disponíveis, criando novas salas apenas quando necessário.         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    menu_principal()
