import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import isomorphism as nxiso

from Multigrafo import Multigrafo


def clonar_simetrico(g: Multigrafo) -> Multigrafo:
    h = Multigrafo([], [])
    for v in g.vertices:
        h.adicionarVertice(v.nome)
    for elo in g.elos:
        h.adicionarElo(
            elo.nome,
            elo.vertice1.nome,
            elo.vertice2.nome,
            isOrientado=False,
            peso=elo.peso,
        )
    return h


def para_nx(g: Multigrafo) -> nx.Graph:
    H = nx.Graph()
    for v in g.vertices:
        H.add_node(v.nome)
    for elo in g.elos:
        a, b = elo.vertice1.nome, elo.vertice2.nome
        if a != b:
            H.add_edge(a, b)
    return H


def eh_simetrico(g: Multigrafo) -> bool:
    return all(not elo.isOrientado for elo in g.elos)


def verificar_isomorfismo(g1: Multigrafo, g2: Multigrafo):
    H1, H2 = para_nx(g1), para_nx(g2)
    if H1.number_of_nodes() != H2.number_of_nodes():
        return False, None
    matcher = nxiso.GraphMatcher(H1, H2)
    if not matcher.is_isomorphic():
        return False, None
    return True, dict(matcher.mapping)


class ContratorMaximo:
    def _proximo_elo(self, g: Multigrafo):
        for elo in g.elos:
            if elo.vertice1.nome != elo.vertice2.nome:
                return elo
        return None

    def contrair_maximo(self, g: Multigrafo):
        h = clonar_simetrico(g)
        conteudo = {v.nome: [v.nome] for v in h.vertices}
        historico = []
        seq = 1
        eid = 1

        while True:
            elo = self._proximo_elo(h)
            if elo is None:
                break

            u, v = elo.vertice1.nome, elo.vertice2.nome
            super_nome = f"S{seq}"
            seq += 1
            fundidos = sorted(set(conteudo[u] + conteudo[v]))

            novas = []
            for e in h.elos:
                if e is elo:
                    continue
                n1, n2 = e.vertice1.nome, e.vertice2.nome
                if n1 not in (u, v) and n2 not in (u, v):
                    continue
                a = super_nome if n1 in (u, v) else n1
                b = super_nome if n2 in (u, v) else n2
                if a == b:
                    continue
                novas.append((a, b, e.peso))

            h.adicionarVertice(super_nome)
            for a, b, peso in novas:
                h.adicionarElo(f"c{eid}", a, b, isOrientado=False, peso=peso)
                eid += 1

            h.removerVertice(u)
            if u != v:
                h.removerVertice(v)

            conteudo[super_nome] = fundidos
            conteudo.pop(u, None)
            conteudo.pop(v, None)

            historico.append({
                "passo": len(historico) + 1,
                "elo": elo.nome,
                "u": u,
                "v": v,
                "super": super_nome,
                "origens": fundidos,
                "n": len(h.vertices),
                "m": len(h.elos),
            })

        return h, historico, conteudo


def construir_grafo_simetrico_base():
    g = Multigrafo([], [])
    n_ciclo = 11
    for i in range(1, n_ciclo + 2):
        g.adicionarVertice(f"V{i}")

    hub = f"V{n_ciclo + 1}"
    eid = 1
    for i in range(1, n_ciclo + 1):
        j = i + 1 if i < n_ciclo else 1
        g.adicionarElo(f"e{eid}", f"V{i}", f"V{j}", isOrientado=False, peso=1)
        eid += 1
        g.adicionarElo(f"e{eid}", hub, f"V{i}", isOrientado=False, peso=1)
        eid += 1
    return g


def construir_g2_isomorfo(g1: Multigrafo):
    nomes = [v.nome for v in g1.vertices]
    n = len(nomes)

    bijecao = {}
    for idx, nome in enumerate(nomes):
        novo_idx = (idx + 5) % n
        bijecao[nome] = f"W{novo_idx + 1}"

    g2 = Multigrafo([], [])
    for nome in nomes:
        g2.adicionarVertice(bijecao[nome])
    for elo in g1.elos:
        g2.adicionarElo(
            f"{elo.nome}_",
            bijecao[elo.vertice1.nome],
            bijecao[elo.vertice2.nome],
            isOrientado=False,
            peso=elo.peso,
        )
    return g2, bijecao


def imprimir_estrutura(titulo, g):
    print(f"{titulo}: |V| = {len(g.vertices)}  |E| = {len(g.elos)}  "
          f"simétrico = {'sim' if eh_simetrico(g) else 'não'}")


