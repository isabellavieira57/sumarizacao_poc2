#!/usr/bin/python
# coding: utf-8

#-----------------------------------------------------------------------#
# Sumarização Automática de Relatórios de Bug							#
# Desenvolvido por Isabella Vieira Ferreira								#
# POC II - Ciência da Computação - UFSJ									#
#-----------------------------------------------------------------------#

#-----------------------------------------------------------------------#
# Estrutura de dados:													#
#      [[tokens_comentarios, referencia_explicita, like]]				#
# Onde:																	#
#	- tokens_comentarios = tokens do comentario							#
#	- referencia_explicita = index do comentario referenciado ou -1 se  #
# nao possui referencia													#
#	- like = 1 se possui like e 0 se nao possui like                    #
#-----------------------------------------------------------------------#

import numpy as np
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA
from scipy import spatial
np.seterr(divide='ignore', invalid='ignore')

#-----------------------------------------------------------------------#
# Coloca os tokens distintos dos dois comentarios a serem analisados em #
# uma lista						 										#
#-----------------------------------------------------------------------#
def getTokensDistintos (comentario1, comentario2):

	listaTokensDistintos = []

	# -2 para nao verificar a referencia explicita e o like
	for i in range(len(comentario1)-2):
		if comentario1[i] not in listaTokensDistintos:
			listaTokensDistintos.append(comentario1[i])
	
	for i in range(len(comentario2)-2):
		if comentario2[i] not in listaTokensDistintos:
			listaTokensDistintos.append(comentario2[i])

	return listaTokensDistintos

#-----------------------------------------------------------------------#
# Coloca os tokens distintos dos dois comentarios a serem analisados em #
# uma lista						 										#
#-----------------------------------------------------------------------#
def getTokensDistintosTitulo (comentario1, titulo):

	listaTokensDistintos = []

	# -2 para nao verificar a referencia explicita e o like
	for i in range(len(comentario1)-2):
		if comentario1[i] not in listaTokensDistintos:
			listaTokensDistintos.append(comentario1[i])

	for i in range(len(titulo)):
		if titulo[i] not in listaTokensDistintos:
			listaTokensDistintos.append(titulo[i])

	return listaTokensDistintos

#-----------------------------------------------------------------------#
# Calcula a frequencia de um termo em uma lista de tokens distintos 	#
#-----------------------------------------------------------------------#
def calculaFrequenciaSimilaridadeCosseno (comentario, listaTokensDistintos, indexComentario, matriztfxidf):

	frequenciaComentario = []

	for i in range(len(listaTokensDistintos)):
		if (listaTokensDistintos[i] in comentario):						# Se o token distinto esta no comentario
			index = comentario.index(listaTokensDistintos[i])
			frequenciaComentario.append(matriztfxidf[indexComentario][index])
		else:
			frequenciaComentario.append(0)

	return frequenciaComentario

#-----------------------------------------------------------------------#
# Calcula a frequencia de um termo em uma lista de tokens distintos 	#
#-----------------------------------------------------------------------#
def calculaFrequenciaSimilaridadeCossenoTitulo (titulo, listaTokensDistintos, indexComentario, matriztfxidfTitulo):

	frequenciaComentario = []

	for i in range(len(listaTokensDistintos)):
		if (listaTokensDistintos[i] in titulo):						# Se o token distinto esta no comentario
			index = titulo.index(listaTokensDistintos[i])
			frequenciaComentario.append(matriztfxidfTitulo[indexComentario][index])
		else:
			frequenciaComentario.append(0)

	return frequenciaComentario

#-----------------------------------------------------------------------#
# Conta quantas vezes o token aparece no documento						#
#-----------------------------------------------------------------------#
def frequenciaToken (token, comentariosPreProcessado):

	contador = 0

	for comentario in comentariosPreProcessado:
		contador = contador + comentario.count(token)

	return contador

#-----------------------------------------------------------------------#
# Numero de comentarios que tem o token 								#
#-----------------------------------------------------------------------#
def contaTokenDocumento (token, comentariosPreProcessado):

	count = 0

	for comentario in comentariosPreProcessado:
		if token in comentario:
			count = count + 1

	return count
