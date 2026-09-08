from __future__ import annotations
from collections import defaultdict 
from typing import List 
import networkx as nx
import matplotlib.pyplot as plt

# Ligação = Elo = Aresta. Para esse progriama foi utilizado Elo
class Elo: 
    def __init__(self, nome, vertice1: Vertice, vertice2: Vertice, isOrientado, peso=1.0):
        self.nome=nome 
        self.vertice1=vertice1
        self.vertice2=vertice2
        self.isOrientado=isOrientado
        #se for orientado, ele sai de vertice1 e entra em vertice2
        self.peso=peso
        #não ponderado=todos os pesos iguais a 1

class Vertice:
    def __init__(self, nome, elos: List[Elo]):
        self.nome=nome
        self.elos=elos 

# os vertices da classe elo e os elos da classe vertice são ponteiros pros objetos originais, então mexer neles atraves dessas classes também mexe no multigrafo

class Multigrafo:
    def __init__(self, vertices: List[Vertice], elos: List[Elo]):
        '''
        vertices: vetor de strings, sendo cada string o nome dos vértices
        elos: vetor de objetos da classe Elo, que representam as arestas entre os vertices
        '''
        self.vertices=vertices
        self.elos=elos


    def buscarVertice(self, nomeVertice):
        for vertice in self.vertices:
            if vertice.nome == nomeVertice:
                return vertice
        return None 
 
    def buscarElo(self, nomeElo):
        for elo in self.elos:
            if elo.nome == nomeElo:
                return elo
        return None

    def adicionarVertice(self, nomeVertice):
        jaExiste = self.buscarVertice(nomeVertice)
        if jaExiste: 
            return 
        novoVertice = Vertice(nomeVertice, [])
        self.vertices.append(novoVertice)
                
    def adicionarElo(self, nomeElo, nomeVertice1, nomeVertice2, isOrientado, peso=1):
        '''
        considerando multigrafo misto, pode haver mais de um elo para o mesmo vértice e na mesma direção, então basta checar se os vértices existem antes de adicionar o elo
        '''
        vertice1 = self.buscarVertice(nomeVertice1)
        vertice2 = self.buscarVertice(nomeVertice2)

        if vertice1 and vertice2:
            novoElo = Elo(nomeElo, vertice1, vertice2, isOrientado, peso)
            self.elos.append(novoElo)
            vertice1.elos.append(novoElo)
            vertice2.elos.append(novoElo)

    def removerVertice(self, nomeVertice):
        vertice = self.buscarVertice(nomeVertice)
        if vertice is None:
            return

        # 1. Identifica todos os elos que encostam nesse vértice
        elosParaRemover = list(vertice.elos)

        # 2. Remove esses elos de TODOS os outros vértices do grafo
        for verticeAdjacente in self.vertices:
            verticeAdjacente.elos = [elo for elo in verticeAdjacente.elos if elo not in elosParaRemover]

        # 3. Remove esses elos da lista global do multigrafo
        self.elos = [elo for elo in self.elos if elo not in elosParaRemover]

        # 4. Remove o vértice da lista global
        self.vertices.remove(vertice)

    def removerElo(self, nomeElo):
        elo=self.buscarElo(nomeElo)
        if elo:
            elo.vertice1.elos.remove(elo)
            elo.vertice2.elos.remove(elo)
            self.elos.remove(elo)

    def alterarVertice(self, nomeAntigo, nomeNovo): 
        vertice=self.buscarVertice(nomeAntigo)
        if vertice:
            vertice.nome = nomeNovo

    def alterarElo(self, nomeAntigo, nomeNovo="", vertice1Novo=None, vertice2Novo=None, isOrientadoNovo=None, pesoNovo=0.0):
        elo = self.buscarElo(nomeAntigo)
        if not elo:
            return 
        if nomeNovo:
            elo.nome = nomeNovo 

        if vertice1Novo:
            elo.vertice1=vertice1Novo

        if vertice2Novo: 
            elo.vertice2=vertice2Novo

        if isOrientadoNovo:
            elo.isOrientado = isOrientadoNovo

        if pesoNovo:
            elo.peso = pesoNovo

    def destruirGrafo(self):
        #necessario remover todas as referencias a cada objeto ou o proprio objeto pra tirar eles da memória
        for vertice in self.vertices:
            vertice.elos.clear()

        self.vertices.clear()
        self.elos.clear()


    def mostrarGrafo(self):
        G = nx.MultiDiGraph()

        for v in self.vertices:
            G.add_node(v.nome)

        pos = nx.circular_layout(G)
        
        plt.figure(figsize=(9, 7))
        plt.title("Visualização do Multigrafo Misto")

        # Desenha os vértices (nós)
        nx.draw_networkx_nodes(G, pos, node_size=800, node_color='skyblue')
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

        # Dicionário para agrupar as conexões entre cada par de vértices (independente de direção)
        # Chave: par ordenado ordenado (v_min, v_max)
        # Valor: lista de objetos Elo entre esses dois vértices
        conexoes_pares = defaultdict(list)
        for elo in self.elos:
            par = tuple(sorted([elo.vertice1.nome, elo.vertice2.nome]))
            conexoes_pares[par].append(elo)

        # Rótulos agrupados por par de vértices para exibir e1, e2, etc. sem sobreposição
        rotulos_pares = {}

        # 1. Desenha cada elo aplicando curvaturas alternadas (-rad e +rad)
        for par, lista_elos in conexoes_pares.items():
            qtd_elos = len(lista_elos)
            textos_rotulos = []

            for idx, elo in enumerate(lista_elos):
                origem = elo.vertice1.nome
                destino = elo.vertice2.nome
                textos_rotulos.append(f"{elo.nome} (p={elo.peso})")

                # Se houver apenas 1 elo entre os vértices, desenha reto (rad=0)
                # Se houver mais, alterna curvaturas positivas e negativas
                if qtd_elos == 1:
                    rad = 0.1 if elo.isOrientado else 0.0
                else:
                    # Passo de curvatura (ex: -0.25, +0.25, -0.5, +0.5...)
                    fator = (idx // 2 + 1) * 0.25
                    rad = fator if idx % 2 == 0 else -fator

                estilo_conexao = f"arc3,rad={rad}"

                if elo.isOrientado:
                    nx.draw_networkx_edges(
                        G, pos,
                        edgelist=[(origem, destino)],
                        arrows=True,
                        arrowstyle='->',
                        arrowsize=20,
                        edge_color='red',
                        connectionstyle=estilo_conexao
                    )
                else:
                    nx.draw_networkx_edges(
                        G, pos,
                        edgelist=[(origem, destino)],
                        arrowstyle='-',
                        edge_color='blue',
                        connectionstyle=estilo_conexao
                    )

            # Junta os textos de todos os elos do mesmo par em linhas separadas
            rotulos_pares[(par[0], par[1])] = "\n".join(textos_rotulos)

        # 2. Desenha os rótulos centralizados por par de vértices
        nx.draw_networkx_edge_labels(
            G, pos, 
            edge_labels=rotulos_pares, 
            font_color='black', 
            font_size=10
        )

        plt.axis('off')
        plt.show()
