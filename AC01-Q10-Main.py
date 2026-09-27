from collections import defaultdict
from math import sqrt

import matplotlib.pyplot as plt
import networkx as nx

from Multigrafo import Multigrafo


def chave_ligacao(elo):
    n1, n2 = elo.vertice1.nome, elo.vertice2.nome
    if elo.isOrientado:
        return ("dir", n1, n2)
    return ("undir", tuple(sorted((n1, n2))))


def conjunto_elos(grafo):
    return {chave_ligacao(elo) for elo in grafo.elos}


def adjacentes(grafo, nome_vertice):
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
    nomes_g1 = {v.nome for v in g1.vertices}
    nomes_g2 = {v.nome for v in g2.vertices}
    nomes = sorted(nomes_g1 & nomes_g2, key=lambda n: (len(n), n))
    so_g1 = sorted(nomes_g1 - nomes_g2, key=lambda n: (len(n), n))
    so_g2 = sorted(nomes_g2 - nomes_g1, key=lambda n: (len(n), n))

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
    return linhas, medias, so_g1, so_g2


def _pct(valor):
    return f"{valor * 100:6.2f}%"


def imprimir_resultados(g1, g2, global_, locais, medias, so_g1, so_g2):
    print("Questão 10 - Similaridade de grafos: Jaccard, Cosseno e Overlap")
    print(f"Analisando G1 ({len(g1.vertices)} vértices, {len(g1.elos)} elos) e "
          f"G2 ({len(g2.vertices)} vértices, {len(g2.elos)} elos)...")

    if so_g1:
        print(f"Vértices presentes só em G1: {', '.join(so_g1)}")
    if so_g2:
        print(f"Vértices presentes só em G2: {', '.join(so_g2)}")

    print("\nEstrutura global (comparação dos conjuntos de ligações):")
    print(f"  |E(G1) AND E(G2)| = {global_['inter']}")
    print(f"  |E(G1) OR  E(G2)| = {global_['uniao']}")
    print(f"  Jaccard  = {global_['jaccard']:.4f} ({_pct(global_['jaccard'])})")
    print(f"  Cosseno  = {global_['cosseno']:.4f} ({_pct(global_['cosseno'])})")
    print(f"  Overlap  = {global_['overlap']:.4f} ({_pct(global_['overlap'])})")

    print("\nSimilaridade local por vértice homólogo (Adj em G1 vs Adj em G2):")
    if not locais:
        print("  (nenhum vértice com mesmo nome em ambos os grafos para comparar)")
    else:
        for linha in locais:
            print(
                f"  {linha['vertice']:<8} "
                f"|Adj1|={linha['tam_a']:<3} |Adj2|={linha['tam_b']:<3} "
                f"inter={linha['inter']:<3} "
                f"J={_pct(linha['jaccard']).strip():>8} "
                f"C={_pct(linha['cosseno']).strip():>8} "
                f"O={_pct(linha['overlap']).strip():>8}"
            )
        print(
            f"  {'Média':<8} "
            f"J={_pct(medias['jaccard']).strip():>8} "
            f"C={_pct(medias['cosseno']).strip():>8} "
            f"O={_pct(medias['overlap']).strip():>8}"
        )


def desenhar_em_eixo(grafo, ax, titulo):
    G = nx.MultiDiGraph()
    for v in grafo.vertices:
        G.add_node(v.nome)

    n = len(G.nodes)
    if n <= 15:
        pos = nx.circular_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42, k=2.0)

    ax.set_title(titulo)
    tam_no = max(300, min(900, 9000 // max(1, n)))
    fonte = max(6, min(10, 120 // max(1, n)))

    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=tam_no, node_color="skyblue")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=fonte, font_weight="bold")

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
                    arrows=True, arrowstyle="->", arrowsize=12,
                    edge_color="red", connectionstyle=estilo,
                )
            else:
                nx.draw_networkx_edges(
                    G, pos, ax=ax, edgelist=[(origem, destino)],
                    arrowstyle="-", edge_color="blue", connectionstyle=estilo,
                )
        rotulos_pares[(par[0], par[1])] = "\n".join(textos_rotulos)

    if n <= 20:
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax, edge_labels=rotulos_pares,
            font_size=max(5, fonte - 1),
        )
    ax.axis("off")
    return pos


def mostrar_grafos_lado_a_lado(g1, g2):
    n1 = len(g1.vertices)
    n2 = len(g2.vertices)
    largura = max(12, min(20, (n1 + n2) * 0.7))
    altura = max(7, min(12, max(n1, n2) * 0.6))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(largura, altura))
    fig.suptitle("Resultado da Similaridade - Q10")
    desenhar_em_eixo(g1, ax1, f"G1 (|V|={n1}, |E|={len(g1.elos)})")
    desenhar_em_eixo(g2, ax2, f"G2 (|V|={n2}, |E|={len(g2.elos)})")
    plt.tight_layout()
    plt.show()


def montar_grafos_demonstracao():
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


def executar_questao_10(g1: Multigrafo, g2: Multigrafo, mostrar_grafico=True):
    global_ = similaridade_global(g1, g2)
    locais, medias, so_g1, so_g2 = similaridade_local_vertices(g1, g2)
    imprimir_resultados(g1, g2, global_, locais, medias, so_g1, so_g2)
    if mostrar_grafico:
        mostrar_grafos_lado_a_lado(g1, g2)
    return global_, locais, medias


if __name__ == "__main__":
    g1_demo, g2_demo = montar_grafos_demonstracao()
    executar_questao_10(g1_demo, g2_demo)
