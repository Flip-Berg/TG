from collections import defaultdict, deque
from heapq import heappop, heappush
from math import inf

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from Multigrafo import Multigrafo


class MultigrafoComExcentricidade(Multigrafo):
    """
    Excentricidade e(v) = max_w d(v, w), com d(v, w) geodésica.
    BFS (quantidade de elos) ou Dijkstra (menor custo), respeitando
    orientação no multigrafo misto. Inalcançável => distancia infinita.
    """

    def _saidas(self, vertice):
        """Pares (vizinho, elo) alcançáveis a partir de vertice."""
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
        return sorted(
            (v.nome for v in self.vertices),
            key=lambda n: int(n[1:]) if n[1:].isdigit() else n,
        )

    def distancias_minimas(self, nome_vertice, considerar_peso=False):
        origem = self.buscarVertice(nome_vertice)
        if origem is None:
            raise ValueError(f"Vertice '{nome_vertice}' nao encontrado.")
        if considerar_peso:
            return self._dijkstra(origem)
        return self._bfs(origem)

    def excentricidade(self, nome_vertice, considerar_peso=False):
        """
        Calcula d(v, w) para todo w e devolve e(v) = max d(v, w),
        os vertices mais distantes e os caminhos correspondentes.
        """
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
        return "inf"
    if float(valor).is_integer():
        return str(int(valor))
    return f"{valor:.2f}"


def imprimir_vertice(resultado, g):
    modo = "ponderado (Dijkstra)" if resultado["considerar_peso"] else "nao ponderado (BFS)"
    v = resultado["vertice"]
    print("=" * 72)
    print(f"Excentricidade de {v}  [{modo}]")
    print("=" * 72)
    print(f"  e({v}) = max d({v}, w) = {_fmt_dist(resultado['e_v'])}")
    print("  Vertices mais distantes: " + ", ".join(resultado["mais_distantes"]))

    print("\n  Distancia geodesica a partir de", v)
    print("  " + "-" * 40)
    print(f"  {'w':<8} {'d(v, w)':>10}")
    print("  " + "-" * 40)
    for nome in g._nomes_ordenados():
        print(f"  {nome:<8} {_fmt_dist(resultado['distancias'][nome]):>10}")
    print("  " + "-" * 40)

    for w, caminho in resultado["caminhos"].items():
        if caminho:
            print(f"  Caminho {v} -> {w}: " + " -> ".join(caminho))
        else:
            print(f"  Caminho {v} -> {w}: inexistente (inalcancavel)")


def imprimir_tabela_todos(g, todos, considerar_peso=False):
    modo = "ponderado (Dijkstra)" if considerar_peso else "nao ponderado (BFS)"
    nomes = g._nomes_ordenados()
    valores = {n: todos[n]["e_v"] for n in nomes}
    e_min = min(valores.values())
    e_max = max(valores.values())
    centrais = [n for n, e in valores.items() if e == e_min]
    perifericos = [n for n, e in valores.items() if e == e_max]

    print("\n" + "=" * 72)
    print(f"Excentricidade de todos os vertices  [{modo}]")
    print("=" * 72)
    print(f"{'Vertice':<10} {'e(v)':>8} {'Mais distantes':<28} {'Papel'}")
    print("-" * 72)
    for n in nomes:
        papeis = []
        if n in centrais:
            papeis.append("CENTRAL")
        if n in perifericos:
            papeis.append("PERIFERICO")
        distantes = ", ".join(todos[n]["mais_distantes"])
        print(f"{n:<10} {_fmt_dist(valores[n]):>8} {distantes:<28} {', '.join(papeis)}")
    print("-" * 72)
    print(f"Raio  r(G) = min e(v) = {_fmt_dist(e_min)}  |  vertices centrais: {', '.join(centrais)}")
    print(f"Diametro D(G) = max e(v) = {_fmt_dist(e_max)}  |  vertices perifericos: {', '.join(perifericos)}")
    return centrais, perifericos


