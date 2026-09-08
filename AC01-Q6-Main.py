from collections import defaultdict
from typing import List

import matplotlib.pyplot as plt
import networkx as nx

from Multigrafo import Elo, Multigrafo, Vertice


class MultigrafoComTravessia(Multigrafo):
    def __init__(self, vertices: List[Vertice], elos: List[Elo]):
        super().__init__(vertices, elos)
        self.visitados = set()
        self.rotulos = {}
        self.ordem_visita = []
        self.rot = 0

    def _adjacentes(self, vertice: Vertice) -> List[Vertice]:
        """
        Adjacência no multigrafo misto:
        - Elo orientado: somente vertice1 alcança vertice2.
        - Elo não orientado: alcance bidirecional.
        Múltiplos elos entre o mesmo par não duplicam o vizinho na lista.
        """
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

    def traverse_topologico(self, v: Vertice):
        """
        Traverse(G, v, rot)
        begin
            Se v de G é não visitado então
                Marque v como visitado e atribua a ele um rótulo (rot := rot + 1);
                Se há um vértice adjacente de v não visitado então
                    Traverse(G, adj(v), rot);
        end
        """
        if v.nome not in self.visitados:
            self.visitados.add(v.nome)
            self.rot += 1
            self.rotulos[v.nome] = self.rot
            self.ordem_visita.append(v.nome)

            for adj in self._adjacentes(v):
                if adj.nome not in self.visitados:
                    self.traverse_topologico(adj)

    def rotulacao_topologica(self):
        """
        Laço principal: 'Tome um vértice v de G não visitado, Traverse(G, v, rot);'
        Garante cobertura de componentes desconexos.
        """
        self.visitados.clear()
        self.rotulos.clear()
        self.ordem_visita.clear()
        self.rot = 0

        for v in self.vertices:
            if v.nome not in self.visitados:
                self.traverse_topologico(v)

        return self.rotulos

    def imprimir_resultado(self):
        print("=" * 56)
        print("Travessia in-order (DFS) e rotulação topológica simples")
        print("=" * 56)
        print("\nOrdem de visita dos vértices:")
        print(" -> ".join(self.ordem_visita))

        print("\nTabela de correspondência: Vértice -> Rótulo Topológico")
        print("-" * 40)
        print(f"{'Vértice':<12} {'Rótulo Topológico':>20}")
        print("-" * 40)
        for nome in [v.nome for v in self.vertices]:
            rotulo = self.rotulos.get(nome, "-")
            print(f"{nome:<12} {str(rotulo):>20}")
        print("-" * 40)

    def mostrarGrafo(self):
        G = nx.MultiDiGraph()

        rotulos_nos = {}
        for v in self.vertices:
            rotulo = self.rotulos.get(v.nome)
            if rotulo is None:
                rotulos_nos[v.nome] = v.nome
            else:
                rotulos_nos[v.nome] = f"{v.nome} (Rótulo: {rotulo})"
            G.add_node(v.nome)

        pos = nx.circular_layout(G)

        plt.figure(figsize=(14, 11))
        plt.title("Multigrafo Misto com Rotulação Topológica (Travessia DFS)")

        nx.draw_networkx_nodes(G, pos, node_size=1600, node_color="skyblue")
        nx.draw_networkx_labels(G, pos, labels=rotulos_nos, font_size=8, font_weight="bold")

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
                textos_rotulos.append(f"{elo.nome} (p={elo.peso})")

                if qtd_elos == 1:
                    rad = 0.1 if elo.isOrientado else 0.0
                else:
                    fator = (idx // 2 + 1) * 0.25
                    rad = fator if idx % 2 == 0 else -fator

                estilo_conexao = f"arc3,rad={rad}"

                if elo.isOrientado:
                    nx.draw_networkx_edges(
                        G,
                        pos,
                        edgelist=[(origem, destino)],
                        arrows=True,
                        arrowstyle="->",
                        arrowsize=16,
                        edge_color="red",
                        connectionstyle=estilo_conexao,
                    )
                else:
                    nx.draw_networkx_edges(
                        G,
                        pos,
                        edgelist=[(origem, destino)],
                        arrowstyle="-",
                        edge_color="blue",
                        connectionstyle=estilo_conexao,
                    )

            rotulos_pares[(par[0], par[1])] = "\n".join(textos_rotulos)

        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=rotulos_pares,
            font_color="black",
            font_size=7,
        )

        plt.axis("off")
        plt.tight_layout()
        plt.show()


def montar_multigrafo_teste() -> MultigrafoComTravessia:
    """Multigrafo misto com 15 vértices (V1..V15) e 20 elos."""
    g = MultigrafoComTravessia([], [])

    for i in range(1, 16):
        g.adicionarVertice(f"V{i}")

    # Múltiplos elos entre V1 e V2 (orientado + não orientado)
    g.adicionarElo("e1", "V1", "V2", isOrientado=True, peso=1)
    g.adicionarElo("e2", "V1", "V2", isOrientado=False, peso=2)

    g.adicionarElo("e3", "V2", "V3", isOrientado=True, peso=1)
    g.adicionarElo("e4", "V3", "V4", isOrientado=True, peso=1)
    g.adicionarElo("e5", "V1", "V5", isOrientado=False, peso=1)
    g.adicionarElo("e6", "V5", "V6", isOrientado=True, peso=3)
    g.adicionarElo("e7", "V6", "V7", isOrientado=False, peso=1)
    g.adicionarElo("e8", "V4", "V7", isOrientado=False, peso=1)
    g.adicionarElo("e9", "V7", "V8", isOrientado=False, peso=1)

    # Múltiplos elos entre V8 e V9
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


if __name__ == "__main__":
    g = montar_multigrafo_teste()
    g.rotulacao_topologica()
    g.imprimir_resultado()
    g.mostrarGrafo()
