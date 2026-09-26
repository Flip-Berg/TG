from collections import defaultdict, deque
from heapq import heappop, heappush
from math import inf

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from Multigrafo import Multigrafo


class MultigrafoComExcentricidade(Multigrafo):
    def _saidas(self, vertice):
        saidas = []
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
            if vizinho is not None and vizinho is not vertice:
                saidas.append((vizinho, elo))
        return saidas

    def _bfs(self, origem):
        dist = {origem.nome: 0.0}
        pred = {origem.nome: None}
        fila = deque([origem])

        while fila:
            atual = fila.popleft()
            for vizinho, elo in self._saidas(atual):
                if vizinho.nome not in dist:
                    dist[vizinho.nome] = dist[atual.nome] + 1.0
                    pred[vizinho.nome] = (atual.nome, elo)
                    fila.append(vizinho)
        return dist, pred

    def _dijkstra(self, origem):
        dist = {origem.nome: 0.0}
        pred = {origem.nome: None}
        heap = [(0.0, origem.nome)]
        visitando = {origem.nome: origem}

        while heap:
            custo, nome_atual = heappop(heap)
            if custo > dist.get(nome_atual, inf):
                continue
            atual = visitando[nome_atual]
            for vizinho, elo in self._saidas(atual):
                novo = custo + float(elo.peso)
                if novo < dist.get(vizinho.nome, inf):
                    dist[vizinho.nome] = novo
                    pred[vizinho.nome] = (nome_atual, elo)
                    visitando[vizinho.nome] = vizinho
                    heappush(heap, (novo, vizinho.nome))
        return dist, pred

    def _reconstruir_caminho(self, pred, destino):
        if destino not in pred:
            return [], []
        vertices = [destino]
        elos = []
        atual = destino
        while pred[atual] is not None:
            pai, elo = pred[atual]
            elos.append(elo)
            vertices.append(pai)
            atual = pai
        vertices.reverse()
        elos.reverse()
        return vertices, elos

    def _nomes_ordenados(self):
        return sorted((v.nome for v in self.vertices), key=lambda n: (len(n), n))

    def distancias_minimas(self, nome_vertice, considerar_peso=False):
        origem = self.buscarVertice(nome_vertice)
        if origem is None:
            raise ValueError(f"Vértice '{nome_vertice}' não encontrado no grafo.")
        if considerar_peso:
            return self._dijkstra(origem)
        return self._bfs(origem)

    def excentricidade(self, nome_vertice, considerar_peso=False):
        dist, pred = self.distancias_minimas(nome_vertice, considerar_peso)
        nomes = self._nomes_ordenados()

        distancias = {}
        for nome in nomes:
            distancias[nome] = dist.get(nome, inf)

        e_v = max(distancias.values()) if distancias else 0.0
        mais_distantes = [n for n, d in distancias.items() if d == e_v and n != nome_vertice]
        if not mais_distantes and nome_vertice in distancias:
            mais_distantes = [nome_vertice]

        caminhos = {}
        elos_caminho = {}
        for w in mais_distantes:
            if distancias[w] == inf:
                caminhos[w] = []
                elos_caminho[w] = []
            else:
                verts, elos = self._reconstruir_caminho(pred, w)
                caminhos[w] = verts
                elos_caminho[w] = elos

        return {
            "vertice": nome_vertice,
            "considerar_peso": considerar_peso,
            "distancias": distancias,
            "e_v": e_v,
            "mais_distantes": mais_distantes,
            "caminhos": caminhos,
            "elos_caminho": elos_caminho,
        }

    def excentricidade_todos(self, considerar_peso=False):
        return {
            v.nome: self.excentricidade(v.nome, considerar_peso)
            for v in self.vertices
        }


def _fmt_dist(valor):
    if valor == inf:
        return "∞"
    if float(valor).is_integer():
        return str(int(valor))
    return f"{valor:.2f}"


