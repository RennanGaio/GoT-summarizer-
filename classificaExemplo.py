import nltk

def melhoraListaFrases(listaFrasesRuim):
	listaFrasesBoa = []
	for frase in listaFrasesRuim:
		for fraseBoa in frase.split('\n'):
			if fraseBoa != '':
				if fraseBoa[-1] != '.':
					fraseBoa += '.'		#coloca ponto final onde estiver faltando
				listaFrasesBoa.append(fraseBoa)
	return listaFrasesBoa

def criaListaTags (listaFrasesBoa):
	#obtem os tokens, separados por frase
	tokensPorFrase = []
	for frase in listaFrasesBoa:
		tokensPorFrase.append(nltk.word_tokenize(frase))

	#gera uma lista com todos os tokens do texto
	tokensGeral = []
	for frase in tokensPorFrase:
		for token in frase:
			tokensGeral.append(token)

	#obtem a classificacao gramatica das palavras
	listaTagsRuim = nltk.pos_tag(tokensGeral)

	#gera uma lista de classificacoes mais facil de mexer
	listaTagsBoa = []
	for par in listaTagsRuim:
		listaTagsBoa.append([str(par[0]),str(par[1])])
	return listaTagsBoa



#abre o arquivo
#arquivo = open('base de dados concatenada.txt')
arquivoEntrada = open('exemplo.txt')

#le o arquivo
raw=arquivoEntrada.read()

#obtem o segmentador de sentencas
sent_tokenizer=nltk.data.load("tokenizers/punkt/english.pickle")

#separa as frases do texto
listaFrasesRuim = sent_tokenizer.tokenize(raw)

#melhora a lista de frases
listaFrasesBoa = melhoraListaFrases(listaFrasesRuim)

#cria a lista de duplas com classificacao das palavras
listaTagsBoa=criaListaTags(listaFrasesBoa)

print listaTagsBoa