from Multigrafo import Multigrafo 
# Criando a estrutura
g = Multigrafo([], [])

# Adicionando vértices
g.adicionarVertice("A")
g.adicionarVertice("B")
g.adicionarVertice("C")

# Adicionando elos (Misto + Multigrafo)
g.adicionarElo("e1", "A", "B", isOrientado=True, peso=5)   # Orientado (A -> B)
g.adicionarElo("e2", "A", "B", isOrientado=False, peso=2)  # Não-orientado entre A e B
g.adicionarElo("e3", "B", "C", isOrientado=True, peso=1)   # Orientado (B -> C)

# Exibindo a janela gráfica
g.mostrarGrafo()
