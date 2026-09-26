import importlib.util
import os
from collections import defaultdict
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from Multigrafo import Elo, Multigrafo, Vertice


def _carregar_modulo_q6():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AC01-Q6-Main.py")
    spec = importlib.util.spec_from_file_location("ac01_q6_main", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class SubgrafoMaximalArvore:
    def __init__(self, G: Multigrafo):
        self.G = G
        self.elos_arvore: List[Elo] = []
        self.componentes = 0
        self.T: Multigrafo | None = None
        self.raizes: List[str] = []
        self.pais: dict = {}
        self.filhos: dict = defaultdict(list)
        self.niveis: dict = {}

    def _adjacencias_subjacentes(self, vertice):
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

        print(f"Analisando o grafo fornecido ({n_v} vértices e {len(self.G.elos)} elos)...")
        print("Construindo subgrafo maximal árvore (floresta maximal) por DFS...")

        if self.raizes:
            print("Componentes encontradas:", self.componentes)
            print("Raízes de cada árvore:", ", ".join(self.raizes))

        print("\nElos selecionados para a árvore/floresta (|E_T| = {}):".format(n_e))
        if n_e == 0:
            print("  (nenhum elo - grafo com vértices isolados)")
        else:
            print("  " + ", ".join(e.nome for e in self.elos_arvore))

        nomes_arvore = {elo.nome for elo in self.elos_arvore}
        elos_descartados = [elo for elo in self.G.elos if elo.nome not in nomes_arvore]
        if elos_descartados:
            print("\nElos descartados (formariam ciclo no grafo subjacente):")
            print("  " + ", ".join(elo.nome for elo in elos_descartados))

        print("\nValidação da propriedade de árvore/floresta:")
        print(f"  |V| = {n_v}")
        print(f"  |E_T| = {n_e}")
        print(f"  Componentes conexas (C) = {c}")
        print(f"  Verificação |E_T| = |V| - C: {n_e} = {n_v} - {c} = {n_v - c}")
        if c == 1:
            print("  Grafo subjacente é conexo: temos uma árvore geradora única.")
        else:
            print("  Grafo subjacente é desconexo: floresta maximal com C árvores.")
        print(f"  Resultado da validação: {'OK' if valido else 'FALHOU'}")

        if self.niveis:
            print("\nHierarquia da DFS (níveis / pais / filhos):")
            for v in self.G.vertices:
                nome = v.nome
                nivel = self.niveis.get(nome, "-")
                pai = self.pais.get(nome, "(raiz)")
                filhos = ", ".join(self.filhos.get(nome, [])) or "(folha)"
                print(f"  {nome}: nível {nivel}, pai={pai}, filhos={filhos}")

    def _posicionar_subarvore(self, nome, x_esq, pos, dx=1.8, dy=1.6):
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
        pos = {}
        x_cursor = 0.0
        for raiz in self.raizes:
            x_cursor = self._posicionar_subarvore(raiz, x_cursor, pos)
            x_cursor += 1.8
        return pos

    def mostrarGrafo(self):
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

        n = len(self.G.vertices)
        if n <= 20:
            pos = self._layout_hierarquico()
        else:
            pos = nx.spring_layout(Gnx, seed=42, k=2.0)

        raizes = set(self.raizes)
        folhas = {nome for nome in self.niveis if not self.filhos.get(nome)}
        internos = [n for n in self.niveis if n not in raizes and n not in folhas]

        largura = max(10, min(20, n * 0.9))
        altura = max(8, min(14, n * 0.75))

        plt.figure(figsize=(largura, altura))
        plt.title("Resultado da Árvore Maximal - Q8")

        tam_no = max(400, min(2200, 20000 // max(1, n)))
        tam_fonte = max(6, min(11, 150 // max(1, n)))

        if raizes:
            nx.draw_networkx_nodes(
                Gnx, pos, nodelist=list(raizes), node_size=tam_no,
                node_color="gold", node_shape="s",
            )
        if internos:
            nx.draw_networkx_nodes(
                Gnx, pos, nodelist=internos, node_size=tam_no,
                node_color="skyblue",
            )
        folhas_nao_raizes = list(folhas - raizes)
        if folhas_nao_raizes:
            nx.draw_networkx_nodes(
                Gnx, pos, nodelist=folhas_nao_raizes, node_size=tam_no,
                node_color="palegreen",
            )

        rotulos_nos = {
            nome: f"{nome}\n(n={self.niveis[nome]})"
            for nome in self.niveis
        }
        nx.draw_networkx_labels(Gnx, pos, labels=rotulos_nos, font_size=tam_fonte, font_weight="bold")

        nx.draw_networkx_edges(
            Gnx,
            pos,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=16,
            edge_color="forestgreen",
            width=2.0,
            connectionstyle="arc3,rad=0.0",
        )
        nx.draw_networkx_edge_labels(
            Gnx,
            pos,
            edge_labels=rotulos_arestas,
            font_color="black",
            font_size=max(5, tam_fonte - 1),
        )

        plt.legend(
            handles=[
                Patch(facecolor="gold", label="Raiz"),
                Patch(facecolor="skyblue", label="Nó interno"),
                Patch(facecolor="palegreen", label="Folha"),
            ],
            loc="upper right",
            fontsize=tam_fonte,
        )

        plt.axis("off")
        plt.tight_layout()
        plt.show()


def montar_multigrafo_demonstracao() -> Multigrafo:
    try:
        q6 = _carregar_modulo_q6()
        return q6.montar_multigrafo_demonstracao()
    except Exception:
        g = Multigrafo([], [])
        for i in range(1, 11):
            g.adicionarVertice(f"V{i}")
        arestas = [("V1","V2"),("V2","V3"),("V3","V4"),("V4","V5"),("V1","V5"),
                   ("V5","V6"),("V6","V7"),("V7","V8"),("V8","V9"),("V9","V10"),("V7","V10")]
        for idx, (a, b) in enumerate(arestas, 1):
            g.adicionarElo(f"e{idx}", a, b, isOrientado=(idx % 4 == 0), peso=1)
        return g


def executar_questao_8(grafo: Multigrafo, mostrar_grafico=True):
    print("Questão 8 - Subgrafo maximal árvore / floresta maximal")
    solucao = SubgrafoMaximalArvore(grafo)
    solucao.construir()
    solucao.imprimir_resultado()
    if mostrar_grafico:
        solucao.mostrarGrafo()
    return solucao


if __name__ == "__main__":
    grafo_demonstracao = montar_multigrafo_demonstracao()
    executar_questao_8(grafo_demonstracao)
