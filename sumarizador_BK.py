import nltk
#import sys
import re

##########################SUMARIO#############################################################################################
# listaTagsBoas - possui TODOS os tokens de elementos do texto, 															 #
#										eles possuem [0]: string do token 													 #
#										[1]: classificacao gramatical 														 #
#																															 #
# listaSemRepeticao - possui todas as entidades nomeadas sem repeticao, 													 #
#										eles possuem [0]: string do token 													 #
#										[1]: classificacao gramatical (ENOMEADA) 											 #
#										[2]: quantidade de vezes que ela aparece no texto 									 #
#										[3]: vetor de possivel classe de entidade 											 #
#										[3][0]: quantidade de vezes que eh referenciado como pessoa 						 #
#										[3][1]: quantidade de vezes que eh referenciado como organizacao 					 #
#										[3][2]: quantidade de vezes que eh referenciado como lugar							 #
#										[4]: classe de entidade final (caso algo estranho aconteca ele escrevera ERROR) 	 #
#																															 #
##############################################################################################################################


#reload(sys)
#sys.setdefaultencoding('cp860')

#somente para nomes de pessoas
#codigo 1 significa que o nome 1 engloba o nome 2, entao sobreescrevemos ele na lista
#codigo 2 significa que o nome 2 engloba o nome 1, entao nao precisamos alterar a lista
#codigo 3 significa que o nome 1 e igual ao nome 2, entao ele bota a palavra no final da lista de entidades sem repeticao 


#preciso normalizar as palavras, talvez melhore
def tiraEntidadesRepetidas(nome1, nome2):
	if (nome1[0]==nome2[0]):
		return 3
	elif nome1[0] in nome2[0]:
		return 2
	elif nome2[0] in nome1[0]:
		return 1
	return False

def melhoraListaFrases(listaFrasesRuim):
	listaFrasesBoa = []
	for frase in listaFrasesRuim:
		for fraseBoa in frase.split('\n'):
			if fraseBoa != '':
				#if fraseBoa[-1] != '.':
					#fraseBoa += '.'		#coloca ponto final onde estiver faltando
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

#gera o classificador de entidades, agora alem da posicao [0] possuir o nome, e a posicao [1] possuir sua classificacao sintatica
#aqueles que tiverem em [1] ENOMEADA, possuirao uma nova posicao [3,4,5] que indicara qual tipo de entidade e aquela, a pocicao [2] e a frequencia


def extraiTipoEntidade(listaTagsBoa, index):
	#crio essa string para ver se a palavra anterior pode ser composta, e entrar em umas das regras tambem
	composta=listaTagsBoa[index-2][0].lower()+' '+listaTagsBoa[index-1][0].lower()

	#pessoa
	if listaTagsBoa[index-1][0].lower() in pessoaInicio:
		return 0

	#organizacao
	elif (listaTagsBoa[index-1][0].lower() in familialist) or (composta in familialist) or listaTagsBoa[index][0].split(' ')[0].lower() in organizacaoInicio:
		return 1

	#lugar
	elif listaTagsBoa[index-1][0].lower() in prepLugarList or (composta in prepLugarList):
		return 2

	#o que sobrar eh pessoa
	return 0



def classificaEntidade(palavra):
	#palavra[4] sera a classe final dessa palavra

	maximo=max(palavra[3])
	index=0
	while (palavra[3][index]!=maximo):
		index+=1
	if index==0:
		palavra.append('pessoa')
	elif index==1:
		palavra.append('organizacao')
	elif index==2:
		palavra.append('lugar')
	else:
		palavra.append('ERROR')

def geraFraseRelevante(ListaSumarioTemp):
	Oracoes=[]
	FraseRelevante=[]

	for word in ListaSumarioTemp:
		if word[1] != ',' and word[1] != '.' and word[1] != 'PONTOFALA':
			Oracoes.append(word)
		else:
			Oracoes.append(word)
			result=retiraInformacoesIrrelevantes(Oracoes)
			if result==1:
				for palavra in Oracoes:
					FraseRelevante.append(palavra)
			Oracoes=[]

			if word[1]=='PONTOFALA':
				return FraseRelevante

	return FraseRelevante

