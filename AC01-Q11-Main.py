from Multigrafo import Multigrafo, Vertice, Elo
from typing import List

# Definições usadas (material "Teoria dos Grafos - Conceitos Básicos", Prof.
# Marcos Negreiros):
#   Caminho Simples (pág. 29): "cadeia que não usa o mesmo arco/elo mais de
#   uma vez".
#   Loop ou Laço (pág. 31): "ligação que inicia e termina no mesmo vértice".
#   Ciclo ou Circuito (pág. 32): "sub-grafo que contém um caminho simples
#   onde os vértices iniciais e finais são os mesmos".
#   Cintura de G (pág. 39): "cardinalidade do menor ciclo em G".
#   Circunferência de G (pág. 39): "comprimento do maior ciclo de G".
#
# Ou seja: um ciclo é um caminho SIMPLES (não repete elo) fechado. Isso já
# cobre, sem precisar de nenhum caso especial:
#   - um laço sozinho -> ciclo de tamanho 1;
#   - DUAS arestas distintas entre o mesmo par de vértices (não-orientadas,
#     orientadas em sentidos opostos, ou uma de cada) -> ciclo de tamanho 2;
#   - ciclos maiores, encontrados pela DFS abaixo.
# IMPORTANTE: uma única aresta não-orientada, sozinha, entre dois vértices
# NÃO forma ciclo -- "ir e voltar" por ela reusaria o mesmo elo, o que viola
# a definição de caminho simples. Por isso EncontrarCiclos ignora "voltar
# pelo mesmo elo de onde veio": esse comportamento já é o correto, e não
# precisa (nem deve) receber nenhum ajuste extra para tratar esse caso como
# ciclo de tamanho 2.


def EncontrarCiclos(multigrafo) -> List[List[Elo]]:
    todos_ciclos = []

    def dfs(vertice_atual, caminho_vertices, caminho_elos, elo_anterior):
        caminho_vertices.append(vertice_atual)

        for elo in vertice_atual.elos:
            # Ignora o mesmo elo de onde veio (evita reusar o elo, exigido
            # pela definição de caminho simples -- pág. 29)
            if elo == elo_anterior:
                continue

            # Descobre o vizinho correto
            vizinho = None
            if elo.isOrientado:
                if elo.vertice1 == vertice_atual:
                    vizinho = elo.vertice2
            else:
                vizinho = elo.vertice2 if elo.vertice1 == vertice_atual else elo.vertice1

            if vizinho is None:
                continue

            # CASO 1: Encontrou um nó que JÁ ESTÁ no caminho atual -> Ciclo detectado!
            if vizinho in caminho_vertices:
                idx_inicio = caminho_vertices.index(vizinho)
                # Extrai apenas os elos que fazem parte desse ciclo
                ciclo_elos = caminho_elos[idx_inicio:] + [elo]

                # Evita adicionar ciclos duplicados
                if ciclo_elos not in todos_ciclos:
                    todos_ciclos.append(ciclo_elos)

            # CASO 2: Vizinho novo -> Avança na recursão
            elif vizinho not in caminho_vertices:
                dfs(vizinho, caminho_vertices, caminho_elos + [elo], elo)

        # Backtracking: remove o vértice ao retornar para permitir outras buscas
        caminho_vertices.pop()

    # Roda a busca partindo de cada vértice
    for v in multigrafo.vertices:
        dfs(v, [], [], None)

    # Um mesmo ciclo pode ser encontrado mais de uma vez (partindo de
    # vértices de partida diferentes, ou percorrido nos dois sentidos);
    # removemos essas duplicatas comparando o CONJUNTO de elos de cada
    # ciclo encontrado.
    ciclos_unicos = []
    chaves_vistas = set()
    for ciclo in todos_ciclos:
        chave = frozenset(id(elo) for elo in ciclo)
        if chave not in chaves_vistas:
            chaves_vistas.add(chave)
            ciclos_unicos.append(ciclo)

    return ciclos_unicos


def calcularCintura(multigrafo):
    # Cintura de G (pág. 39): cardinalidade (nº de elos) do MENOR ciclo do grafo
    ciclos = EncontrarCiclos(multigrafo)
    if not ciclos:
        return None  # grafo acíclico: cintura não definida (infinita)
    return min(len(c) for c in ciclos)


def calcularCircunferencia(multigrafo):
    # Circunferência de G (pág. 39): comprimento do MAIOR ciclo do grafo
    ciclos = EncontrarCiclos(multigrafo)
    if not ciclos:
        return None  # grafo acíclico: circunferência não definida
    return max(len(c) for c in ciclos)


# ---------------------------------------------------------------------
# Testando o identificador de ciclos, a cintura e a circunferência
# ---------------------------------------------------------------------
if __name__ == "__main__":
    g = Multigrafo([], [])

    for v in ["A", "B", "C", "D", "E", "F"]:
        g.adicionarVertice(v)

    # Ciclo orientado de tamanho 4: A -> B -> C -> D -> A
    g.adicionarElo("e1", "A", "B", isOrientado=True)
    g.adicionarElo("e2", "B", "C", isOrientado=True)
    g.adicionarElo("e3", "C", "D", isOrientado=True)
    g.adicionarElo("e4", "D", "A", isOrientado=True)

    # Ciclo de tamanho 2 genuíno entre E e F: DUAS arestas distintas que
    # permitem ir e voltar sem reusar o mesmo elo (uma não-orientada, uma
    # orientada no sentido de volta) -- diferente de uma única aresta
    # não-orientada sozinha, que NÃO forma ciclo (ver nota acima).
    g.adicionarElo("e5", "E", "F", isOrientado=False)
    g.adicionarElo("e6", "F", "E", isOrientado=True)

    # Liga o restante do grafo ao ciclo principal, sem criar novos ciclos
    g.adicionarElo("e7", "D", "E", isOrientado=True)

    print('=== Ciclos encontrados por EncontrarCiclos ===')
    ciclos = EncontrarCiclos(g)
    if not ciclos:
        print("Nenhum ciclo encontrado.")
    for i, ciclo in enumerate(ciclos, start=1):
        nomes = " -> ".join(elo.nome for elo in ciclo)
        print(f"  Ciclo {i} (tamanho {len(ciclo)}): {nomes}")

    cintura = calcularCintura(g)
    circunferencia = calcularCircunferencia(g)

    print(f"\nCintura de G: {cintura}")
    print(f"Circunferência de G: {circunferencia}")

    # Teste extra: um laço (pág. 31) é, por definição, um ciclo de tamanho 1.
    print("\n=== Teste extra: grafo só com um laço ===")
    g2 = Multigrafo([], [])
    g2.adicionarVertice("X")
    g2.adicionarElo("laco1", "X", "X", isOrientado=False)
    print("Ciclos:", [[e.nome for e in c] for c in EncontrarCiclos(g2)])
    print("Cintura:", calcularCintura(g2))
    print("Circunferência:", calcularCircunferencia(g2))

    # Teste extra: UMA única aresta não-orientada sozinha NÃO é um ciclo.
    print("\n=== Teste extra: uma única aresta não-orientada sozinha ===")
    g3 = Multigrafo([], [])
    g3.adicionarVertice("P")
    g3.adicionarVertice("Q")
    g3.adicionarElo("unica", "P", "Q", isOrientado=False)
    print("Ciclos:", EncontrarCiclos(g3))
    print("Cintura:", calcularCintura(g3), "(None = grafo acíclico, como esperado)")

    g.mostrarGrafo()