def imprimir_historico(nome, historico, final):
    print(f"\nHistórico de contração máxima de {nome}")
    print(f"  {'Passo':<5} {'Elo':<6} {'fusão':<22} {'super':<6} {'|V|':>4} {'|E|':>4}")
    for h in historico:
        fusao = f"{h['u']} + {h['v']}"
        print(f"  {h['passo']:<5} {h['elo']:<6} {fusao:<22} {h['super']:<6} {h['n']:>4} {h['m']:>4}")
    print(f"  Núcleo final: |V| = {len(final.vertices)}, |E| = {len(final.elos)}")
    if final.vertices:
        restantes = ", ".join(v.nome for v in final.vertices)
        print(f"  Vértice(s) restante(s): {restantes}")


def desenhar_em_eixo(g, ax, titulo, pos=None):
    H = para_nx(g)
    n = H.number_of_nodes()
    if pos is None:
        if n <= 1:
            pos = {n: (0.0, 0.0) for n in H.nodes}
        elif n <= 15:
            pos = nx.circular_layout(H)
        else:
            pos = nx.spring_layout(H, seed=42, k=2.5)

    ax.set_title(titulo)
    if n == 0:
        ax.text(0.5, 0.5, "(grafo vazio)", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return pos

    tam_no = max(300, min(900, 8000 // max(1, n)))
    fonte = max(6, min(11, 120 // max(1, n)))
    nx.draw_networkx_nodes(H, pos, ax=ax, node_size=tam_no, node_color="skyblue")
    nx.draw_networkx_edges(H, pos, ax=ax, edge_color="steelblue", width=1.3)
    nx.draw_networkx_labels(H, pos, ax=ax, font_size=fonte, font_weight="bold")
    ax.axis("off")
    return pos


def mostrar_subplots(g1, g2, c1, c2):
    n_max = max(len(g1.vertices), len(g2.vertices), 1)
    largura = max(12, min(18, n_max * 0.9))
    altura = max(9, min(13, n_max * 0.7))

    fig, axes = plt.subplots(2, 2, figsize=(largura, altura))
    fig.suptitle("Resultado da Q16 - Grafos e Contração Máxima")
    desenhar_em_eixo(g1, axes[0, 0], f"G1 (|V|={len(g1.vertices)}, |E|={len(g1.elos)})")
    desenhar_em_eixo(g2, axes[0, 1], f"G2 (|V|={len(g2.vertices)}, |E|={len(g2.elos)})")
    desenhar_em_eixo(c1, axes[1, 0], f"G1 contraído (|V|={len(c1.vertices)})")
    desenhar_em_eixo(c2, axes[1, 1], f"G2 contraído (|V|={len(c2.vertices)})")
    plt.tight_layout()
    plt.show()


def executar_questao_16(g1: Multigrafo, g2: Multigrafo, mostrar_grafico=True):
    print("Questão 16 - Isomorfismo e contração máxima de elos")
    imprimir_estrutura("G1", g1)
    imprimir_estrutura("G2", g2)

    iso_ini, mapeamento = verificar_isomorfismo(g1, g2)
    print(f"\nIsomorfismo (grafo subjacente simples): G1 ~ G2 = {'SIM' if iso_ini else 'NÃO'}")
    if mapeamento:
        print("Um mapeamento bijetor encontrado:")
        for a in sorted(mapeamento, key=lambda x: (len(str(x)), str(x))):
            print(f"  {a} -> {mapeamento[a]}")

    contrator = ContratorMaximo()
    print("\nExecutando contração máxima (funde elos até restar K1 ou laços)...")
    c1, hist1, _ = contrator.contrair_maximo(g1)
    c2, hist2, _ = contrator.contrair_maximo(g2)
    imprimir_historico("G1", hist1, c1)
    imprimir_historico("G2", hist2, c2)

    iso_fim, _ = verificar_isomorfismo(c1, c2)
    k1_1 = len(c1.vertices) == 1 and len(c1.elos) == 0
    k1_2 = len(c2.vertices) == 1 and len(c2.elos) == 0

    print("\nConclusão da contração máxima:")
    print(f"  G1 contraído é K1: {'sim' if k1_1 else 'não'}")
    print(f"  G2 contraído é K1: {'sim' if k1_2 else 'não'}")
    print(f"  G1_contraído ~ G2_contraído: {'SIM' if iso_fim else 'NÃO'}")
    if iso_ini:
        print("  Grafos originais são isomorfos (estruturalmente equivalentes).")

    if mostrar_grafico:
        mostrar_subplots(g1, g2, c1, c2)
    return (iso_ini, mapeamento), (c1, c2)


if __name__ == "__main__":
    g1_demo = construir_grafo_simetrico_base()
    g2_demo, _ = construir_g2_isomorfo(g1_demo)
    executar_questao_16(g1_demo, g2_demo)