def geraPontuacaoFrase(ListaSumarioTemp, listaSemRepeticao, titulo):

	FraseRelevante=geraFraseRelevante(ListaSumarioTemp)
	if FraseRelevante==[]:
		return 0
	else:
		cont=0
		#estou considerando que todas as preposicoes estarao se referindo a uma pessoa, logo ela tem a mesma importancia de uma entidade nomeada
		while cont < len(FraseRelevante):
			if FraseRelevante[cont][1]=='PRP' or FraseRelevante[cont][1]=='PRP$':
				FraseRelevante[cont][1]='REFERENCIA'
			cont+=1


		cont=0
		qtdAdj=0
		qtdVerbo=0
		seguintes=1
		listaVerbo=['VB','VBD','VBG','VBN','VBP', 'VBZ', 'RB']
		listaAdjetivo=['JJ', 'JJR', 'JJS']
		pontuacao=1.0
		pontuacaoFinal=1.0

		while cont < len(FraseRelevante):
			#favorece frases com muitas entidades, e se eles realizam acoes
			if FraseRelevante[cont][1]=='ENOMEADA' or FraseRelevante[cont][1]=='REFERENCIA':
				tipoEntidade=''
				pesoExtra=0.0

				#se a entidade for a que nomeia o capitulo ela tera um acrecimo no bonus, pois ela e mais importante naquele contexto
				if titulo.lower() in FraseRelevante[cont][0].lower():
					
					pesoExtra=0.3

				#se a entidade for um personagem frequente na historia toda (principal), ele ganhara um pequeno bonus
				for palavra in listaSemRepeticao:
					if FraseRelevante[cont][0] in palavra[0]:
						tipoEntidade=palavra[4]
						pesoExtra=pesoExtra + palavra[2]/1400  # dividi por 1400 pois a entidade que mais aparece no texto eh ned stark, com 657 aparicoes, e
						#essa divisao eh feita pois nao queremos que so frases que esse personagem aparece sejam selecionadas
				#isso favorecera entidades que nao sao pessoas, pois pessoas sao muito comuns no texto, entao pode-se estar dando muitos
				#pontos a algo que nao eh tao relevante

				if tipoEntidade=='pessoa' or FraseRelevante[cont][1]=='REFERENCIA':
					pontuacao=pontuacao*(1.3+pesoExtra)

				else:
					pontuacao=pontuacao*(1.7+pesoExtra)

				if FraseRelevante[cont+1][1] in listaVerbo:
					pontuacao=pontuacao*2
				cont+=1
				continue

			#favorece frases que possuam muitos verbos, tendem a ser mais importantes
			if FraseRelevante[cont][1] in listaVerbo and cont<len(FraseRelevante)-1 and (FraseRelevante[cont+1][1]=='REFERENCIA' or FraseRelevante[cont+1][1]=='ENOMEADA'):
				#qtdVerbo+=1
				pontuacao=pontuacao+0.5
				cont+=1
				continue

			#desfavorece frases que possuem muitos adjetivos, caracteristicas e comparacoes
			if FraseRelevante[cont][1] in listaAdjetivo:
				qtdAdj+=1
				cont+=1
				continue

			#se alguem referenciado faz uma acao essa deve ser contabilizada
			if FraseRelevante[cont][1]=='REFERENCIA' and (FraseRelevante[cont+1][1]=='NN' or FraseRelevante[cont+1][1]=='NNS'):
				if FraseRelevante[cont+2][1] in listaVerbo:
					pontuacao=pontuacao*2
				cont+=1
				continue

			#locucao de que alguem ou alguma coisa realizou alguma acao, logo se um dragao matou fulano, ou uma pedra caiu na cidade, isso sera
			#contabilizado aqui
			if FraseRelevante[cont][1]=='DT' and (FraseRelevante[cont+1][1]=='NN' or FraseRelevante[cont+1][1]=='NNS'):
				if FraseRelevante[cont+2][1] in listaVerbo:
					pontuacao=pontuacao*2
				cont+=1
				continue

			cont+=1


		#pontuacaoFinal=pontuacaoFinal+0.2*qtdVerbo
		pontuacaoFinal=pontuacaoFinal-0.1*qtdAdj
		pontuacaoFinal=pontuacaoFinal*pontuacao

		#se a frase tinha muita coisa irrelevante ela perde ponto
		#dif=(len(ListaSumarioTemp)-len(FraseRelevante))
		#if dif==0:
		#return pontuacaoFinal
		#else:
		#	return pontuacao/len(FraseRelevante)
		#pontuacao=10*pontuacao/len(ListaSumarioTemp)

		return pontuacaoFinal