def imprimir_vertice(resultado, g):
    modo = "ponderado (Dijkstra)" if resultado["considerar_peso"] else "não ponderado (BFS)"
    v = resultado["vertice"]
    print(f"Excentricidade de {v} [{modo}]")
    print(f"  e({v}) = max d({v}, w) = {_fmt_dist(resultado['e_v'])}")
    print(f"  Vértices mais distantes: {', '.join(resultado['mais_distantes'])}")
    print(f"  Distâncias geodésicas a partir de {v}:")
    for nome in g._nomes_ordenados():
        print(f"    d({v}, {nome}) = {_fmt_dist(resultado['distancias'][nome])}")

    for w, caminho in resultado["caminhos"].items():
        if caminho:
            print(f"  Caminho {v} -> {w}: " + " -> ".join(caminho))
        else:
            print(f"  Caminho {v} -> {w}: inexistente (inalcançável)")


def imprimir_tabela_todos(g, todos, considerar_peso=False):
    modo = "ponderado (Dijkstra)" if considerar_peso else "não ponderado (BFS)"
    nomes = g._nomes_ordenados()
    valores = {n: todos[n]["e_v"] for n in nomes}

    e_min = min(valores.values()) if valores else 0
    e_max = max(valores.values()) if valores else 0
    centrais = [n for n, e in valores.items() if e == e_min]
    perifericos = [n for n, e in valores.items() if e == e_max]

    print(f"\nExcentricidade de todos os vértices [{modo}]")
    print(f"  {'Vértice':<10} {'e(v)':>8} {'Mais distantes':<20} {'Papel'}")
    for n in nomes:
        papeis = []
        if n in centrais:
            papeis.append("CENTRAL")
        if n in perifericos:
            papeis.append("PERIFÉRICO")
        distantes = ", ".join(todos[n]["mais_distantes"])
        print(f"  {n:<10} {_fmt_dist(valores[n]):>8} {distantes:<20} {', '.join(papeis)}")

    print(f"Raio  r(G) = min e(v) = {_fmt_dist(e_min)}  |  vértices centrais: {', '.join(centrais)}")
    print(f"Diâmetro D(G) = max e(v) = {_fmt_dist(e_max)}  |  vértices periféricos: {', '.join(perifericos)}")
    return centrais, perifericos


