from collections import defaultdict, deque
import math

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from Multigrafo import Multigrafo


class MultigrafoComCortes(Multigrafo):
    def _nomes_ordenados(self):
        return sorted((v.nome for v in self.vertices), key=lambda n: (len(n), n))

    def _vizinhos_subjacentes(self, nome, ignorar_vertices=None, ignorar_elos=None):
        ignorar_vertices = ignorar_vertices or set()
        ignorar_elos = ignorar_elos or set()
        if nome in ignorar_vertices:
            return []

        vertice = self.buscarVertice(nome)
        if vertice is None:
            return []

        vizinhos = []
        vistos = set()
        for elo in vertice.elos:
            if id(elo) in ignorar_elos:
                continue
            if elo.vertice1.nome == nome:
                outro = elo.vertice2.nome
            elif elo.vertice2.nome == nome:
                outro = elo.vertice1.nome
            else:
                continue
            if outro in ignorar_vertices or outro == nome or outro in vistos:
                continue
            vistos.add(outro)
            vizinhos.append(outro)
        return vizinhos

    def numero_componentes(self, ignorar_vertices=None, ignorar_elos=None):
        ignorar_vertices = ignorar_vertices or set()
        ativos = [n for n in self._nomes_ordenados() if n not in ignorar_vertices]
        visitados = set()
        componentes = 0

        for origem in ativos:
            if origem in visitados:
                continue
            componentes += 1
            fila = deque([origem])
            visitados.add(origem)
            while fila:
                atual = fila.popleft()
                for viz in self._vizinhos_subjacentes(atual, ignorar_vertices, ignorar_elos):
                    if viz not in visitados:
                        visitados.add(viz)
                        fila.append(viz)
        return componentes

    def vertices_de_corte(self):
        c0 = self.numero_componentes()
        articulacoes = []
        detalhes = []
        for nome in self._nomes_ordenados():
            c1 = self.numero_componentes(ignorar_vertices={nome})
            if c1 > c0:
                articulacoes.append(nome)
                detalhes.append({"vertice": nome, "C_antes": c0, "C_depois": c1})
        return articulacoes, detalhes, c0

    def elos_de_corte(self):
        c0 = self.numero_componentes()
        pontes = []
        detalhes = []
        for elo in self.elos:
            c1 = self.numero_componentes(ignorar_elos={id(elo)})
            if c1 > c0:
                pontes.append(elo)
                detalhes.append({
                    "elo": elo.nome,
                    "v1": elo.vertice1.nome,
                    "v2": elo.vertice2.nome,
                    "C_antes": c0,
                    "C_depois": c1,
                })
        return pontes, detalhes, c0

    def conjunto_corte_vertices_minimo(self):
        articulacoes, _, c0 = self.vertices_de_corte()
        if articulacoes:
            exemplo = [articulacoes[0]]
            c1 = self.numero_componentes(ignorar_vertices=set(exemplo))
            return exemplo, 1, c0, c1
        return [], None, c0, c0

    def conjunto_corte_arestas_minimo(self):
        pontes, _, c0 = self.elos_de_corte()
        if pontes:
            exemplo = [pontes[0]]
            c1 = self.numero_componentes(ignorar_elos={id(pontes[0])})
            return exemplo, 1, c0, c1
        return [], None, c0, c0


def imprimir_resultados(g):
    print("Questão 14 - Cortes em vértices e arestas (grafo subjacente)")
    print(f"Analisando o grafo fornecido ({len(g.vertices)} vértices, {len(g.elos)} elos)...")

    articulacoes, det_v, c0 = g.vertices_de_corte()
    pontes, det_e, _ = g.elos_de_corte()
    corte_v, kappa, _, c_v = g.conjunto_corte_vertices_minimo()
    corte_e, lamb, _, c_e = g.conjunto_corte_arestas_minimo()

    print(f"Componentes conexas (antes dos cortes): {c0}")

    print("\nPontos de articulação (corte em vértices de tamanho 1):")
    if not articulacoes:
        print("  Nenhum ponto de articulação encontrado (grafo é 2-vértice-conexo ou trivial).")
    else:
        print("  " + ", ".join(articulacoes))
        for d in det_v:
            print(f"    Remover {d['vertice']}: C passa de {d['C_antes']} para {d['C_depois']}")

    print("\nPontes (corte em arestas de tamanho 1):")
    if not pontes:
        print("  Nenhuma ponte encontrada (grafo é 2-aresta-conexo ou trivial).")
    else:
        print("  " + ", ".join(p.nome for p in pontes))
        for d in det_e:
            print(f"    Remover {d['elo']} ({d['v1']}--{d['v2']}): C passa de {d['C_antes']} para {d['C_depois']}")

    print("\nConectividade e cortes mínimos:")
    if kappa is not None:
        print(f"  κ(G) = {kappa} (conectividade em vértices)")
        print(f"  Exemplo de corte mínimo em vértices: {{{', '.join(corte_v)}}} → C = {c_v}")
    else:
        print("  Nenhum corte de 1 vértice; κ(G) ≥ 2.")

    if lamb is not None:
        nomes_e = [e.nome for e in corte_e]
        print(f"  λ(G) = {lamb} (conectividade em arestas)")
        print(f"  Exemplo de corte mínimo em arestas: {{{', '.join(nomes_e)}}} → C = {c_e}")
    else:
        print("  Nenhuma ponte; λ(G) ≥ 2.")

    return articulacoes, pontes