def retiraInformacoesIrrelevantes(Oracoes):
	listaRelevante=['ENOMEADA', 'POS', 'PRP', 'VB','VBD','VBG','VBN','VBP', 'VBZ']
	
	for word in Oracoes:
		if word[1] in listaRelevante:
			return 1
	return 0

#todo titulo eh um nome de personagem e todo titulo possui todas as letras maiusculas
def identificaTitulo(cedula, tituloAnterior):
	titulo=cedula[0][1:len(cedula[0])]
	#fiz esse tamanho minimo para ele nao pegar nem um lixo, e como o menor nome de capitulo eh JON, nao teremos problema
	if titulo.upper()==titulo and len(titulo)>2:
		return cedula[0]
	else:
		return tituloAnterior


#abre o arquivo
#arquivo = open('base de dados concatenada.txt')
arquivoEntrada = open('exemplo2.txt')

#le o arquivo
raw=arquivoEntrada.read()

#obtem o segmentador de sentencas
sent_tokenizer=nltk.data.load("tokenizers/punkt/english.pickle")

#separa as frases do texto
listaFrasesRuim = sent_tokenizer.tokenize(raw)

#melhora a lista de frases
#listaFrasesBoa = melhoraListaFrases(listaFrasesRuim)
listaFrasesBoa = listaFrasesRuim

#cria a lista de duplas com classificacao das palavras
listaTagsBoa=criaListaTags(listaFrasesBoa)


#listas auxiliares para classificacao de entidades


listaSemRepeticao=[]
prepLugarList=['above', 'across', 'after', 'against', 'along', 'among',
			'around', 'at', 'behind', 'below', 'beside', 'between', 'beyond the',
			'close to', 'down', 'from', 'in front of',
			'inside', 'in', 'into', 'near', 'next to', 'off', 'on',
			'onto', 'opposite', 'out of', 'outside', 'over',
			'past', 'round', 'through', 'to', 'towards', 'under', 'up']
familialist=['of the', 'from the']
blacklist=['in','on','at', 'beyond', 'as', '[',']', 'and', 'are', 'for', 'from','while','with',
			'under', 'to', 'does','into','is','again','angrily',
			'was','then','that','during','tells','takes','calls',
			'back','if','before','through','by','about','atop', 'until', 'since']
organizacaoInicio = ['house','houses']
pessoaInicio = ['king', 'queen', 'prince', 'princess', 'lord', 'lady', 'ser', 'commander', 'Young']

listaVerbo=['VB','VBD','VBG','VBN','VBP', 'VBZ', 'RB']



#chama todos os substantivos proprios de entidade nomeada
cont=0
while cont < len(listaTagsBoa):
	if listaTagsBoa[cont][1]=='NNP' or listaTagsBoa[cont][1]=='NNPS':
		listaTagsBoa[cont][1]='ENOMEADA'

	#estou fazendo isso pois no final de cada frase de personagem temos ',' ao infez de um '.'
	elif listaTagsBoa[cont][1]==',':
		if (cont < (len(listaTagsBoa)-1)) and (listaTagsBoa[cont+1][1]=="''"): #essas aspas "''" aparecem como fecha aspas no formato pdf
			listaTagsBoa[cont][1]='PONTOFALA'
	cont+=1


tamanhoDoTexto=len(listaTagsBoa)
index=0


#separa todas as preposicoes indesejadas
for word in listaTagsBoa:
	if (word[0].lower() in blacklist) or (word[0].lower() in prepLugarList) or (word[0].lower() in familialist):
		word[1]='LNEGRA'
	if (word[0].lower() in pessoaInicio):
		word[1]='TITULO'


######################################################################################################################################
##debuger, serve para printar todos os tokens assim que eles sao classificados pelo tokenizer, e passados pelas alteracoes de listas
#
#for word in listaTagsBoa:
#	print word
#
#print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
########################acaba aqui####################################################################################################

