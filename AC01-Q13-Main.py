from Multigrafo import Multigrafo
import math

# Definições usadas (material "Teoria dos Grafos - Conceitos Básicos", Prof.
# Marcos Negreiros, pág. 45):
#   "Excentricidade de v em V, Ex(v): É o tamanho do maior caminho elementar
#   entre v e w, tal que w em V-{v}"
#   "Raio de G - Rad(G): é o valor mínimo de Ex(v), para todo v em V;"
#   "Diâmetro de G - Diam(G): é o valor máximo de Ex(v), para todo v em V;"
#   "Centro de G - Centro(G): É o conjunto de vértices de excentricidade
#   mínima."
# Ex(v) é o MAIOR entre os caminhos MÍNIMOS (mais curtos) de v até cada
# outro vértice w -- daí usarmos calcularDistancias (Dijkstra, em
# Multigrafo.py) para achar a distância de v a cada w, e então tomar o maior
# valor entre elas.


def calcularExcentricidade(multigrafo, vertice):
    '''
    Ex(v) (pág. 45): maior distância (caminho mínimo) entre 'vertice' e
    qualquer outro vértice alcançável do multigrafo.
    '''
    distancias = multigrafo.calcularDistancias(vertice)
    distanciasFinitas = [d for v, d in distancias.items() if v != vertice and d != math.inf]

    if not distanciasFinitas:
        return math.inf  # não alcança nenhum outro vértice

    return max(distanciasFinitas)


def calcularRaioDiametroCentro(multigrafo):
    '''
    Rad(G): menor excentricidade dentre os vértices de G.
    Diam(G): maior excentricidade dentre os vértices de G.
    Centro(G): conjunto de vértices de excentricidade mínima (== Rad(G)).
    '''
    excentricidades = {v: calcularExcentricidade(multigrafo, v) for v in multigrafo.vertices}
    finitas = {v: e for v, e in excentricidades.items() if e != math.inf}

    if not finitas:
        return None, None, [], excentricidades

    raio = min(finitas.values())
    diametro = max(finitas.values())
    centro = [v for v, e in finitas.items() if e == raio]

    return raio, diametro, centro, excentricidades


# ---------------------------------------------------------------------
# Testando Raio, Diâmetro e Centro
# ---------------------------------------------------------------------
if __name__ == "__main__":
    g = Multigrafo([], [])

    for nome in ["A", "B", "C", "D", "E"]:
        g.adicionarVertice(nome)

    # Grafo não-orientado (para que raio/diâmetro sejam simétricos e mais
    # fáceis de interpretar): um ciclo B-C-D-E-B com A pendurado em B
    g.adicionarElo("e1", "A", "B", isOrientado=False, peso=1)
    g.adicionarElo("e2", "B", "C", isOrientado=False, peso=1)
    g.adicionarElo("e3", "C", "D", isOrientado=False, peso=1)
    g.adicionarElo("e4", "D", "E", isOrientado=False, peso=1)
    g.adicionarElo("e5", "B", "E", isOrientado=False, peso=1)

    raio, diametro, centro, excentricidades = calcularRaioDiametroCentro(g)

    print("=== Excentricidades ===")
    for v, e in excentricidades.items():
        print(f"  {v.nome}: {e}")

    print(f"\nRaio de G: {raio}")
    print(f"Diâmetro de G: {diametro}")
    print("Centro de G:", ", ".join(v.nome for v in centro))

    g.mostrarGrafo()