#-----------------------------------------------------------------------#
# 						 												#
#-----------------------------------------------------------------------#
def tfxidf (token, i, j, comentariosPreProcessado, vetorIntermerdiario):

	totalComentariosTemToken = contaTokenDocumento(token,comentariosPreProcessado)
	frequenciaTokenDocumento = frequenciaToken(token,comentariosPreProcessado) 
	numeroComentarios = len(comentariosPreProcessado)

	if (totalComentariosTemToken != 0):
		resultadoTFXIDF = (frequenciaTokenDocumento * (np.log(numeroComentarios/totalComentariosTemToken)))
	else:
		resultadoTFXIDF = (frequenciaTokenDocumento * (np.log(numeroComentarios)))

	vetorIntermerdiario.append(resultadoTFXIDF)
	
	
#-----------------------------------------------------------------------#
# Normaliza numero colunas na matriz tfxidf								#
# Todas as linhas passam a ter o mesmo numero de colunas preenchidas com #
# 999																	#
#-----------------------------------------------------------------------#
def normalizaTFXIDF (matriztfxidf):
	
	# Encontra qual a maior dimensao da matriz
	maiorDimensao = 0
	for i in (range(len(matriztfxidf))):
		if (len(matriztfxidf[i]) > maiorDimensao):
			maiorDimensao = len(matriztfxidf[i])
			#maiorIndice = i
	
	maiorDimensao = maiorDimensao
	
	# Percorre a matriz toda e depois cada linha, concatenando ate atingir a maior dimensao
	for i in range(len(matriztfxidf)):
		j = len(matriztfxidf[i])
		quantidadeColunasFaltantes = maiorDimensao - len(matriztfxidf[i])
		for j in range(quantidadeColunasFaltantes):
			matriztfxidf[i].append(9999)		#TODO Arrumar! Alocar com 0.0 pode ser um problema
			
	#print len(matriztfxidf)

#-----------------------------------------------------------------------#
# spatial.distance.cosine calcula a distância e não a similaridade.     # 
# Para avaliar a similaridade, deve-se subtrair 1.                      #
#-----------------------------------------------------------------------#
def calculaSimilaridadeCosseno (matrizSimilaridadeCosseno, indexComentario1, indexComentario2, frequenciaComentario1, frequenciaComentario2):

	#print "frequencia comentario 1 ", frequenciaComentario1
	#print "frequencia comentario 2 ", frequenciaComentario2
	similaridade = 1 - spatial.distance.cosine(frequenciaComentario1, frequenciaComentario2)
	similaridadeTruncada = float(format(similaridade, ".1f"))	# 1 casa decimal depois da virgula
	#print "similaridade truncada ", similaridadeTruncada
	matrizSimilaridadeCosseno[indexComentario1][indexComentario2] = similaridadeTruncada
	matrizSimilaridadeCosseno[indexComentario2][indexComentario1] = similaridadeTruncada
	#matrizSimilaridadeCosseno[indexComentario1][indexComentario2] = similaridade
	#matrizSimilaridadeCosseno[indexComentario2][indexComentario1] = similaridade

#-----------------------------------------------------------------------#
# spatial.distance.cosine calcula a distância e não a similaridade.     # 
# Para avaliar a similaridade, deve-se subtrair 1.                      #
#-----------------------------------------------------------------------#
def calculaSimilaridadeCossenoTitulo (vetorSimilaridadeCossenoTitulo, indexComentario, frequenciaComentario1, frequenciaComentario2):

	similaridade = 1 - spatial.distance.cosine(frequenciaComentario1, frequenciaComentario2)
	similaridadeTruncada = float(format(similaridade, ".1f"))	# 1 casa decimal depois da virgula
	vetorSimilaridadeCossenoTitulo[indexComentario] = similaridadeTruncada
	#vetorSimilaridadeCossenoTitulo[indexComentario] = similaridade

