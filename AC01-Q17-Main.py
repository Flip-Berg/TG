from Multigrafo import Multigrafo


# ---------------------------------------------------------------------
# Testando a Contração Máxima (Fusão de Arestas, material pág. 84) em um
# grafo com pelo menos 15 vértices
# ---------------------------------------------------------------------
#
# Estrutura escolhida: um vértice central "J" (junção) do qual partem 4
# "cadeias" (caminhos) de vértices de grau 2 até 4 vértices-folha
# (L1..L4). Isso soma 4 folhas + 1 junção + 4 cadeias de 3 vértices
# internos cada = 4 + 1 + 12 = 17 vértices (>= 15), e permite observar
# claramente o efeito da Fusão de Arestas: cada cadeia de vértices de
# grau 2 é "esticada" até virar uma única aresta ligando a folha
# diretamente à junção J.
if __name__ == "__main__":
    g = Multigrafo([], [])

    folhas = ["L1", "L2", "L3", "L4"]
    for folha in folhas:
        g.adicionarVertice(folha)
    g.adicionarVertice("J")

    contador_elo = 0
    for idx, folha in enumerate(folhas, start=1):
        cadeia = [folha] + [f"C{idx}_{k}" for k in range(1, 4)] + ["J"]
        for nomeInterno in cadeia[1:-1]:
            g.adicionarVertice(nomeInterno)
        for a, b in zip(cadeia, cadeia[1:]):
            contador_elo += 1
            g.adicionarElo(f"e{contador_elo}", a, b, isOrientado=False, peso=1)

    print(f"Grafo original: {len(g.vertices)} vértices, {len(g.elos)} elos")
    print("Graus:", {v.nome: len(v.elos) for v in g.vertices})

    gReduzido = g.clonar()
    gReduzido.contracaoMaxima()

    print(f"\nGrafo após a Contração Máxima: {len(gReduzido.vertices)} vértices, "
          f"{len(gReduzido.elos)} elos")
    print("Vértices restantes:", [v.nome for v in gReduzido.vertices])
    print("Elos resultantes:")
    for elo in gReduzido.elos:
        print(f"  {elo.nome}: {elo.vertice1.nome} -- {elo.vertice2.nome} (peso={elo.peso})")
    print("\n(cada cadeia de vértices de grau 2 entre uma folha e J foi fundida em uma")
    print(" única aresta; o peso da aresta resultante é a soma dos pesos da cadeia)")

    g.mostrarGrafo()
    gReduzido.mostrarGrafo()
