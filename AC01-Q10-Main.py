from collections import defaultdict
from math import sqrt

import matplotlib.pyplot as plt
import networkx as nx

from Multigrafo import Multigrafo


def chave_ligacao(elo):
    """
    Identidade de uma ligação para comparação de conjuntos E(G):
    par de vértices (u, v) + orientação.
    Elo orientado: (u -> v). Elo não orientado: {u, v} (ordem canônica).
    """
    n1, n2 = elo.vertice1.nome, elo.vertice2.nome
    if elo.isOrientado:
        return ("dir", n1, n2)
    return ("undir", tuple(sorted((n1, n2))))


def conjunto_elos(grafo):
    return {chave_ligacao(elo) for elo in grafo.elos}


def adjacentes(grafo, nome_vertice):
    """
    Adj(u) no multigrafo misto:
    - elo orientado: somente vertice1 alcança vertice2;
    - elo não orientado: alcance bidirecional.
    """
    vertice = grafo.buscarVertice(nome_vertice)
    if vertice is None:
        return set()

    vizinhos = set()
    for elo in vertice.elos:
        if elo.isOrientado:
            if elo.vertice1 is vertice:
                vizinhos.add(elo.vertice2.nome)
        else:
            if elo.vertice1 is vertice:
                vizinhos.add(elo.vertice2.nome)
            elif elo.vertice2 is vertice:
                vizinhos.add(elo.vertice1.nome)
    return vizinhos


def _seguro_jaccard(inter, uniao):
    if uniao == 0:
        return 1.0
    return inter / uniao


def _seguro_overlap(inter, tam_a, tam_b):
    menor = min(tam_a, tam_b)
    if menor == 0:
        return 1.0 if tam_a == 0 and tam_b == 0 else 0.0
    return inter / menor


def _seguro_cosseno(inter, tam_a, tam_b):
    if tam_a == 0 or tam_b == 0:
        return 1.0 if tam_a == 0 and tam_b == 0 else 0.0
    return inter / (sqrt(tam_a) * sqrt(tam_b))


def similaridade_conjuntos(a, b):
    inter = len(a & b)
    uniao = len(a | b)
    return {
        "inter": inter,
        "uniao": uniao,
        "tam_a": len(a),
        "tam_b": len(b),
        "jaccard": _seguro_jaccard(inter, uniao),
        "cosseno": _seguro_cosseno(inter, len(a), len(b)),
        "overlap": _seguro_overlap(inter, len(a), len(b)),
    }


def similaridade_global(g1, g2):
    return similaridade_conjuntos(conjunto_elos(g1), conjunto_elos(g2))


def similaridade_local_vertices(g1, g2):
    """
    Vértices homólogos: mesmo nome em G1 e G2.
    Métricas sobre Adj(u) em cada grafo; devolve tabela por vértice e médias.
    """
    nomes = sorted(
        {v.nome for v in g1.vertices} & {v.nome for v in g2.vertices},
        key=lambda n: (len(n), n),
    )

    linhas = []
    for nome in nomes:
        met = similaridade_conjuntos(adjacentes(g1, nome), adjacentes(g2, nome))
        met["vertice"] = nome
        linhas.append(met)

    n = len(linhas) or 1
    medias = {
        "jaccard": sum(l["jaccard"] for l in linhas) / n,
        "cosseno": sum(l["cosseno"] for l in linhas) / n,
        "overlap": sum(l["overlap"] for l in linhas) / n,
    }
    return linhas, medias


def _pct(valor):
    return f"{valor * 100:6.2f}%"


def imprimir_resultados(g1, g2, global_, locais, medias):
    print("=" * 72)
    print("Similaridade de grafos: Jaccard, Cosseno e Coeficiente de Sobreposição")
    print("=" * 72)

    print("\nEstrutura global")
    print("-" * 72)
    print(f"  |V(G1)| = {len(g1.vertices):>3}     |E(G1)| = {global_['tam_a']:>3}")
    print(f"  |V(G2)| = {len(g2.vertices):>3}     |E(G2)| = {global_['tam_b']:>3}")
    print(f"  |E(G1) AND E(G2)| = {global_['inter']}")
    print(f"  |E(G1) OR  E(G2)| = {global_['uniao']}")

    print("\nMétricas globais (conjuntos de ligações)")
    print("-" * 72)
    print(f"{'Métrica':<28} {'Índice':>10} {'Percentual':>12}")
    print("-" * 72)
    print(f"{'Jaccard':<28} {global_['jaccard']:>10.4f} {_pct(global_['jaccard']):>12}")
    print(f"{'Cosseno':<28} {global_['cosseno']:>10.4f} {_pct(global_['cosseno']):>12}")
    print(f"{'Sobreposição (Overlap)':<28} {global_['overlap']:>10.4f} {_pct(global_['overlap']):>12}")
    print("-" * 72)

    print("\nSimilaridade local por vértice homólogo (Adj(u) em G1 vs Adj(u) em G2)")
    print("-" * 72)
    print(f"{'Vertice':<10} {'|Adj1|':>7} {'|Adj2|':>7} {'|inter|':>7} "
          f"{'Jaccard':>10} {'Cosseno':>10} {'Overlap':>10}")
    print("-" * 72)
    for linha in locais:
        print(
            f"{linha['vertice']:<10} {linha['tam_a']:>7} {linha['tam_b']:>7} "
            f"{linha['inter']:>7} {_pct(linha['jaccard']):>10} "
            f"{_pct(linha['cosseno']):>10} {_pct(linha['overlap']):>10}"
        )
    print("-" * 72)
    print(
        f"{'Media':<10} {'':>7} {'':>7} {'':>7} "
        f"{_pct(medias['jaccard']):>10} {_pct(medias['cosseno']):>10} "
        f"{_pct(medias['overlap']):>10}"
    )
    print("-" * 72)


