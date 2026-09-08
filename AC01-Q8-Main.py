import importlib.util
import os
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from Multigrafo import Multigrafo


def _carregar_modulo_q6():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AC01-Q6-Main.py")
    spec = importlib.util.spec_from_file_location("ac01_q6_main", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class SubgrafoMaximalArvore:
    """
    Produz um subgrafo maximal árvore (ou floresta maximal) de G.

    Sobre o grafo subjacente (orientação ignorada para conectividade):
    uma DFS/Traverse inclui um elo na árvore somente quando ele liga um
    vértice já visitado a um ainda não visitado. Elos restantes fecham ciclo
    e são descartados. Cada nova raiz da Traverse inicia uma componente.
    """

    def __init__(self, G: Multigrafo):
        self.G = G
        self.elos_arvore = []
        self.componentes = 0
        self.T = None
        self.raizes = []
        self.pais = {}
        self.filhos = defaultdict(list)
        self.niveis = {}

    def _adjacencias_subjacentes(self, vertice):
        """Vizinhos no grafo subjacente: todo elo incidente é bidirecional."""
        adjacencias = []
        elos_vistos = set()

        for elo in vertice.elos:
            if id(elo) in elos_vistos:
                continue
            elos_vistos.add(id(elo))

            if elo.vertice1 is vertice:
                vizinho = elo.vertice2
            elif elo.vertice2 is vertice:
                vizinho = elo.vertice1
            else:
                continue

            if vizinho is vertice:
                continue

            adjacencias.append((vizinho, elo))

        return adjacencias

    def _traverse(self, v, visitados, nivel=0, pai=None):
        """
        Traverse(G, v) para árvore geradora:
        marca v, registra o nível DFS e, para cada adj não visitado,
        inclui o elo (filho) e recursa.
        """
        visitados.add(v.nome)
        self.niveis[v.nome] = nivel

        if pai is None:
            self.raizes.append(v.nome)
        else:
            self.pais[v.nome] = pai.nome
            self.filhos[pai.nome].append(v.nome)

        for vizinho, elo in self._adjacencias_subjacentes(v):
            if vizinho.nome not in visitados:
                self.elos_arvore.append(elo)
                self._traverse(vizinho, visitados, nivel + 1, v)

    def construir(self) -> Multigrafo:
        visitados = set()
        self.elos_arvore = []
        self.componentes = 0
        self.raizes = []
        self.pais = {}
        self.filhos = defaultdict(list)
        self.niveis = {}

        for v in self.G.vertices:
            if v.nome not in visitados:
                self.componentes += 1
                self._traverse(v, visitados)

        self.T = Multigrafo([], [])
        for v in self.G.vertices:
            self.T.adicionarVertice(v.nome)

        for elo in self.elos_arvore:
            self.T.adicionarElo(
                elo.nome,
                elo.vertice1.nome,
                elo.vertice2.nome,
                elo.isOrientado,
                elo.peso,
            )

        return self.T

    def imprimir_resultado(self):
        n_v = len(self.G.vertices)
        n_e = len(self.elos_arvore)
        c = self.componentes
        valido = n_e == n_v - c

        print("=" * 64)
        print("Subgrafo maximal árvore / floresta maximal de G")
        print("=" * 64)

        print("\nVértices do subgrafo (|V| = {}):".format(n_v))
        print("  " + ", ".join(v.nome for v in self.G.vertices))

        print("\nElos selecionados para a árvore/floresta (|E_T| = {}):".format(n_e))
        print("-" * 64)
        print(f"{'Elo':<8} {'v1':<8} {'v2':<8} {'Orientado':<12} {'Peso':>8}")
        print("-" * 64)
        for elo in self.elos_arvore:
            orient = "sim" if elo.isOrientado else "não"
            print(
                f"{elo.nome:<8} {elo.vertice1.nome:<8} {elo.vertice2.nome:<8} "
                f"{orient:<12} {elo.peso:>8}"
            )
        print("-" * 64)

        nomes_arvore = {elo.nome for elo in self.elos_arvore}
        elos_descartados = [elo for elo in self.G.elos if elo.nome not in nomes_arvore]
        print("\nElos descartados (formariam ciclo no grafo subjacente):")
        if elos_descartados:
            print("  " + ", ".join(elo.nome for elo in elos_descartados))
        else:
            print("  (nenhum)")

        print("\nValidação da propriedade de árvore/floresta:")
        print(f"  |V| = {n_v}")
        print(f"  |E_T| = {n_e}")
        print(f"  C (componentes conexas no grafo subjacente) = {c}")
        print(f"  |E_T| = |V| - C  =>  {n_e} = {n_v} - {c}  =>  {n_v - c}")
        if c == 1:
            print("  G subjacente é conexo: |E_T| = |V| - 1 (árvore geradora).")
        else:
            print("  G subjacente é desconexo: floresta maximal com C árvores.")
        print(f"  Resultado da validação: {'OK' if valido else 'FALHOU'}")

        print("\nHierarquia da DFS (raiz no topo):")
        for nome in [v.nome for v in self.G.vertices]:
            nivel = self.niveis.get(nome, "-")
            pai = self.pais.get(nome, "(raiz)")
            filhos = ", ".join(self.filhos.get(nome, [])) or "(folha)"
            print(f"  {nome}: nível {nivel}, pai={pai}, filhos={filhos}")

    def _posicionar_subarvore(self, nome, x_esq, pos, dx=1.8, dy=1.6):
        """Coloca o nó no centro horizontal dos filhos; y = -nível DFS."""
        filhos = self.filhos.get(nome, [])
        y = -self.niveis[nome] * dy

        if not filhos:
            pos[nome] = (x_esq, y)
            return x_esq + dx

        x_cursor = x_esq
        for filho in filhos:
            x_cursor = self._posicionar_subarvore(filho, x_cursor, pos, dx, dy)

        xs = [pos[filho][0] for filho in filhos]
        pos[nome] = ((min(xs) + max(xs)) / 2.0, y)
        return x_cursor

    def _layout_hierarquico(self):
        """
        Disposição por níveis da Traverse: cada raiz no topo da sua árvore;
        florestas ficam lado a lado.
        """
        pos = {}
        x_cursor = 0.0
        for raiz in self.raizes:
            x_cursor = self._posicionar_subarvore(raiz, x_cursor, pos)
            x_cursor += 1.8
        return pos

    def mostrarGrafo(self):
        """Desenha a árvore/floresta maximal em layout hierárquico (DFS)."""
        Gnx = nx.DiGraph()
        for v in self.G.vertices:
            Gnx.add_node(v.nome)

        rotulos_arestas = {}
        for elo in self.elos_arvore:
            n1, n2 = elo.vertice1.nome, elo.vertice2.nome
            if self.pais.get(n2) == n1:
                pai, filho = n1, n2
            elif self.pais.get(n1) == n2:
                pai, filho = n2, n1
            else:
                pai, filho = n1, n2
            Gnx.add_edge(pai, filho)
            rotulos_arestas[(pai, filho)] = elo.nome

        pos = self._layout_hierarquico()

        raizes = set(self.raizes)
        folhas = {nome for nome in self.niveis if not self.filhos.get(nome)}
        internos = [n for n in self.niveis if n not in raizes and n not in folhas]

        plt.figure(figsize=(14, 11))
        plt.title(
            "Árvore maximal em layout hierárquico "
            "(raiz no topo; camadas = níveis da DFS)"
        )

        nx.draw_networkx_nodes(
            Gnx, pos, nodelist=list(raizes), node_size=2200,
            node_color="gold", node_shape="s",
        )
        nx.draw_networkx_nodes(
            Gnx, pos, nodelist=internos, node_size=1800,
            node_color="skyblue",
        )
        nx.draw_networkx_nodes(
            Gnx, pos, nodelist=list(folhas - raizes), node_size=1800,
            node_color="palegreen",
        )

        rotulos_nos = {
            nome: f"{nome}\n(n={self.niveis[nome]})"
            for nome in self.niveis
        }
        nx.draw_networkx_labels(Gnx, pos, labels=rotulos_nos, font_size=8, font_weight="bold")

        nx.draw_networkx_edges(
            Gnx,
            pos,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=18,
            edge_color="forestgreen",
            width=2.4,
            connectionstyle="arc3,rad=0.0",
        )
        nx.draw_networkx_edge_labels(
            Gnx,
            pos,
            edge_labels=rotulos_arestas,
            font_color="black",
            font_size=8,
        )

        plt.legend(
            handles=[
                Patch(facecolor="gold", label="Raiz"),
                Patch(facecolor="skyblue", label="Nó interno"),
                Patch(facecolor="palegreen", label="Folha"),
            ],
            loc="upper right",
        )

        plt.axis("off")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    q6 = _carregar_modulo_q6()
    g = q6.montar_multigrafo_teste()

    solucao = SubgrafoMaximalArvore(g)
    solucao.construir()
    solucao.imprimir_resultado()
    solucao.mostrarGrafo()
