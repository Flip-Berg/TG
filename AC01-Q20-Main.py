from collections import defaultdict, deque
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from Multigrafo import Elo, Multigrafo, Vertice


class MultigrafoBFSTopologico(Multigrafo):
    def __init__(self, vertices: List[Vertice], elos: List[Elo]):
        super().__init__(vertices, elos)
        self.visitados = set()
        self.rotulos = {}
        self.ordem_visita = []
        self.arestas_arvore = []
        self.rot = 0

    def _adjacentes(self, vertice: Vertice) -> List[Vertice]:
        adjacentes = []
        nomes_vistos = set()

        for elo in vertice.elos:
            vizinho = None
            if elo.isOrientado:
                if elo.vertice1 is vertice:
                    vizinho = elo.vertice2
            else:
                if elo.vertice1 is vertice:
                    vizinho = elo.vertice2
                elif elo.vertice2 is vertice:
                    vizinho = elo.vertice1

            if vizinho is not None and vizinho.nome not in nomes_vistos:
                nomes_vistos.add(vizinho.nome)
                adjacentes.append(vizinho)

        return adjacentes

    def traverse_bfs(self, v_inicial: Vertice):
        fila = deque()
        fila.append(v_inicial)
        self.visitados.add(v_inicial.nome)
        self.rot += 1
        self.rotulos[v_inicial.nome] = self.rot
        self.ordem_visita.append(v_inicial.nome)

        while fila:
            v = fila.popleft()
            for adj in self._adjacentes(v):
                if adj.nome not in self.visitados:
                    self.visitados.add(adj.nome)
                    self.rot += 1
                    self.rotulos[adj.nome] = self.rot
                    self.ordem_visita.append(adj.nome)
                    self.arestas_arvore.append((v.nome, adj.nome))
                    fila.append(adj)

    def rotulacao_topologica_bfs(self, vertice_inicial=None):
        self.visitados.clear()
        self.rotulos.clear()
        self.ordem_visita.clear()
        self.arestas_arvore.clear()
        self.rot = 0

        if vertice_inicial is not None:
            v_inicial = self.buscarVertice(vertice_inicial)
            if v_inicial is not None and v_inicial.nome not in self.visitados:
                self.traverse_bfs(v_inicial)

        for v in self.vertices:
            if v.nome not in self.visitados:
                self.traverse_bfs(v)

        return self.rotulos

    def imprimir_resultado(self):
        n_vertices = len(self.vertices)
        n_elos = len(self.elos)
        print(f"Analisando o grafo fornecido ({n_vertices} vértices e {n_elos} elos)...")

        if self.ordem_visita:
            v_inicial = self.ordem_visita[0]
            print(f"Iniciando travessia BFS a partir do nó inicial '{v_inicial}':")
            print("Ordem de visita (por camadas): " + " -> ".join(self.ordem_visita))
            print("Resultado da rotulação BFS:", self.rotulos)
        else:
            print("Nenhum vértice para visitar (grafo vazio).")

        if self.arestas_arvore:
            print("Arestas de árvore da BFS (descobertas pela travessia):")
            for idx, (origem, destino) in enumerate(self.arestas_arvore, 1):
                print(f"  E{idx}: {origem} → {destino}")

    def mostrarGrafo(self):
        G = nx.MultiDiGraph()

        rotulos_nos = {}
        for v in self.vertices:
            rotulo = self.rotulos.get(v.nome)
            if rotulo is None:
                rotulos_nos[v.nome] = v.nome
            else:
                rotulos_nos[v.nome] = f"{v.nome}\n(Rótulo BFS: {rotulo})"
            G.add_node(v.nome)

        n_vertices = len(self.vertices)
        if n_vertices <= 15:
            pos = nx.circular_layout(G)
        else:
            pos = nx.spring_layout(G, seed=42, k=2.5)

        largura_figura = max(11, min(22, n_vertices * 1.0))
        altura_figura = max(9, min(16, n_vertices * 0.85))

        plt.figure(figsize=(largura_figura, altura_figura))
        plt.title("Resultado da Travessia BFS - Q20")

        tam_no = max(500, min(2500, 22000 // max(1, n_vertices)))
        fonte = max(6, min(12, 160 // max(1, n_vertices)))

        nx.draw_networkx_nodes(G, pos, node_size=tam_no, node_color="lightgreen")
        nx.draw_networkx_labels(G, pos, labels=rotulos_nos, font_size=fonte, font_weight="bold")

        arestas_arvore_set = set(self.arestas_arvore)

        conexoes_pares = defaultdict(list)
        for elo in self.elos:
            par = tuple(sorted([elo.vertice1.nome, elo.vertice2.nome]))
            conexoes_pares[par].append(elo)

        rotulos_pares = {}

        for par, lista_elos in conexoes_pares.items():
            qtd_elos = len(lista_elos)
            textos_rotulos = []

            for idx, elo in enumerate(lista_elos):
                origem = elo.vertice1.nome
                destino = elo.vertice2.nome
                textos_rotulos.append(f"{elo.nome}")

                if qtd_elos == 1:
                    rad = 0.12 if elo.isOrientado else 0.0
                else:
                    fator = (idx // 2 + 1) * 0.28
                    rad = fator if idx % 2 == 0 else -fator

                estilo_conexao = f"arc3,rad={rad}"

                eh_aresta_arvore = (origem, destino) in arestas_arvore_set

                if eh_aresta_arvore:
                    cor_aresta = "darkgreen"
                    espessura = 2.5
                    estilo_linha = "solid"
                else:
                    cor_aresta = "red" if elo.isOrientado else "blue"
                    espessura = 1.0
                    estilo_linha = "dashed"

                if elo.isOrientado:
                    nx.draw_networkx_edges(
                        G,
                        pos,
                        edgelist=[(origem, destino)],
                        arrows=True,
                        arrowstyle="->",
                        arrowsize=18,
                        edge_color=cor_aresta,
                        width=espessura,
                        style=estilo_linha,
                        connectionstyle=estilo_conexao,
                    )
                else:
                    nx.draw_networkx_edges(
                        G,
                        pos,
                        edgelist=[(origem, destino)],
                        arrowstyle="-",
                        edge_color=cor_aresta,
                        width=espessura,
                        style=estilo_linha,
                        connectionstyle=estilo_conexao,
                    )

            rotulos_pares[(par[0], par[1])] = "\n".join(textos_rotulos)

        fonte_arestas = max(5, min(10, 120 // max(1, n_vertices)))
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=rotulos_pares,
            font_color="black",
            font_size=fonte_arestas,
        )

        from matplotlib.lines import Line2D
        legenda = [
            Line2D([0], [0], color="darkgreen", lw=3, label="Aresta de árvore BFS"),
            Line2D([0], [0], color="red", lw=1, ls="dashed", label="Elo orientado (não-árvore)"),
            Line2D([0], [0], color="blue", lw=1, ls="dashed", label="Elo não-orientado (não-árvore)"),
        ]
        plt.legend(handles=legenda, loc="lower right", fontsize=max(7, fonte - 1))

        plt.axis("off")
        plt.tight_layout()
        plt.show()


def montar_multigrafo_demonstracao() -> MultigrafoBFSTopologico:
    g = MultigrafoBFSTopologico([], [])

    for i in range(1, 16):
        g.adicionarVertice(f"V{i}")

    g.adicionarElo("e1", "V1", "V2", isOrientado=True, peso=1)
    g.adicionarElo("e2", "V1", "V2", isOrientado=False, peso=2)

    g.adicionarElo("e3", "V2", "V3", isOrientado=True, peso=1)
    g.adicionarElo("e4", "V3", "V4", isOrientado=True, peso=1)
    g.adicionarElo("e5", "V1", "V5", isOrientado=False, peso=1)
    g.adicionarElo("e6", "V5", "V6", isOrientado=True, peso=3)
    g.adicionarElo("e7", "V6", "V7", isOrientado=False, peso=1)
    g.adicionarElo("e8", "V4", "V7", isOrientado=False, peso=1)
    g.adicionarElo("e9", "V7", "V8", isOrientado=False, peso=1)

    g.adicionarElo("e10", "V8", "V9", isOrientado=True, peso=1)
    g.adicionarElo("e11", "V8", "V9", isOrientado=False, peso=4)

    g.adicionarElo("e12", "V9", "V10", isOrientado=False, peso=1)
    g.adicionarElo("e13", "V10", "V11", isOrientado=True, peso=1)
    g.adicionarElo("e14", "V11", "V12", isOrientado=False, peso=1)
    g.adicionarElo("e15", "V12", "V13", isOrientado=True, peso=2)
    g.adicionarElo("e16", "V13", "V14", isOrientado=False, peso=1)
    g.adicionarElo("e17", "V14", "V15", isOrientado=False, peso=1)
    g.adicionarElo("e18", "V3", "V6", isOrientado=True, peso=1)
    g.adicionarElo("e19", "V15", "V10", isOrientado=True, peso=1)
    g.adicionarElo("e20", "V4", "V8", isOrientado=True, peso=5)

    return g


def executar_questao_20(grafo: Multigrafo, vertice_inicial=None, mostrar_grafico=True):
    if not isinstance(grafo, MultigrafoBFSTopologico):
        g = MultigrafoBFSTopologico([], [])
        for v in grafo.vertices:
            g.adicionarVertice(v.nome)
        for elo in grafo.elos:
            g.adicionarElo(
                elo.nome,
                elo.vertice1.nome,
                elo.vertice2.nome,
                elo.isOrientado,
                elo.peso,
            )
    else:
        g = grafo

    if vertice_inicial is None and g.vertices:
        vertice_inicial = g.vertices[0].nome

    g.rotulacao_topologica_bfs(vertice_inicial)
    g.imprimir_resultado()
    if mostrar_grafico:
        g.mostrarGrafo()
    return g


if __name__ == "__main__":
    grafo_demonstracao = montar_multigrafo_demonstracao()
    executar_questao_20(grafo_demonstracao)