def desenhar_em_eixo(grafo, ax, titulo):
    G = nx.MultiDiGraph()
    for v in grafo.vertices:
        G.add_node(v.nome)

    pos = nx.circular_layout(G)
    ax.set_title(titulo)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=700, node_color="skyblue")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_weight="bold")

    conexoes_pares = defaultdict(list)
    for elo in grafo.elos:
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
                rad = 0.1 if elo.isOrientado else 0.0
            else:
                fator = (idx // 2 + 1) * 0.25
                rad = fator if idx % 2 == 0 else -fator

            estilo = f"arc3,rad={rad}"
            if elo.isOrientado:
                nx.draw_networkx_edges(
                    G, pos, ax=ax, edgelist=[(origem, destino)],
                    arrows=True, arrowstyle="->", arrowsize=14,
                    edge_color="red", connectionstyle=estilo,
                )
            else:
                nx.draw_networkx_edges(
                    G, pos, ax=ax, edgelist=[(origem, destino)],
                    arrowstyle="-", edge_color="blue", connectionstyle=estilo,
                )
        rotulos_pares[(par[0], par[1])] = "\n".join(textos_rotulos)

    nx.draw_networkx_edge_labels(
        G, pos, ax=ax, edge_labels=rotulos_pares, font_size=7,
    )
    ax.axis("off")


def mostrar_grafos_lado_a_lado(g1, g2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Comparação visual de G1 e G2 (vermelho = orientado, azul = não orientado)")
    desenhar_em_eixo(g1, ax1, f"G1  (|V|={len(g1.vertices)}, |E|={len(g1.elos)})")
    desenhar_em_eixo(g2, ax2, f"G2  (|V|={len(g2.vertices)}, |E|={len(g2.elos)})")
    plt.tight_layout()
    plt.show()


def montar_grafos_similares_teste():
    """
    Dois multigrafos mistos com 10 vértices (V1..V10).
    9 ligações idênticas (par + orientação) e 6 exclusivas em cada um:
    Overlap = 9/15 = 60%.
    """
    g1 = Multigrafo([], [])
    g2 = Multigrafo([], [])
    for i in range(1, 11):
        g1.adicionarVertice(f"V{i}")
        g2.adicionarVertice(f"V{i}")

    comuns = [
        ("c1", "V1", "V2", True, 1),
        ("c2", "V2", "V3", False, 1),
        ("c3", "V3", "V4", True, 1),
        ("c4", "V4", "V5", False, 1),
        ("c5", "V5", "V6", True, 1),
        ("c6", "V1", "V6", False, 1),
        ("c7", "V6", "V7", False, 1),
        ("c8", "V7", "V8", True, 1),
        ("c9", "V8", "V9", False, 1),
    ]
    for nome, a, b, orient, peso in comuns:
        g1.adicionarElo(nome, a, b, isOrientado=orient, peso=peso)
        g2.adicionarElo(nome, a, b, isOrientado=orient, peso=peso)

    exclusivos_g1 = [
        ("a1", "V9", "V10", True, 1),
        ("a2", "V2", "V8", False, 1),
        ("a3", "V3", "V7", True, 1),
        ("a4", "V4", "V10", True, 1),
        ("a5", "V1", "V5", False, 1),
        ("a6", "V9", "V1", True, 1),
    ]
    for nome, a, b, orient, peso in exclusivos_g1:
        g1.adicionarElo(nome, a, b, isOrientado=orient, peso=peso)

    exclusivos_g2 = [
        ("b1", "V9", "V10", False, 1),
        ("b2", "V2", "V5", True, 1),
        ("b3", "V3", "V9", False, 1),
        ("b4", "V4", "V8", False, 1),
        ("b5", "V10", "V6", True, 1),
        ("b6", "V7", "V10", False, 1),
    ]
    for nome, a, b, orient, peso in exclusivos_g2:
        g2.adicionarElo(nome, a, b, isOrientado=orient, peso=peso)

    return g1, g2


if __name__ == "__main__":
    g1, g2 = montar_grafos_similares_teste()
    global_ = similaridade_global(g1, g2)
    locais, medias = similaridade_local_vertices(g1, g2)
    imprimir_resultados(g1, g2, global_, locais, medias)
    mostrar_grafos_lado_a_lado(g1, g2)