def mostrar_excentricidade(g, resultado):
    v = resultado["vertice"]
    alvo = resultado["mais_distantes"][0] if resultado["mais_distantes"] else v
    caminho_verts = set(resultado["caminhos"].get(alvo, []))
    caminho_elos = {id(elo) for elo in resultado["elos_caminho"].get(alvo, [])}

    Gnx = nx.MultiDiGraph()
    for vert in g.vertices:
        Gnx.add_node(vert.nome)

    n = len(Gnx.nodes)
    if n <= 15:
        pos = nx.spring_layout(Gnx, seed=12, k=2.0)
    else:
        pos = nx.spring_layout(Gnx, seed=12, k=3.0)

    largura = max(10, min(18, n * 0.9))
    altura = max(8, min(14, n * 0.75))
    plt.figure(figsize=(largura, altura))
    plt.title(f"Resultado da Excentricidade - Q12: e({v}) = {_fmt_dist(resultado['e_v'])}")

    tam_no = max(500, min(1500, 15000 // max(1, n)))
    fonte = max(7, min(12, 140 // max(1, n)))

    outros = [n for n in Gnx.nodes if n not in caminho_verts]
    if outros:
        nx.draw_networkx_nodes(Gnx, pos, nodelist=outros, node_size=tam_no, node_color="lightgray")
    intermediarios = [n for n in caminho_verts if n != v and n != alvo]
    if intermediarios:
        nx.draw_networkx_nodes(
            Gnx, pos, nodelist=intermediarios, node_size=tam_no + 200, node_color="palegreen"
        )
    if v in Gnx.nodes:
        nx.draw_networkx_nodes(Gnx, pos, nodelist=[v], node_size=tam_no + 600, node_color="gold", node_shape="s")
    if alvo in Gnx.nodes:
        nx.draw_networkx_nodes(Gnx, pos, nodelist=[alvo], node_size=tam_no + 600, node_color="salmon")
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
            textos.append(f"{elo.nome}")
            no_caminho = id(elo) in caminho_elos
            cor = "forestgreen" if no_caminho else "lightgray"
            largura_linha = 3.0 if no_caminho else 1.0
            if len(lista) == 1:
                rad = 0.1 if elo.isOrientado else 0.0
            else:
                fator = (idx // 2 + 1) * 0.25
                rad = fator if idx % 2 == 0 else -fator
            estilo = f"arc3,rad={rad}"
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
            Patch(facecolor="gold", label=f"vértice selecionado ({v})"),
            Patch(facecolor="salmon", label=f"mais distante ({alvo})"),
            Patch(facecolor="palegreen", label="vértices do caminho geodésico"),
            Patch(facecolor="forestgreen", label="elos do caminho"),
        ],
        loc="upper right",
        fontsize=max(6, fonte - 1),
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def montar_grafo_demonstracao():
    g = MultigrafoComExcentricidade([], [])
    for i in range(1, 13):
        g.adicionarVertice(f"V{i}")

    g.adicionarElo("e1", "V1", "V2", isOrientado=False, peso=1)
    g.adicionarElo("e2", "V2", "V3", isOrientado=False, peso=1)
    g.adicionarElo("e3", "V3", "V4", isOrientado=False, peso=4)
    g.adicionarElo("e4", "V4", "V5", isOrientado=False, peso=1)
    g.adicionarElo("e5", "V5", "V6", isOrientado=False, peso=1)
    g.adicionarElo("e6", "V6", "V7", isOrientado=False, peso=1)
    g.adicionarElo("e7", "V7", "V8", isOrientado=False, peso=1)
    g.adicionarElo("e8", "V5", "V9", isOrientado=False, peso=1)
    g.adicionarElo("e9", "V9", "V10", isOrientado=False, peso=1)
    g.adicionarElo("e10", "V6", "V11", isOrientado=False, peso=1)
    g.adicionarElo("e11", "V11", "V12", isOrientado=False, peso=1)
    g.adicionarElo("e12", "V3", "V9", isOrientado=True, peso=1)
    g.adicionarElo("e13", "V10", "V4", isOrientado=True, peso=2)
    g.adicionarElo("e14", "V8", "V12", isOrientado=False, peso=3)
    g.adicionarElo("e15", "V2", "V5", isOrientado=True, peso=2)
    return g


def executar_questao_12(grafo: Multigrafo, nome_vertice=None, considerar_peso=False, mostrar_grafico=True):
    if not isinstance(grafo, MultigrafoComExcentricidade):
        g = MultigrafoComExcentricidade([], [])
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

    print(f"Questão 12 - Excentricidade, raio e diâmetro")
    print(f"Analisando o grafo fornecido ({len(g.vertices)} vértices, {len(g.elos)} elos)...")

    if nome_vertice is None:
        if g.vertices:
            nome_vertice = g.vertices[0].nome
        else:
            print("Grafo vazio: sem vértices para analisar.")
            return None

    res_bfs = g.excentricidade(nome_vertice, considerar_peso=False)
    imprimir_vertice(res_bfs, g)

    if considerar_peso:
        res_dij = g.excentricidade(nome_vertice, considerar_peso=True)
        modo = "ponderado"
        print(f"\nComparativo {modo}: e({nome_vertice}) = {_fmt_dist(res_dij['e_v'])} "
              f"| mais distantes: {', '.join(res_dij['mais_distantes'])}")
        for w, caminho in res_dij["caminhos"].items():
            if caminho:
                print(f"  Caminho {modo} {nome_vertice} -> {w}: " + " -> ".join(caminho))

    todos = g.excentricidade_todos(considerar_peso=False)
    imprimir_tabela_todos(g, todos, considerar_peso=False)
    if mostrar_grafico:
        mostrar_excentricidade(g, res_bfs)
    return g


if __name__ == "__main__":
    grafo_demonstracao = montar_grafo_demonstracao()
    executar_questao_12(grafo_demonstracao)