####################################################
#		REGRAS DE JUNCAO DE ENTIDADES              #
####################################################
while (index-tamanhoDoTexto)<0:

	while listaTagsBoa[index][1]=='ENOMEADA':
		if listaTagsBoa[index+1][1]=='ENOMEADA':
			listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]
			listaTagsBoa.pop(index+1)
			tamanhoDoTexto-=1
			continue
		

		# optamos por remover os cardinais, pois eles erravam mais do que acertavam, estavam gerando muito lixo
		#
		#CARDINAIS
		#if listaTagsBoa[index+1][1]=='CD':
		#	listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]
		#	listaTagsBoa.pop(index+1)
		#	tamanhoDoTexto-=1
		#	continue
		#if listaTagsBoa[index-1][1]=='CD':
		#	listaTagsBoa[index][0]=listaTagsBoa[index-1][0]+' '+listaTagsBoa[index][0]
		#	listaTagsBoa.pop(index-1)
		#	tamanhoDoTexto-=1
		#	index-=1
		#	continue

		#PREPOSICAO
		if listaTagsBoa[index+1][1]=='IN' and listaTagsBoa[index+2][1]=='ENOMEADA':
			listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]+' '+listaTagsBoa[index+2][0]
			listaTagsBoa.pop(index+2)
			listaTagsBoa.pop(index+1)
			tamanhoDoTexto-=2
			continue
		if listaTagsBoa[index+1][1]=='IN' and listaTagsBoa[index+2][1]=='DT' and listaTagsBoa[index+3][1]=='ENOMEADA':
			listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]+' '+listaTagsBoa[index+2][0]+' '+listaTagsBoa[index+3][0]
			listaTagsBoa.pop(index+3)
			listaTagsBoa.pop(index+2)
			listaTagsBoa.pop(index+1)
			tamanhoDoTexto-=3
			continue

		#CASOS ESPECIAL 1 :ENOMEADA's ENOMEADA
		if listaTagsBoa[index+1][0]=="'s" and listaTagsBoa[index+2][1]=='ENOMEADA':
			listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]+' '+listaTagsBoa[index+2][0]
			listaTagsBoa.pop(index+2)
			listaTagsBoa.pop(index+1)
			tamanhoDoTexto-=2
		break



	#faz a juncao de todos os substantivos subsequentes para um bloco soh, para fazer a analise de sumarizacao
	while listaTagsBoa[index][1]=='NN' or listaTagsBoa[index][1]=='NNS':
		if listaTagsBoa[index+1][1]=='NN' or listaTagsBoa[index+1][1]=='NNS':
			listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]
			listaTagsBoa.pop(index+1)
			tamanhoDoTexto-=1
			continue
		if listaTagsBoa[index+1][1]=="POS" and (listaTagsBoa[index+2][1]=='NN' or listaTagsBoa[index+2][1]=='NNS'):
			listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]+' '+listaTagsBoa[index+2][0]
			listaTagsBoa.pop(index+2)
			listaTagsBoa.pop(index+1)
			tamanhoDoTexto-=2
		break
		

	#faz a juncao de verbos compostos, para contarem como um soh
	while listaTagsBoa[index][1] in listaVerbo:
		if listaTagsBoa[index+1][1] in listaVerbo:
			listaTagsBoa[index][0]=listaTagsBoa[index][0]+' '+listaTagsBoa[index+1][0]
			listaTagsBoa.pop(index+1)
			tamanhoDoTexto-=1
			continue
		break

	index+=1


retorno=[]


################################################################
#			REGRAS DE TIRAR ENTIDADES REPETIDAS 			   #
################################################################

tamanhoDoTexto=len(listaTagsBoa) #fazendo de novo so pra ter certeza
index=0

#comeca a gerar o tratamento das entidades

