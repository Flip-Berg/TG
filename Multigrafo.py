from __future__ import annotations
from collections import defaultdict, deque
from typing import List
import math
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# Ligação = Elo = Aresta. Para esse progriama foi utilizado Elo
class Elo: 
    def __init__(self, nome, vertice1: Vertice, vertice2: Vertice, isOrientado, peso=1.0):
        self.nome=nome 
        self.vertice1=vertice1
        self.vertice2=vertice2
        self.isOrientado=isOrientado
        #se for orientado, ele sai de vertice1 e entra em vertice2
        self.peso=peso
        #não ponderado=todos os pesos iguais a 1

class Vertice:
    def __init__(self, nome, elos: List[Elo]):
        self.nome=nome
        self.elos=elos 

# os vertices da classe elo e os elos da classe vertice são ponteiros pros objetos originais, então mexer neles atraves dessas classes também mexe no multigrafo

class Multigrafo:
    def __init__(self, vertices: List[Vertice], elos: List[Elo]):
        '''
        vertices: vetor de strings, sendo cada string o nome dos vértices
        elos: vetor de objetos da classe Elo, que representam as arestas entre os vertices
        '''
        self.vertices=vertices
        self.elos=elos


    def buscarVertice(self, nomeVertice):
        for vertice in self.vertices:
            if vertice.nome == nomeVertice:
                return vertice
        return None 
 
    def buscarElo(self, nomeElo):
        for elo in self.elos:
            if elo.nome == nomeElo:
                return elo
        return None

    def adicionarVertice(self, nomeVertice):
        jaExiste = self.buscarVertice(nomeVertice)
        if jaExiste: 
            return 
        novoVertice = Vertice(nomeVertice, [])
        self.vertices.append(novoVertice)
                
    def adicionarElo(self, nomeElo, nomeVertice1, nomeVertice2, isOrientado, peso=1):
        '''
        considerando multigrafo misto, pode haver mais de um elo para o mesmo vértice e na mesma direção, então basta checar se os vértices existem antes de adicionar o elo
        '''
        vertice1 = self.buscarVertice(nomeVertice1)
        vertice2 = self.buscarVertice(nomeVertice2)

        if vertice1 and vertice2:
            novoElo = Elo(nomeElo, vertice1, vertice2, isOrientado, peso)
            self.elos.append(novoElo)
            vertice1.elos.append(novoElo)
            vertice2.elos.append(novoElo)

    def removerVertice(self, nomeVertice):
        vertice = self.buscarVertice(nomeVertice)
        if vertice is None:
            return

        # 1. Identifica todos os elos que encostam nesse vértice
        elosParaRemover = list(vertice.elos)

        # 2. Remove esses elos de TODOS os outros vértices do grafo
        for verticeAdjacente in self.vertices:
            verticeAdjacente.elos = [elo for elo in verticeAdjacente.elos if elo not in elosParaRemover]

        # 3. Remove esses elos da lista global do multigrafo
        self.elos = [elo for elo in self.elos if elo not in elosParaRemover]

        # 4. Remove o vértice da lista global
        self.vertices.remove(vertice)

    def removerElo(self, nomeElo):
        elo=self.buscarElo(nomeElo)
        if elo:
            elo.vertice1.elos.remove(elo)
            elo.vertice2.elos.remove(elo)
            self.elos.remove(elo)

    def alterarVertice(self, nomeAntigo, nomeNovo): 
        vertice=self.buscarVertice(nomeAntigo)
        if vertice:
            vertice.nome = nomeNovo

    def alterarElo(self, nomeAntigo, nomeNovo="", vertice1Novo=None, vertice2Novo=None, isOrientadoNovo=None, pesoNovo=0.0):
        elo = self.buscarElo(nomeAntigo)
        if not elo:
            return 
        if nomeNovo:
            elo.nome = nomeNovo 

        if vertice1Novo:
            elo.vertice1=vertice1Novo

        if vertice2Novo: 
            elo.vertice2=vertice2Novo

        if isOrientadoNovo:
            elo.isOrientado = isOrientadoNovo

        if pesoNovo:
            elo.peso = pesoNovo

    def destruirGrafo(self):
        #necessario remover todas as referencias a cada objeto ou o proprio objeto pra tirar eles da memória
        for vertice in self.vertices:
            vertice.elos.clear()

        self.vertices.clear()
        self.elos.clear()


    def mostrarGrafo(self):
        G = nx.MultiDiGraph()

        for v in self.vertices:
            G.add_node(v.nome)

        pos = nx.circular_layout(G)
        
        plt.figure(figsize=(9, 7))
        plt.title("Visualização do Multigrafo Misto")

        nx.draw_networkx_nodes(G, pos, node_size=800, node_color='skyblue')
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

        # Dicionário para agrupar as conexões entre cada par de vértices (independente de direção)
        # Chave: par ordenado ou não ordenado (v_min, v_max)
        # Valor: lista de objetos Elo entre esses dois vértices
        paresConexoes = defaultdict(list)
        for elo in self.elos:
            par = tuple(sorted([elo.vertice1.nome, elo.vertice2.nome]))
            paresConexoes[par].append(elo)

        # Rótulos agrupados por par de vértices para exibir e1, e2, etc. sem sobreposição
        rotulos_pares = {}

        # 1. Desenha cada elo aplicando curvaturas alternadas (-rad e +rad)
        for par, lista_elos in paresConexoes.items():
            qtd_elos = len(lista_elos)
            textos_rotulos = []

            for idx, elo in enumerate(lista_elos):
                origem = elo.vertice1.nome
                destino = elo.vertice2.nome
                textos_rotulos.append(f"{elo.nome} (p={elo.peso})")

                # Se houver apenas 1 elo entre os vértices, desenha reto (rad=0)
                # Se houver mais, alterna curvaturas positivas e negativas
                if qtd_elos == 1:
                    rad = 0.1 if elo.isOrientado else 0.0
                else:
                    # Passo de curvatura (ex: -0.25, +0.25, -0.5, +0.5...)
                    fator = (idx // 2 + 1) * 0.25
                    rad = fator if idx % 2 == 0 else -fator

                estilo_conexao = f"arc3,rad={rad}"

                if elo.isOrientado:
                    nx.draw_networkx_edges(
                        G, pos,
                        edgelist=[(origem, destino)],
                        arrows=True,
                        arrowstyle='->',
                        arrowsize=20,
                        edge_color='red',
                        connectionstyle=estilo_conexao
                    )
                else:
                    nx.draw_networkx_edges(
                        G, pos,
                        edgelist=[(origem, destino)],
                        arrowstyle='-',
                        edge_color='blue',
                        connectionstyle=estilo_conexao
                    )

            # Junta os textos de todos os elos do mesmo par em linhas separadas
            rotulos_pares[(par[0], par[1])] = "\n".join(textos_rotulos)

        # 2. Desenha os rótulos centralizados por par de vértices
        nx.draw_networkx_edge_labels(
            G, pos, 
            edge_labels=rotulos_pares, 
            font_color='black', 
            font_size=10
        )

        plt.axis('off')
        plt.show()

    # ------------------------------------------------------------------
    # Funções essenciais/gerais de análise de grafo, reaproveitadas por
    # mais de uma questão da lista (Q11, Q13, Q15, Q17, Q19...). Cada uma
    # traz entre parênteses a página do material ("Teoria dos Grafos -
    # Conceitos Básicos", Prof. Marcos Negreiros) de onde vem a definição.
    # ------------------------------------------------------------------

    def calcularDistancias(self, origem):
        '''
        Calcula, via algoritmo de Dijkstra, a menor distância (soma dos
        pesos) do vértice 'origem' até todos os demais vértices, respeitando
        a orientação dos elos: um elo orientado só pode ser percorrido de
        vertice1 para vertice2; um elo não-orientado pode ser percorrido nos
        dois sentidos. Assume pesos não-negativos.

        Retorna um dicionário {vertice: distancia}, com distancia = math.inf
        para vértices não alcançáveis a partir de 'origem'. Base da
        Excentricidade/Raio/Diâmetro/Centro (pág. 45), usada em Q12 e Q13.
        '''
        distancias = {v: math.inf for v in self.vertices}
        distancias[origem] = 0
        visitados = set()

        fila = [(0, id(origem), origem)]
        while fila:
            dist_atual, _, atual = heapq.heappop(fila)
            if atual in visitados:
                continue
            visitados.add(atual)

            for elo in atual.elos:
                vizinho = None
                if elo.isOrientado:
                    if elo.vertice1 == atual:
                        vizinho = elo.vertice2
                else:
                    vizinho = elo.vertice2 if elo.vertice1 == atual else elo.vertice1

                if vizinho is None or vizinho in visitados:
                    continue

                novaDist = dist_atual + elo.peso
                if novaDist < distancias[vizinho]:
                    distancias[vizinho] = novaDist
                    heapq.heappush(fila, (novaDist, id(vizinho), vizinho))

        return distancias

    def componentesComElos(self, elos):
        '''
        Calcula as componentes conexas do multigrafo considerando SOMENTE o
        subconjunto de elos fornecido (tratados como bidirecionais, ou seja,
        ignorando a orientação). Vértices sem nenhum elo do subconjunto
        formam sua própria componente (unitária).

        Útil para analisar subgrafos -- por exemplo, uma árvore geradora, ou
        a árvore após a remoção de um elo (Corte Fundamental, pág. 48, Q15).

        Retorna uma lista de componentes, cada uma uma lista de Vertice.
        '''
        adjacencia = defaultdict(list)
        for elo in elos:
            adjacencia[elo.vertice1].append(elo.vertice2)
            adjacencia[elo.vertice2].append(elo.vertice1)

        visitados = set()
        componentes = []
        for vertice in self.vertices:
            if vertice in visitados:
                continue
            componente = []
            pilha = [vertice]
            visitados.add(vertice)
            while pilha:
                atual = pilha.pop()
                componente.append(atual)
                for vizinho in adjacencia[atual]:
                    if vizinho not in visitados:
                        visitados.add(vizinho)
                        pilha.append(vizinho)
            componentes.append(componente)

        return componentes

    def componentesConexas(self, ignorarElos=None):
        '''
        Identifica as Componentes Conexas / s-Conexas (pág. 25-26): "É todo
        sub-grafo maximal conexo de um grafo", tratando toda ligação --
        orientada ou não -- como bidirecional. Se 'ignorarElos' for
        informado, esses elos são desconsiderados durante a busca (útil
        para testar o efeito da remoção de um elo -- Corte em Arestas,
        pág. 48).

        Retorna uma lista de componentes, cada uma uma lista de Vertice.
        '''
        ignorarElos = set(ignorarElos) if ignorarElos else set()
        elosConsiderados = [e for e in self.elos if e not in ignorarElos]
        return self.componentesComElos(elosConsiderados)

    def arvoreGeradora(self, origem=None):
        '''
        Constrói uma árvore (ou floresta, se o multigrafo não for conexo)
        geradora por busca em largura, tratando os elos como bidirecionais
        -- Árvore T(V,E), |E|=|V|-1 (pág. 33). Usada no Corte Fundamental
        (pág. 48, Q15): "é a remoção de uma aresta de um subgrafo árvore T
        de um grafo G".

        Retorna uma tupla (elosArvore, elosRestantes).
        '''
        if not self.vertices:
            return [], []

        ordemInicial = list(self.vertices)
        if origem is not None and origem in self.vertices:
            ordemInicial.remove(origem)
            ordemInicial.insert(0, origem)

        visitados = set()
        elosArvore = []

        for inicial in ordemInicial:
            if inicial in visitados:
                continue
            visitados.add(inicial)
            fila = deque([inicial])
            while fila:
                atual = fila.popleft()
                for elo in atual.elos:
                    vizinho = elo.vertice2 if elo.vertice1 == atual else elo.vertice1
                    if vizinho not in visitados:
                        visitados.add(vizinho)
                        elosArvore.append(elo)
                        fila.append(vizinho)

        elosArvoreSet = set(elosArvore)
        elosRestantes = [elo for elo in self.elos if elo not in elosArvoreSet]
        return elosArvore, elosRestantes

    def clonar(self):
        '''
        Retorna uma cópia independente do multigrafo (novos objetos de
        Vertice e Elo, mas com os mesmos nomes/atributos e a mesma
        estrutura de conexões). Útil antes de aplicar uma operação
        destrutiva, como contracaoMaxima.
        '''
        novoGrafo = Multigrafo([], [])
        for v in self.vertices:
            novoGrafo.adicionarVertice(v.nome)
        for elo in self.elos:
            novoGrafo.adicionarElo(elo.nome, elo.vertice1.nome, elo.vertice2.nome,
                                    isOrientado=elo.isOrientado, peso=elo.peso)
        return novoGrafo

    def fundirVertice(self, nomeVertice):
        '''
        "Fusão de Arestas" (material, pág. 84): "é uma operação que permite
        suprimir um vértice v de G, se d(v)>=2, eliminando-se as arestas que
        incidem sobre v, suprimindo-o, e criando novas arestas que ligam os
        vértices que se encontravam originalmente conectados ao vértice v
        eliminado." O exemplo do Grafo Minor (pág. 61 -- grafo de Petersen,
        3-regular, reduzido de 10 para 5 vértices) confirma que a operação
        vale para QUALQUER vértice de grau >= 2, não só grau 2 (num grafo
        3-regular não existe vértice de grau 2): os antigos vizinhos de v
        são ligados DOIS A DOIS, uma nova aresta não-orientada por par.

        Se o vértice tiver grau < 2, não há o que fundir e nada é feito.
        Modifica o multigrafo EM PLACE (use clonar() antes, se quiser
        preservar o grafo original).
        '''
        vertice = self.buscarVertice(nomeVertice)
        if vertice is None:
            return

        vizinhosExternos = []
        for elo in list(vertice.elos):
            if elo.vertice1 == vertice and elo.vertice2 == vertice:
                continue  # ignora laços no próprio vértice a ser eliminado
            vizinho = elo.vertice2 if elo.vertice1 == vertice else elo.vertice1
            vizinhosExternos.append((vizinho, elo.peso))

        if len(vizinhosExternos) < 2:
            return  # grau < 2: nada a fundir

        self.removerVertice(nomeVertice)

        contador = 0
        for i in range(len(vizinhosExternos)):
            for j in range(i + 1, len(vizinhosExternos)):
                viz_i, peso_i = vizinhosExternos[i]
                viz_j, peso_j = vizinhosExternos[j]
                contador += 1
                # peso da nova aresta = soma dos pesos das duas arestas fundidas
                # (equivalente a somar os comprimentos de um caminho em série)
                self.adicionarElo(f"fus_{nomeVertice}_{contador}", viz_i.nome, viz_j.nome,
                                   isOrientado=False, peso=peso_i + peso_j)

    def contracaoMaxima(self):
        '''
        Aplica repetidamente a Fusão de Arestas sobre vértices de grau
        EXATAMENTE 2 (o caso mais comum e mais bem-comportado da operação
        descrita na pág. 84 -- eliminar um nó de "passagem", ligando seus
        dois vizinhos diretamente), até que nenhum reste -- ou seja, até que
        a contração não possa mais avançar sem alterar a estrutura de
        ramificação do grafo (grafo reduzido / Grafo Minor, págs. 61 e 84).

        OBS: a definição da pág. 84 fala em d(v)>=2, e o exemplo do Grafo
        Minor (pág. 61) chega a fundir vértices de grau 3 (grafo de
        Petersen, 10->5 vértices). fundirVertice() já suporta isso para
        qualquer grau >=2. Mas aplicar ">=2" repetidamente até não sobrar
        NENHUM vértice com grau>=2 colapsa qualquer grafo com um ciclo (ou
        um vértice de grau>=3) até um único vértice cheio de laços -- ao
        fundir um vértice de grau d>=3, seus d vizinhos passam a formar uma
        "roda" (clique) entre si, o que cria novos ciclos e nunca pára. Por
        isso, para uma "contração máxima" que produza um grafo reduzido
        útil (o esqueleto de ramificações do grafo, sem os nós de simples
        passagem), esta função reduz apenas os vértices de grau exatamente
        2. Quem quiser reproduzir o exemplo do Grafo Minor (fundindo também
        vértices de grau >=3) pode chamar fundirVertice diretamente.
        '''
        def grauExterno(vertice):
            return sum(
                1 for elo in vertice.elos
                if not (elo.vertice1 == vertice and elo.vertice2 == vertice)
            )

        while True:
            candidatos = [v for v in self.vertices if grauExterno(v) == 2]
            if not candidatos:
                break
            self.fundirVertice(candidatos[0].nome)

    def dfsRotulacaoTopologica(self, origem=None):
        '''
        Implementa o pseudocódigo Traverse/DFS do material (págs. 92-93):
        percorre o multigrafo em profundidade, atribuindo a cada vértice um
        rótulo sequencial (rot:=rot+1) no momento em que é visitado; e,
        seguindo a própria instrução do pseudocódigo ("Tome um vértice de G
        não visitado, Traverse(G,v,rot)"), reinicia a busca a partir de
        qualquer vértice ainda não visitado até cobrir todo o multigrafo
        (mesmo que ele seja desconexo).

        Retorna uma lista de tuplas (vertice, rotulo), na ordem de visita.
        '''
        visitados = set()
        rotulos = []
        rot = [0]

        def visitar(vertice):
            visitados.add(vertice)
            rot[0] += 1
            rotulos.append((vertice, rot[0]))

            for elo in vertice.elos:
                vizinho = None
                if elo.isOrientado:
                    if elo.vertice1 == vertice:
                        vizinho = elo.vertice2
                else:
                    vizinho = elo.vertice2 if elo.vertice1 == vertice else elo.vertice1

                if vizinho is not None and vizinho not in visitados:
                    visitar(vizinho)

        ordemInicial = list(self.vertices)
        if origem is not None and origem in self.vertices:
            ordemInicial.remove(origem)
            ordemInicial.insert(0, origem)

        for vertice in ordemInicial:
            if vertice not in visitados:
                visitar(vertice)

        return rotulos

    def dfs(self, vertice_inicial=None, visitados=None):
        if visitados is None:
            visitados = []
            
        if vertice_inicial is None:
            if not self.vertices:
                return visitados
            vertice_inicial = self.vertices[0]
            
        visitados.append(vertice_inicial)
        
        for elo in vertice_inicial.elos:
            # Descobre o vizinho correto dependendo se o elo é orientado ou não
            vizinho = None
            if elo.isOrientado:
                if elo.vertice1 == vertice_inicial:
                    vizinho = elo.vertice2
            else:
                vizinho = elo.vertice2 if elo.vertice1 == vertice_inicial else elo.vertice1
                
            if vizinho and vizinho not in visitados:
                self.dfs(vertice_inicial=vizinho, visitados=visitados)
                
        return visitados
