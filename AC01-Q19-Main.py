from Multigrafo import Multigrafo

# O material ("Teoria dos Grafos - Conceitos Básicos", Prof. Marcos
# Negreiros, págs. 91-93) define "Rotulação ou Busca Topológica" através do
# pseudocódigo Traverse/DFS:
#
#   DFS(G,v,rot)
#   begin
#      Se v de G é não visitado então
#       Marque v como visitado e atribua a ele um rótulo (pex. rot:=rot+1);
#       Se há um vértice adjacente de v não visitado então Traverse(G,adj(v),rot)
#      Tome um vértice v de G não visitado, Traverse(G,v,rot);
#   end;
#
# Ou seja, a "rotulação topológica" pedida é simplesmente a numeração
# sequencial (rot:=rot+1) atribuída a cada vértice no momento em que a DFS o
# VISITA (ordem de descoberta) -- e, pela própria última linha do
# pseudocódigo, a busca reinicia a partir de qualquer vértice ainda não
# visitado até cobrir todo o grafo, mesmo que ele seja desconexo. É
# exatamente isso que Multigrafo.dfsRotulacaoTopologica() implementa.

if __name__ == "__main__":
    g = Multigrafo([], [])

    # Grafo orientado representando pré-requisitos entre matérias,
    # construído como o multigrafo da questão 5
    materias = ["Calculo I", "Calculo II", "Algebra Linear", "Programacao I",
                "Programacao II", "Estruturas de Dados", "Algoritmos", "Grafos"]
    for m in materias:
        g.adicionarVertice(m)

    g.adicionarElo("e1", "Programacao I", "Programacao II", isOrientado=True)
    g.adicionarElo("e2", "Programacao II", "Estruturas de Dados", isOrientado=True)
    g.adicionarElo("e3", "Calculo I", "Calculo II", isOrientado=True)
    g.adicionarElo("e4", "Calculo I", "Algebra Linear", isOrientado=True)
    g.adicionarElo("e5", "Estruturas de Dados", "Algoritmos", isOrientado=True)
    g.adicionarElo("e6", "Algebra Linear", "Algoritmos", isOrientado=True)
    g.adicionarElo("e7", "Algoritmos", "Grafos", isOrientado=True)
    g.adicionarElo("e8", "Estruturas de Dados", "Grafos", isOrientado=True)

    print("=== Travessia DFS a partir de um único vértice (g.dfs) ===")
    visitados = g.dfs()
    print("  " + " -> ".join(v.nome for v in visitados))
    print("  (esta é a versão simples de origem única: numa DFS que só parte")
    print("   de um vértice, em um grafo orientado, pode não sobrar ninguém")
    print("   inalcançado de fora -- por isso o pseudocódigo do material reinicia")
    print("   a busca a partir de vértices não visitados, coberto abaixo)")

    print("\n=== Rotulação Topológica (Traverse/DFS, pág. 92-93) ===")
    rotulos = g.dfsRotulacaoTopologica()
    for vertice, rot in rotulos:
        print(f"  rot={rot}: {vertice.nome}")

    g.mostrarGrafo()
