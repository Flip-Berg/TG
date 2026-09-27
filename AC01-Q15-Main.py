from Multigrafo import Multigrafo

# Definições usadas (material "Teoria dos Grafos - Conceitos Básicos", Prof.
# Marcos Negreiros, pág. 48):
#   "Corte em Arestas: Conjunto mínimo de arestas que ao removê-las torna o
#   Grafo em 2 componentes conexas;"
#   "Corte Fundamental: é a remoção de uma aresta de um subgrafo árvore T de
#   um grafo G."
# Ou seja: parte-se de uma árvore geradora T de G; para CADA aresta de T,
# removê-la de T divide a árvore em duas partes (dois conjuntos de
# vértices); o corte fundamental associado a essa aresta é o conjunto de
# TODAS as arestas de G (da árvore ou não) que ligam essas duas partes --
# exatamente o "Corte em Arestas" entre elas.


def cortesFundamentais(multigrafo):
    '''
    Para cada elo de uma árvore geradora de G, calcula o Corte Fundamental
    associado (pág. 48): ao remover esse elo da árvore, ela se divide em
    duas partes (dois conjuntos de vértices); o corte fundamental é o
    conjunto de TODOS os elos de G (da árvore ou não) que ficam com uma
    ponta em cada uma dessas duas partes.

    Retorna uma lista de tuplas (eloDaArvore, listaDeElosDoCorte).
    '''
    elosArvore, _ = multigrafo.arvoreGeradora()

    resultado = []
    for eloRemovido in elosArvore:
        elosArvoreSemEste = [e for e in elosArvore if e != eloRemovido]
        componentes = multigrafo.componentesComElos(elosArvoreSemEste)

        if len(componentes) < 2:
            # não deveria acontecer para um elo que pertence à árvore
            continue

        lado1 = set(componentes[0])
        lado2 = set(v for comp in componentes[1:] for v in comp)

        elosDoCorte = [
            elo for elo in multigrafo.elos
            if (elo.vertice1 in lado1 and elo.vertice2 in lado2)
            or (elo.vertice1 in lado2 and elo.vertice2 in lado1)
        ]
        resultado.append((eloRemovido, elosDoCorte))

    return resultado


# ---------------------------------------------------------------------
# Testando o Corte Fundamental de G
# ---------------------------------------------------------------------
if __name__ == "__main__":
    g = Multigrafo([], [])

    for nome in ["A", "B", "C", "D", "E"]:
        g.adicionarVertice(nome)

    # Elos que a busca em largura vai escolher para a árvore geradora
    g.adicionarElo("e1", "A", "B", isOrientado=False)
    g.adicionarElo("e2", "B", "C", isOrientado=False)
    g.adicionarElo("e3", "C", "D", isOrientado=False)
    g.adicionarElo("e4", "D", "E", isOrientado=False)

    # Elos extras (fora da árvore), que aparecerão nos cortes fundamentais
    g.adicionarElo("e5", "A", "C", isOrientado=False)
    g.adicionarElo("e6", "B", "E", isOrientado=False)

    elosArvore, elosRestantes = g.arvoreGeradora()
    print("=== Árvore Geradora de G ===")
    print("  Elos da árvore:", [e.nome for e in elosArvore])
    print("  Elos fora da árvore:", [e.nome for e in elosRestantes])

    cortes = cortesFundamentais(g)

    print("\n=== Cortes Fundamentais de G ===")
    for eloArvore, corte in cortes:
        nomesCorte = ", ".join(e.nome for e in corte)
        print(f"  Removendo '{eloArvore.nome}' da árvore -> Corte Fundamental: {{{nomesCorte}}}")

    g.mostrarGrafo()
