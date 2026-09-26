import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from Multigrafo import Multigrafo


class VerificadorPlanaridade:
    def __init__(self, G: Multigrafo, nome="G"):
        self.G = G
        self.nome = nome

    def grafo_subjacente_simples(self):
        H = nx.Graph()
        lacos = 0
        multiplos_reduzidos = 0
        pares_vistos = set()

        for v in self.G.vertices:
            H.add_node(v.nome)

        for elo in self.G.elos:
            a, b = elo.vertice1.nome, elo.vertice2.nome
            if a == b:
                lacos += 1
                continue
            par = tuple(sorted((a, b)))
            if par in pares_vistos:
                multiplos_reduzidos += 1
                continue
            pares_vistos.add(par)
            H.add_edge(a, b)

        return H, lacos, multiplos_reduzidos

    def _tem_triangulo(self, H):
        if H.number_of_nodes() < 3:
            return False
        return sum(nx.triangles(H).values()) > 0

    def _classificar_kuratowski(self, K):
        if K is None or K.number_of_nodes() == 0:
            return "subgrafo proibido (Kuratowski) não identificado"

        graus = dict(K.degree())
        ramificacao = [n for n, d in graus.items() if d >= 3]
        deg_ram = sorted(graus[n] for n in ramificacao)

        if len(ramificacao) == 5 and all(d >= 4 for d in deg_ram):
            return "subdivisão de K5 (completo com 5 vértices)"
        if len(ramificacao) == 6 and all(d == 3 for d in deg_ram):
            return "subdivisão de K3,3 (bipartido completo 3+3)"
        if K.number_of_nodes() == 5 and K.number_of_edges() == 10:
            return "K5 (grafo completo com 5 vértices)"
        if K.number_of_nodes() == 6 and K.number_of_edges() == 9:
            return "K3,3 (bipartido completo 3+3)"
        return (
            f"subgrafo de Kuratowski com {K.number_of_nodes()} vértices e "
            f"{K.number_of_edges()} arestas"
        )

    def verificar(self):
        H, lacos, multiplos = self.grafo_subjacente_simples()
        n = H.number_of_nodes()
        m = H.number_of_edges()
        n_orig = len(self.G.vertices)
        m_orig = len(self.G.elos)
        conexo = nx.is_connected(H) if n > 0 else True
        tem_triangulo = self._tem_triangulo(H)

        euler_3n6 = None
        euler_2n4 = None
        violou_necessaria = False
        passos_euler = []

        if n < 3:
            passos_euler.append(f"|V| = {n} < 3: desigualdades 3|V|-6 e 2|V|-4 não se aplicam.")
        else:
            limite_3n6 = 3 * n - 6
            euler_3n6 = m <= limite_3n6
            passos_euler.append(
                f"|E| <= 3*|V| - 6  →  {m} <= {limite_3n6}  →  "
                f"{'OK' if euler_3n6 else 'VIOLADO (não planar)'}"
            )
            if not euler_3n6:
                violou_necessaria = True

            if not tem_triangulo:
                limite_2n4 = 2 * n - 4
                euler_2n4 = m <= limite_2n4
                passos_euler.append(
                    f"Sem triângulos: |E| <= 2*|V| - 4  →  "
                    f"{m} <= {limite_2n4}  →  {'OK' if euler_2n4 else 'VIOLADO (não planar)'}"
                )
                if not euler_2n4:
                    violou_necessaria = True
            else:
                passos_euler.append("Há triângulos; a condição 2*|V|-4 não é exigida.")

        is_planar, certificado = nx.check_planarity(H, counterexample=True)
        kuratowski = None
        embedding = None
        if is_planar:
            embedding = certificado
        else:
            kuratowski = certificado

        return {
            "nome": self.nome,
            "n_orig": n_orig,
            "m_orig": m_orig,
            "n": n,
            "m": m,
            "lacos": lacos,
            "multiplos": multiplos,
            "conexo": conexo,
            "tem_triangulo": tem_triangulo,
            "euler_3n6": euler_3n6,
            "euler_2n4": euler_2n4,
            "violou_necessaria": violou_necessaria,
            "passos_euler": passos_euler,
            "planar": is_planar,
            "embedding": embedding,
            "kuratowski": kuratowski,
            "H": H,
            "tipo_proibido": None if is_planar else self._classificar_kuratowski(kuratowski),
        }

    def imprimir(self, r):
        print("Questão 18 - Verificação de planaridade")
        print(f"Analisando {r['nome']}: {r['n_orig']} vértices e {r['m_orig']} elos (multigrafo misto original)")
        print(
            f"  Grafo subjacente simples: |V|={r['n']}, |E|={r['m']} "
            f"(laços removidos={r['lacos']}, elos múltiplos reduzidos={r['multiplos']})"
        )
        print(f"  Conexo: {'sim' if r['conexo'] else 'não'}")

        print("\nCondições necessárias (Euler / corolários):")
        for passo in r["passos_euler"]:
            print(f"  {passo}")
        if r["violou_necessaria"]:
            print("  → Viola condição necessária: não planar.")
        else:
            print("  → Condições necessárias OK (não garante planaridade).")

        print("\nTeorema de Kuratowski (nx.check_planarity):")
        if r["planar"]:
            print("  Não há subdivisão de K5 nem de K3,3.")
            print("  VEREDITO: O GRAFO É PLANAR")
        else:
            print(f"  Subgrafo obstrutor: {r['tipo_proibido']}")
            if r["kuratowski"] is not None:
                verts = ", ".join(sorted(r["kuratowski"].nodes(), key=str))
                print(f"  Vértices do certificado: {verts}")
            print("  VEREDITO: O GRAFO NÃO É PLANAR")

    def mostrar(self, r):
        H = r["H"]
        n = H.number_of_nodes()
        largura = max(9, min(16, n * 0.8))
        altura = max(7, min(12, n * 0.7))
        fig, ax = plt.subplots(figsize=(largura, altura))

        tam_no = max(400, min(1100, 12000 // max(1, n)))
        fonte = max(6, min(12, 150 // max(1, n)))

        if r["planar"]:
            try:
                pos = nx.planar_layout(H) if n > 0 else {}
            except Exception:
                pos = nx.spring_layout(H, seed=7, k=2.0) if n > 0 else {}
            ax.set_title(f"Resultado Q18 - {r['nome']}: PLANAR")
            nx.draw_networkx_nodes(H, pos, ax=ax, node_size=tam_no, node_color="lightgreen")
            nx.draw_networkx_edges(H, pos, ax=ax, edge_color="steelblue", width=1.5)
            nx.draw_networkx_labels(H, pos, ax=ax, font_size=fonte, font_weight="bold")
        else:
            pos = nx.spring_layout(H, seed=7, k=2.0) if n > 0 else {}
            ax.set_title(f"Resultado Q18 - {r['nome']}: NÃO PLANAR ({r['tipo_proibido']})")
            K = r["kuratowski"]
            verts_k = set(K.nodes()) if K is not None else set()
            arestas_k = set(tuple(sorted(e)) for e in K.edges()) if K is not None else set()

            demais = [n for n in H.nodes if n not in verts_k]
            if demais:
                nx.draw_networkx_nodes(H, pos, ax=ax, nodelist=demais, node_size=tam_no, node_color="lightgray")
            if verts_k:
                nx.draw_networkx_nodes(
                    H, pos, ax=ax, nodelist=list(verts_k), node_size=tam_no + 300, node_color="salmon",
                )

            outras = [e for e in H.edges if tuple(sorted(e)) not in arestas_k]
            nx.draw_networkx_edges(H, pos, ax=ax, edgelist=outras, edge_color="lightgray", width=1.0)
            if arestas_k:
                nx.draw_networkx_edges(
                    H, pos, ax=ax,
                    edgelist=[e for e in H.edges if tuple(sorted(e)) in arestas_k],
                    edge_color="crimson", width=2.4,
                )
            nx.draw_networkx_labels(H, pos, ax=ax, font_size=fonte, font_weight="bold")
            ax.legend(
                handles=[
                    Patch(facecolor="salmon", label="Vértices de Kuratowski"),
                    Patch(facecolor="crimson", label="Arestas do subgrafo obstrutor"),
                    Patch(facecolor="lightgray", label="Demais elementos"),
                ],
                loc="upper right",
                fontsize=max(6, fonte - 1),
            )

        ax.axis("off")
        fig.tight_layout()
        plt.show()


def montar_grafo_planar_grade():
    g = Multigrafo([], [])
    linhas, colunas = 3, 4
    for i in range(linhas):
        for j in range(colunas):
            g.adicionarVertice(f"V{i * colunas + j + 1}")

    eid = 1
    for i in range(linhas):
        for j in range(colunas):
            u = f"V{i * colunas + j + 1}"
            if j + 1 < colunas:
                v = f"V{i * colunas + j + 2}"
                g.adicionarElo(f"e{eid}", u, v, isOrientado=(eid % 5 == 0), peso=1)
                eid += 1
            if i + 1 < linhas:
                v = f"V{(i + 1) * colunas + j + 1}"
                g.adicionarElo(f"e{eid}", u, v, isOrientado=False, peso=1)
                eid += 1

    g.adicionarElo(f"e{eid}", "V1", "V2", isOrientado=True, peso=2)
    return g


def montar_grafo_nao_planar_k5():
    g = Multigrafo([], [])
    for i in range(1, 13):
        g.adicionarVertice(f"V{i}")

    eid = 1
    for a in range(1, 6):
        for b in range(a + 1, 6):
            g.adicionarElo(f"k{eid}", f"V{a}", f"V{b}", isOrientado=(eid % 4 == 0), peso=1)
            eid += 1

    for i in range(5, 12):
        g.adicionarElo(f"c{i}", f"V{i}", f"V{i + 1}", isOrientado=False, peso=1)
    return g


def executar_questao_18(grafo: Multigrafo, nome="grafo de entrada", mostrar_grafico=True):
    ver = VerificadorPlanaridade(grafo, nome=nome)
    resultado = ver.verificar()
    ver.imprimir(resultado)
    if mostrar_grafico:
        ver.mostrar(resultado)
    return resultado


if __name__ == "__main__":
    grafo_demonstracao = montar_grafo_planar_grade()
    executar_questao_18(grafo_demonstracao, nome="Exemplo - grade 3x4")