def mostrar_excentricidade(g, resultado):
    v = resultado["vertice"]
    alvo = resultado["mais_distantes"][0]
    caminho_verts = set(resultado["caminhos"].get(alvo, []))
    caminho_elos = {id(elo) for elo in resultado["elos_caminho"].get(alvo, [])}

    Gnx = nx.MultiDiGraph()
    for vert in g.vertices:
        Gnx.add_node(vert.nome)
    pos = nx.spring_layout(Gnx, seed=12, k=1.3)

    plt.figure(figsize=(13, 10))
    plt.title(
        f"Excentricidade de {v}: e({v}) = {_fmt_dist(resultado['e_v'])}  "
        f"(caminho ate {alvo})"
    )

    outros = [n for n in Gnx.nodes if n not in caminho_verts]
    if outros:
        nx.draw_networkx_nodes(Gnx, pos, nodelist=outros, node_size=900, node_color="lightgray")
    intermediarios = [n for n in caminho_verts if n != v and n != alvo]
    if intermediarios:
        nx.draw_networkx_nodes(
            Gnx, pos, nodelist=intermediarios, node_size=1100, node_color="palegreen"
        )
    nx.draw_networkx_nodes(Gnx, pos, nodelist=[v], node_size=1500, node_color="gold", node_shape="s")
    nx.draw_networkx_nodes(Gnx, pos, nodelist=[alvo], node_size=1500, node_color="salmon")
    nx.draw_networkx_labels(Gnx, pos, font_size=9, font_weight="bold")

    conexoes_pares = defaultdict(list)
    for elo in g.elos:
        par = tuple(sorted([elo.vertice1.nome, elo.vertice2.nome]))
        conexoes_pares[par].append(elo)

    rotulos = {}
    for par, lista in conexoes_pares.items():
        textos = []
        for idx, elo in enumerate(lista):
            origem, destino = elo.vertice1.nome, elo.vertice2.nome
            textos.append(f"{elo.nome} (p={elo.peso})")
            no_caminho = id(elo) in caminho_elos
            cor = "forestgreen" if no_caminho else "lightgray"
            largura = 3.0 if no_caminho else 1.0
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
                    edge_color=cor, width=largura, connectionstyle=estilo,
                )
            else:
                nx.draw_networkx_edges(
                    Gnx, pos, edgelist=[(origem, destino)],
                    arrowstyle="-", edge_color=cor, width=largura,
                    connectionstyle=estilo,
                )
        rotulos[(par[0], par[1])] = "\n".join(textos)

    nx.draw_networkx_edge_labels(Gnx, pos, edge_labels=rotulos, font_size=7)
    plt.legend(
        handles=[
            Patch(facecolor="gold", label=f"v selecionado ({v})"),
            Patch(facecolor="salmon", label=f"mais distante ({alvo})"),
            Patch(facecolor="palegreen", label="vertices do caminho geodesico"),
            Patch(facecolor="forestgreen", label="elos do caminho"),
        ],
        loc="upper right",
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def montar_grafo_teste():
    """Multigrafo misto ponderado com 12 vertices."""
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


if __name__ == "__main__":
    g = montar_grafo_teste()
    vertice_escolhido = "V1"

    res_bfs = g.excentricidade(vertice_escolhido, considerar_peso=False)
    imprimir_vertice(res_bfs, g)

    res_dij = g.excentricidade(vertice_escolhido, considerar_peso=True)
    print(f"\n  Comparacao ponderada: e({vertice_escolhido}) = {_fmt_dist(res_dij['e_v'])} "
          f"| mais distantes: {', '.join(res_dij['mais_distantes'])}")
    for w, caminho in res_dij["caminhos"].items():
        if caminho:
            print(f"  Caminho ponderado {vertice_escolhido} -> {w}: " + " -> ".join(caminho))

    todos = g.excentricidade_todos(considerar_peso=False)
    imprimir_tabela_todos(g, todos, considerar_peso=False)
    mostrar_excentricidade(g, res_bfs)