#-----------------------------------------------------------------------------#
# average(cosine_similarities)+alpha*standard_deviation(cosine_similarities)  #
#-----------------------------------------------------------------------------#
"""def calculaThresholdSimilaridadeCosseno (matrizSimilaridadeCosseno):

	alpha = 0.75

	threshold = np.mean(matrizSimilaridadeCosseno) + alpha * np.std(matrizSimilaridadeCosseno)

	return threshold"""
	
#-----------------------------------------------------------------------------#
# 	    					 												  #
#-----------------------------------------------------------------------------#
"""def salvaMatrizSimilaridadeCosseno (matriz, tamanhoMatriz):

	arquivoGrafoPonderado = open("similaridadeCosseno.txt", 'wr+')
	
	for i in range(tamanhoMatriz):
		for j in range(i+1,tamanhoMatriz):
			arquivoGrafoPonderado.write("%d %d %0.1f\n" % (i,j,matriz[i][j]))
	
	for i in range(tamanhoMatriz):
		for j in range(tamanhoMatriz):
			arquivoGrafoPonderado.write("%d %d %0.1f\n" % (i,j,matriz[i][j]))
	
	
	arquivoGrafoPonderado.close()"""

#-----------------------------------------------------------------------------#
# 	    					 												  #
#-----------------------------------------------------------------------------#
def salvaMatrizSimilaridadeCossenoEsparsa (matriz, tamanhoMatriz):

	arquivoGrafoPonderado = open("grafo.txt", 'wr+')
	
	for i in range(tamanhoMatriz):
		for j in range(i+1,tamanhoMatriz):
			arquivoGrafoPonderado.write("%d %d %0.1f\n" % (i,j,matriz[i][j]))
				
	arquivoGrafoPonderado.close()
	
#-----------------------------------------------------------------------------#
# 	    					 												  #
#-----------------------------------------------------------------------------#
def fazCopiaMatrizSimilaridadeCosseno (matrizSimilaridadeCosseno, copiaMatrizSimilaridadeCosseno):

	for i in range(len(matrizSimilaridadeCosseno)):
		for j in range(len(matrizSimilaridadeCosseno)):
			copiaMatrizSimilaridadeCosseno[i][j] = matrizSimilaridadeCosseno[i][j]
			
#-----------------------------------------------------------------------------#
# 																			  #
#-----------------------------------------------------------------------------#
def calculaMediaSimilaridadeTituloDescricao (matrizSimilaridadeCosseno, vetorSimilaridadeCossenoTitulo):

	mediaDescricaoTitulo = []
	vetorParaMedia = []
	vetorIntermerdiario = []

	for i in range(len(matrizSimilaridadeCosseno)):
		vetorIntermerdiario.append(matrizSimilaridadeCosseno[0][i])
		vetorIntermerdiario.append(vetorSimilaridadeCossenoTitulo[i])
		vetorParaMedia.append(vetorIntermerdiario)
		vetorIntermerdiario = []

	for i in range(len(matrizSimilaridadeCosseno)):
		mediaDescricaoTitulo.append(np.mean(vetorParaMedia[i]))		# contem a media da similaridade do titulo e da descricao, o index do vetor mediaDescricaoTitulo é o ID do comentário

	return mediaDescricaoTitulo
	
#-----------------------------------------------------------------------------#
# Método de Fatorização de Matrizes: NMF									  #
# Matriz tfxidf nao tem like e referencia explicita
#-----------------------------------------------------------------------------#
def nmf (matriztfxidf):
	
	normalizaTFXIDF(matriztfxidf)
	
	model = NMF(n_components=2, init='random', random_state=0)
	model.fit(matriztfxidf) 
	
	"""print "\n\nCOMPONENTES"
	print model.components_
	print "\n\nMODEL RECONSTRUCTION"
	print model.reconstruction_err_ """

#-----------------------------------------------------------------------------#
# Método de Fatorização de Matrizes: PCA									  #
# Matriz tfxidf nao tem like e referencia explicita
#-----------------------------------------------------------------------------#
def pca (matriztfxidf):

	normalizaTFXIDF (matriztfxidf)
		
	pca = PCA(n_components=4)
	pca.fit(matriztfxidf)
	
	#pca.transform(matriztfxidf)
	
	print(pca.explained_variance_ratio_) 
	
	print(pca.get_covariance) 