def mostrar_cortes(g, articulacoes, pontes):
    arts = set(articulacoes)
    ids_pontes = {id(e) for e in pontes}

    Gnx = nx.MultiDiGraph()
    for v in g.vertices:
        Gnx.add_node(v.nome)

    n = len(Gnx.nodes)
    if n <= 15:
        pos = nx.spring_layout(Gnx, seed=42, k=2.0)
    else:
        pos = nx.spring_layout(Gnx, seed=42, k=3.0)

    largura = max(10, min(18, n * 0.9))
    altura = max(7, min(13, n * 0.7))
    plt.figure(figsize=(largura, altura))
    plt.title("Resultado dos Cortes - Q14")

    tam_no = max(500, min(1500, 14000 // max(1, n)))
    fonte = max(7, min(12, 140 // max(1, n)))

    demais = [n for n in Gnx.nodes if n not in arts]
    if demais:
        nx.draw_networkx_nodes(Gnx, pos, nodelist=demais, node_size=tam_no, node_color="skyblue")
    if arts:
        nx.draw_networkx_nodes(
            Gnx, pos, nodelist=list(arts), node_size=tam_no + 400,
            node_color="gold", node_shape="s",
        )
    nx.draw_networkx_labels(Gnx, pos, font_size=fonte, font_weight="bold")

    conexoes_pares = defaultdict(list)
    for elo in g.elos:
        par = tuple(sorted([elo.vertice1.nome, elo.vertice2.nome]))
        conexoes_pares[par].append(elo)

    rotulos = {}
    for par, lista in conexoes_pares.items():
        textos = []
        for idx, elo in enumerate(lista):
            origem, destino = elo.vertice1.nome, elo.vertice2.nome
            eh_ponte = id(elo) in ids_pontes
            textos.append(f"{elo.nome}" + (" [P]" if eh_ponte else ""))
            if len(lista) == 1:
                rad = 0.12 if elo.isOrientado else 0.0
            else:
                fator = (idx // 2 + 1) * 0.25
                rad = fator if idx % 2 == 0 else -fator
            estilo = f"arc3,rad={rad}"
            cor = "darkorange" if eh_ponte else ("red" if elo.isOrientado else "steelblue")
            largura_linha = 3.0 if eh_ponte else 1.2
            if elo.isOrientado:
                nx.draw_networkx_edges(
                    Gnx, pos, edgelist=[(origem, destino)],
                    arrows=True, arrowstyle="->", arrowsize=14,
                    edge_color=cor, width=largura_linha, connectionstyle=estilo,
                )
            else:
                nx.draw_networkx_edges(
                    Gnx, pos, edgelist=[(origem, destino)],
                    arrowstyle="-", edge_color=cor, width=largura_linha,
                    connectionstyle=estilo,
                )
        rotulos[(par[0], par[1])] = "\n".join(textos)

    if n <= 25:
        nx.draw_networkx_edge_labels(Gnx, pos, edge_labels=rotulos, font_size=max(5, fonte - 2))

    plt.legend(
        handles=[
            Patch(facecolor="gold", label="Ponto de articulação"),
            Patch(facecolor="skyblue", label="Demais vértices"),
            Patch(facecolor="darkorange", label="Ponte (elo de corte)"),
            Patch(facecolor="steelblue", label="Elo não orientado"),
            Patch(facecolor="red", label="Elo orientado"),
        ],
        loc="upper right",
        fontsize=max(6, fonte - 1),
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def montar_grafo_demonstracao():
    g = MultigrafoComCortes([], [])
    for i in range(1, 15):
        g.adicionarVertice(f"V{i}")

    for a, b, orient, nome in [
        ("V1","V2",False,"e1"), ("V2","V3",True,"e2"), ("V3","V4",False,"e3"),
        ("V4","V5",False,"e4"), ("V5","V6",True,"e5"), ("V6","V7",False,"e6"),
        ("V7","V1",False,"e7"), ("V1","V3",False,"e8"), ("V2","V4",False,"e9"),
        ("V3","V5",False,"e10"), ("V4","V6",False,"e11"), ("V5","V7",False,"e12"),
        ("V6","V1",True,"e13"), ("V7","V8",False,"e16"),
        ("V8","V9",False,"e17"), ("V9","V10",True,"e18"), ("V10","V11",False,"e19"),
        ("V11","V12",False,"e20"), ("V12","V13",True,"e21"), ("V13","V14",False,"e22"),
        ("V14","V8",False,"e23"), ("V8","V10",False,"e24"), ("V9","V11",False,"e25"),
        ("V10","V12",False,"e26"), ("V11","V13",False,"e27"), ("V12","V14",False,"e28"),
        ("V13","V8",True,"e29"),
    ]:
        g.adicionarElo(nome, a, b, isOrientado=orient, peso=1)
    return g


def executar_questao_14(grafo: Multigrafo, mostrar_grafico=True):
    if not isinstance(grafo, MultigrafoComCortes):
        g = MultigrafoComCortes([], [])
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

    articulacoes, pontes = imprimir_resultados(g)
    if mostrar_grafico:
        mostrar_cortes(g, articulacoes, pontes)
    return g


if __name__ == "__main__":
    grafo_demonstracao = montar_grafo_demonstracao()
    executar_questao_14(grafo_demonstracao)