while index<tamanhoDoTexto:
	#############################################################################################################################
	#CONSIDERE NOS COMENTARIOS word=listaTagsBoa[index], essa word seria o token que estamos analizando no texto naquele momento#
	#############################################################################################################################

	stop=0       #essa chave servira apenas para incluir uma palavra pela 1 vez no vetor (ela nao apareceu antes)

	if listaTagsBoa[index][1]=='ENOMEADA':

		#estara percorendo a lista de tras para frente, pois assim o john sera referenciado ao ultimo jonh alguma coisa que apareceu antes dele
		#e nao ao primeiro john que apareceu na historia
		for palavra in listaSemRepeticao[::-1]:
			#gera os codigos para sabermos o que fazer com a palavra
			temp=palavra 				#estou fazendo isso para evitar bugs

			codigo=tiraEntidadesRepetidas(listaTagsBoa[index], palavra)

			###########################
			#SE WORD ENGLOBA A PALAVRA#
			###########################
			if (codigo==1):				
				palavra[0]=listaTagsBoa[index][0]		#substitui palavra por word na lista
				palavra[2]+=1							#incrementa a frequencia da palavra


				tipo=int(extraiTipoEntidade(listaTagsBoa, index)) #avalia o possivel tipo de entidade
				palavra[3][tipo]+=1 						 #incrementa o possivel tipo
				
				stop=1
				break

			#########################
			#SE PALAVRA ENGLOBA WORD#
			#########################
			elif (codigo==2):				
				#listaTagsBoa[index][0]=palavra[0]		#substitui ela no "texto", para depois fazermos as triplas de relacao
				palavra[2]+=1							#incrementa a frequencia da palavra

				tipo=int(extraiTipoEntidade(listaTagsBoa, index))
				palavra[3][tipo]+=1

				stop=1
				break

			####################
			#SE WORD == PALAVRA#
			####################
			elif (codigo==3):      
				listaSemRepeticao.remove(temp) 		#se a palavra for igual a word, eu quero botar ela no final da lista, para saber que o
				listaSemRepeticao.append(temp)		#proximo referencial a aquele nome sera o ultimo da lista
				temp[2]+=1				#incrementa a frequencia da palavra

				tipo=int(extraiTipoEntidade(listaTagsBoa, index))
				palavra[3][tipo]+=1
				
				stop=1
				break
		if stop==0:			#se nao houve repeticao
			# ESSA SERA A FREQUENCIA DA PALAVRA NO TEXTO (palavra[2])
			listaTagsBoa[index].append(1)

			# ESSE SERA A FREQUENCIA DE TIPO DE ENTIDADE (palavra[3][0,1,2]), 0 eh pessoa, 1 eh organizacao, 2 eh lugar
			listaTagsBoa[index].append([0,0,0])

			tipo=int(extraiTipoEntidade(listaTagsBoa, index))

			#incrementa o possivel tipo

			listaTagsBoa[index][3][tipo]+=1

			#inclui na lista de entidades unicas

			listaSemRepeticao.append(listaTagsBoa[index])
	
	#retrosubstituicao de pronomes, mas simplorio desse jeito nao funfa		
	#if (listaTagsBoa[index][0].lower() == 'he' or listaTagsBoa[index][0].lower() == 'she') and (len(listaSemRepeticao)>0):
	#	listaTagsBoa[index][0]=listaTagsBoa[index][0]+ ' (' + listaSemRepeticao[-1][0]+ ')'

	index+=1

for palavra in listaSemRepeticao:
	classificaEntidade(palavra)			 #acha a classe daquela entidade

################################################################################
#																			   #
#                      GERANDO RETORNO DO PROGRAMA:							   #
#CADA RETORNO PODERA GERAR UM ARQUIVO COM INFORMACOES RELEVANTES IMPORTANTES   #
#ESSES SERAO SEPARADOS PARA MELHOR ENTENDIMENTO (OS OUTPUTS NO CASO)           #
#																			   #
################################################################################


##################################################################################################
#
#
#                                          Sumarizador                                           #
#
#
##################################################################################################

arqSaida4 = open('Sumario.txt', 'w')

ListaSumarioTemp = []

cont=0
titulo=''
while cont < len(listaTagsBoa): 
	titulo=identificaTitulo(listaTagsBoa[cont], titulo)
	#pegarei de frase em frase para analisar
	if listaTagsBoa[cont][1] != '.' and listaTagsBoa[cont][0]!=titulo:
		ListaSumarioTemp.append(listaTagsBoa[cont])
	else:
		ListaSumarioTemp.append(listaTagsBoa[cont])
		#isso ira fazer com que todas as falas sejam classificadas do inicio o " ate o fim do "
		if cont<(len(listaTagsBoa)-1) and listaTagsBoa[cont+1][1]=="''":
			cont+=1
			ListaSumarioTemp.append(listaTagsBoa[cont])
		#se entrar aqui significa que eh um fim de frase, e o programa ira pontuar, para saber se a frase eh um modelo de sumario
		pontos=geraPontuacaoFrase(ListaSumarioTemp, listaSemRepeticao, titulo)
		if pontos >= 6:
			#quero fazer essa parte depois que as frases ficarem boas
			#ListaSumario=sumariza(ListaSumarioTemp)
			for palavra in ListaSumarioTemp:
				arqSaida4.write (palavra[0]+ ' ')
			arqSaida4.write (str(pontos) +' \n')

		#depois dela avaliar a frase, teremos que resetar, para avaliarmos a proxima frase
		ListaSumarioTemp=[]
	cont+=1

arqSaida4.close()
