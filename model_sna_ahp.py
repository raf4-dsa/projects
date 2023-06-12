#Analytics for Pricing by raf4

#Library

import pandas as pd #manipulação de dataframes
import igraph as ig #manipuçlação de grafos (SNA)
import numpy as np #manipulações estatísitcas

# SNA - Gerando grafo a partir de um csv

df = pd.read_csv('input_rede.csv', sep = ";", header = 0, names = ["codproduto", "source", "target", "weight", "last_update"]) #importa o arquivo e nomeia as colunas
g = ig.Graph(directed=True) #gera um grafo nulo
vertices = list(set(df['source']) | set(df['target'])) #gera lista de nós
g.add_vertices(vertices) #adiciona lista de nós no grafo
df_tuples = df[["source", "target"]] #gera um objeto com apenas duas colunas do dataframe (fonte e destino da aresta do grafo)
tuples = [tuple(x) for x in df_tuples.values] #gera arestas com source e target
g.add_edges(tuples) #insere as arestas no grafo
g.es["weight"] = df["weight"] #insere atributos (pesos) nas arestas

# SNA - Calculando medidas no grafo

degree_in = g.degree(vertices, mode='in', loops=True) #calcula degree in para os nós
coeficiente_clustering = g.transitivity_local_undirected(vertices) #calcula coeficiente de clustering (cc) para os nós

# SNA - Montando matriz de decisão com as colunas concorrentes (str), relevancia (float) e competitividade (int)

matriz_decisao = {'concorrente':vertices, 'relevancia':coeficiente_clustering,'competitividade':degree_in } #gera uma matriz com 3 vetores finais
df_matriz_decisao = pd.DataFrame(matriz_decisao) #monta o dataframe com a matriz gerada
df_matriz_decisao['relevancia'] = 1 / df_matriz_decisao['relevancia'].astype(float) #muda a variável relevancia (cc) de str para float e inverte o CC
df_matriz_decisao['competitividade'] = df_matriz_decisao['competitividade'].astype(int) #muda a variável competitividade (degree in) de str para int

# AHP - Normalização dos critérios

soma_relevancia = np.sum(df_matriz_decisao['relevancia']) #soma da coluna relevencia
soma_competitividade = np.sum(df_matriz_decisao['competitividade']) #soma da coluna competitividade
relevancia_normalizada = ((df_matriz_decisao['relevancia'] / soma_relevancia))*100 #divisão do total da soma da coluna por cada linha da coluna relevancia
competitividade_normalizada = (df_matriz_decisao['competitividade'] / soma_competitividade)*100 #divisão do total da soma da coluna por cada linha da coluna relevancia

matriz_decisao_normalizada = {'concorrente':vertices,
                              'relevancia_normalizada':relevancia_normalizada,
                              'competitividade_normalizada':competitividade_normalizada} #montar matriz de decisão
df_matriz_decisao_normalizada = pd.DataFrame(matriz_decisao_normalizada) #gerar dataframe com a matriz de decisão

print(df_matriz_decisao_normalizada)

# AHP - Modelagem Gaussiana dos Critérios

media_relevancia = np.mean(df_matriz_decisao_normalizada['relevancia_normalizada']) #calcular media da coluna relevancia
media_competitividade = np.mean(df_matriz_decisao_normalizada['competitividade_normalizada']) #calcular media da coluna competitividade
desvio_padrao_relevancia = np.std(df_matriz_decisao_normalizada['relevancia_normalizada']) #calcular desvio padrão da coluna relevancia
desvio_padrao_competitividade = np.std(df_matriz_decisao_normalizada['competitividade_normalizada']) #calcular desvio padrão da coluna competitividade
fator_gaussiano_relevancia = np.divide(desvio_padrao_relevancia, media_relevancia) #calcular fator gaussiano da coluna relevancia
fator_gaussiano_competitividade = np.divide(desvio_padrao_competitividade, media_competitividade) #calcular fator gaussiano da coluna competitividade

criterios_ponderados = {'fator_gaussiano_relevancia':[fator_gaussiano_relevancia],
                        'fator_gaussiano_competitividade':[fator_gaussiano_competitividade]
}

df_criterios_ponderados = pd.DataFrame(criterios_ponderados)
print(df_criterios_ponderados)

# AHP - Ponderação dos valores de cada Critério

soma_criterios_gaussiano = np.sum(df_criterios_ponderados, axis = 1) # soma os dois fatores gaussianos (relevancia e competitividade)
fg_relevancia_normalizado =  df_criterios_ponderados.iloc[0,0] / soma_criterios_gaussiano # normalização o fator gaussiano da relevância
fg_competitividade_normalizado = df_criterios_ponderados.iloc[0,1] / soma_criterios_gaussiano #normalização do fator gaussiano da competitividade

df_matriz_decisao_normalizada['relevancia_normalizada'].fillna(0)
df_matriz_decisao_normalizada['competitividade_normalizada'].fillna(0)

df_matriz_decisao_normalizada['competitividade_normalizada'] = df_matriz_decisao_normalizada['competitividade_normalizada'] * fg_competitividade_normalizado


print(df_matriz_decisao_normalizada)

# AHP - Obtenção do ranking
ranking = np.sum(df_matriz_decisao_ponderada, axis = 1)

matriz_final = {'vertices':vertices,
            'ranking':ranking}
df_final = pd.DataFrame(matriz_final)
df_final_ordenado = df_final.sort_values(by='ranking', ascending=False)
top_20 = df_final_ordenado.head(20)
print(top_20)


