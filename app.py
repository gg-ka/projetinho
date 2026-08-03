#Flask: para criar a aplicação web
#render_template: para exibir pagina HTML
#request: para pegar dados enviados por formulários
#redirect e url_for: redireciona o usuario para outra rota/pagina
from flask import Flask, render_template, request, redirect, url_for 
#importe a biblioteca json para ler e salvar arquivos desse tipo
import json

app = Flask(__name__)

def carregar_dados():
    #Abre o arquivo dados.json no modo de leitura ("r"), garantindo o suporte a acentos (encoding="utf-8").
    with open("dados.json", "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo) #Converte o conteúdo do texto JSON em um dicionário/lista nativa do Python.

    return dados

def salvar_dados(dados):
    #Abre o arquivo dados.json no modo de escrita ("w"), para sobrescrever o conteúdo antigo
    with open("dados.json", "w", encoding="utf-8") as arquivo:
        json.dump( #converte os dados python de voltar para json
            dados,
            arquivo,
            ensure_ascii=False, #mantém acentos corretos em português
            indent=4 #formata o json com recuo de 4 espaços
        )

def calcular_estatisticas(dados): #função que calcula as méduas das avaliações
    for filme in dados["filmes"]: #filmes está entre aspas pois ele quer

        soma_notas = 0
        quantidade_avaliacoes = 0

        for avaliacao in dados["avaliacoes"]:
            #Checa se o filme_id da avaliação é igual ao id do filme atual.
            if avaliacao["filme_id"] == filme["id"]:
                #Se for, adiciona a no a soma_notas
                soma_notas += avaliacao["nota"]
                #aumenta em 1 o numero total de avaliações desse filme
                quantidade_avaliacoes += 1

        #verifica se o filme tem pelo menos 1 avaliação
        if quantidade_avaliacoes > 0: 
            filme["media"] = round(
                soma_notas / quantidade_avaliacoes,
                1
            )
        else: #retorna nulo se o filme n tem nota
            filme["media"] = None

        ##guarda o total de avaliações dentro do proprio filme
        filme["quantidade_avaliacoes"] = quantidade_avaliacoes

    return dados["filmes"] #retorna a lista de filmes atualizada com as médias

@app.route("/") #endereço principal do site
def dashboard():
    dados = carregar_dados() #le o json
    filmes = calcular_estatisticas(dados) #calcula as médias

    ranking = [] #cria uma lista vazia para o ranking

    for filme in filmes: #passa por todos os filmes
        if filme["media"] is not None: #adiciona só aqueles com nota
            ranking.append(filme)

    ranking = sorted( #ordena o ranking
        ranking,
        key=lambda 
        filme: filme["media"],
        reverse=True #ordem decrescente
    )
    
    #ao inverter a lista do json a lista de filmes fica sendo exibida em ordem do mais recente para o mais antigo
    filmes_recentes = list(reversed(filmes))

    #retorna a pagina do dashboard e atualiza o ranking e deixa na ordem dos filmes mais recentes
    return render_template(
        "dashboard.html", 
        ranking=ranking,
        filmes_recentes=filmes_recentes
    )

@app.route("/catalogo", methods=["GET", "POST"]) #GET e POST significa q o usuario pode visualizar a pagina (GET) e pode enviar um formulario (POST)
def catalogo():
    dados = carregar_dados()

    #Verifica se o usuário enviou o formulário de novo filme (POST)
    if request.method == "POST":

        #Pega os valores preenchidos pelo usuário nos campos de texto HTML
        titulo = request.form["titulo"]
        capa = request.form["capa"]
        descricao = request.form["descricao"]

        #cria o novo filme com novo id
        novo_filme = {
            "id": len(dados["filmes"]) + 1,
            "titulo": titulo,
            "capa_url": capa,
            "descricao": descricao
        }

        #adiciona o filme a lista de filmes no json
        dados["filmes"].append(novo_filme)
        #salva os dados novos
        salvar_dados(dados)

        #redireciona para recarregar a pagina catalogo
        return redirect(url_for("catalogo"))

    #se for apenas o acesso GET calcula as estatisticas
    filmes = calcular_estatisticas(dados)

    #Renderiza a página catalogo noramlmente (GET)
    return render_template(
        "catalogo.html",
        filmes=filmes
    )


@app.route("/avaliacao", methods=["GET", "POST"])
def avaliacao():
    dados = carregar_dados()

    if request.method == "POST":

        #pega as informações do usuario
        filme_id = int(request.form["filme_id"])
        nota = float(request.form["nota"])
        nome_avaliador = request.form["nome_avaliador"]
        comentario = request.form["comentario"]

        #cria a nova avaliação com as insfor do usuario
        nova_avaliacao = {
            "id": len(dados["avaliacoes"]) + 1,
            "filme_id": filme_id,
            "nota": nota,
            "nome_avaliador": nome_avaliador,
            "comentario": comentario
        }

        #Insere a nova avaliação na lista dados["avaliacoes"]
        dados["avaliacoes"].append(nova_avaliacao)
        #alva a alteração no arquivo json
        salvar_dados(dados)

        #retorna para a pagina principal
        return redirect(url_for("dashboard"))

    #Renderiza a página avaliação noramlmente (GET)
    filme_selecionado = request.args.get("filme_id", type=int)

    return render_template(
        "avaliacao.html",
        filmes=dados["filmes"],
        filme_selecionado=filme_selecionado
    )

#Checa se o arquivo Python está sendo executado diretamente (não importado por outro)
#Inicia o servidor local do Flask com o modo de depuração ativado (debug=True)
if __name__ == "__main__":
    app.run(debug=True)
