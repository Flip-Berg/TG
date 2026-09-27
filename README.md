# Como executar os códigos (Multigrafo.py e AC01-QXX-Main.py)

Este guia assume que você **nunca** instalou Python nem usou uma IDE antes.
Vale para Windows, Mac ou Linux — cada parte diz o que muda em cada sistema.

Vamos fazer 3 coisas, nesta ordem:
1. Instalar o Python
2. Colocar os arquivos numa pasta e instalar duas bibliotecas
3. Rodar os arquivos

---

## 1. Instalar o Python

### Windows
1. Acesse **https://www.python.org/downloads/** e clique no botão grande de
   download (ele já detecta que você está no Windows).
2. Abra o instalador baixado.
3. **MUITO IMPORTANTE:** na primeira tela do instalador, marque a caixinha
   **"Add python.exe to PATH"** (fica embaixo) antes de clicar em "Install Now".
   Se pular esse passo, os comandos abaixo não vão funcionar.
4. Aguarde terminar e feche o instalador.

### Mac
1. Acesse **https://www.python.org/downloads/** e baixe a versão para macOS.
2. Abra o arquivo `.pkg` baixado e siga o instalador (Continuar → Continuar →
   Instalar), como qualquer outro programa de Mac.

### Linux
A maioria das distribuições já vem com Python instalado. Para garantir,
abra o Terminal e rode:
```
sudo apt update && sudo apt install python3 python3-pip
```
(em distribuições baseadas em Debian/Ubuntu; em outras, use o gerenciador de
pacotes correspondente, como `dnf` ou `pacman`).

---

## 2. Preparar a pasta e instalar as bibliotecas

### 2.1. Crie uma pasta para os arquivos
Crie uma pasta em qualquer lugar (por exemplo, na Área de Trabalho) chamada
`grafos`, e coloque **todos** os arquivos `.py` que você recebeu dentro dela:
- `Multigrafo.py`
- `AC01-Q11-Main.py`
- `AC01-Q13-Main.py`
- `AC01-Q15-Main.py`
- `AC01-Q17-Main.py`
- `AC01-Q19-Main.py`

Todos precisam estar **na mesma pasta**, porque os arquivos `AC01-QXX-Main.py`
usam o `Multigrafo.py` como base.

### 2.2. Abra um terminal dentro dessa pasta

- **Windows:** abra a pasta no Explorador de Arquivos, clique na barra de
  endereço no topo (onde mostra o caminho da pasta), apague o texto, digite
  `cmd` e aperte Enter. Um terminal preto vai abrir já dentro da pasta.
- **Mac:** abra o Finder, vá até a pasta, clique com o botão direito nela
  (ou Ctrl+clique) e escolha **"Novos Termos na Pasta"** (ou abra o app
  **Terminal** e digite `cd ` seguido de arrastar a pasta para dentro da
  janela do Terminal, e aperte Enter).
- **Linux:** abra o gerenciador de arquivos, clique com o botão direito
  dentro da pasta e procure a opção **"Abrir no Terminal"** (o nome exato
  varia conforme a distribuição).

### 2.3. Instale as duas bibliotecas necessárias
Os códigos usam duas bibliotecas externas para desenhar os grafos:
`networkx` e `matplotlib`. Com o terminal aberto dentro da pasta, digite:

```
pip install networkx matplotlib
```

e aperte Enter. Espere a instalação terminar (pode demorar um minuto).

> Se aparecer o erro `pip: comando não encontrado` (mais comum no Mac/Linux),
> tente `pip3 install networkx matplotlib` no lugar.

---

## 3. Rodar os arquivos

Ainda no mesmo terminal (dentro da pasta), digite o nome do arquivo que você
quer rodar, precedido de `python` (ou `python3`). Por exemplo, para rodar a
questão 11:

```
python AC01-Q11-Main.py
```

> Se der erro de comando não encontrado, tente `python3` no lugar de
> `python`:
> ```
> python3 AC01-Q11-Main.py
> ```

O terminal vai mostrar o resultado (números, listas, etc.) como texto, e
depois vai abrir **uma janela gráfica** com o desenho do grafo. Para rodar
outro arquivo, primeiro **feche essa janela gráfica** (o programa fica
"pausado" enquanto ela estiver aberta) e só depois digite o próximo comando.

Para rodar as outras questões, troque só o nome do arquivo:

```
python AC01-Q13-Main.py
python AC01-Q15-Main.py
python AC01-Q17-Main.py
python AC01-Q19-Main.py
```

(O `AC01-Q17-Main.py` abre **duas** janelas gráficas, uma depois da outra: o
grafo original e o grafo já reduzido.)

---

## Problemas comuns

- **"python não é reconhecido..." (Windows):** o Python foi instalado sem
  marcar "Add python.exe to PATH". Desinstale, instale de novo e marque essa
  caixinha (passo 1).
- **"No module named 'networkx'" ou "No module named 'matplotlib'":** o
  passo 2.3 (instalar as bibliotecas) não foi feito, ou foi feito num
  terminal diferente do que você está usando agora. Rode `pip install
  networkx matplotlib` de novo.
- **Nada abre / trava:** verifique se uma janela gráfica de uma execução
  anterior ainda está aberta em segundo plano — feche-a.
- **Os arquivos `AC01-QXX-Main.py` dão erro dizendo que não encontram o
  `Multigrafo`:** os arquivos precisam estar todos dentro da mesma pasta.
