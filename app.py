from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

def carregar_dados():
    with open("dados.json", "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return dados

def salvar_dados(dados):
    with open("dados.json", "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

def calcular_estatisticas(dados):
    for filme in dados["filmes"]:

        soma_notas = 0
        quantidade_avaliacoes = 0

        for avaliacao in dados["avaliacoes"]:
            if avaliacao["filme_id"] == filme["id"]:
                soma_notas += avaliacao["nota"]
                quantidade_avaliacoes += 1

        if quantidade_avaliacoes > 0:
            filme["media"] = round(
                soma_notas / quantidade_avaliacoes,
                1
            )
        else:
            filme["media"] = None

        filme["quantidade_avaliacoes"] = quantidade_avaliacoes

    return dados["filmes"]

@app.route("/")
def dashboard():
    dados = carregar_dados()

    filmes = calcular_estatisticas(dados)

    ranking = []

    for filme in filmes:
        if filme["media"] is not None:
            ranking.append(filme)

    ranking = sorted(
        ranking,
        key=lambda 
        filme: filme["media"],
        reverse=True
    )

    filmes_recentes = list(reversed(filmes))

    return render_template(
        "dashboard.html", 
        ranking=ranking,
        filmes_recentes=filmes_recentes
    )

@app.route("/catalogo", methods=["GET", "POST"])
def catalogo():
    dados = carregar_dados()

    if request.method == "POST":

        titulo = request.form["titulo"]
        capa = request.form["capa"]
        descricao = request.form["descricao"]

        novo_filme = {
            "id": len(dados["filmes"]) + 1,
            "titulo": titulo,
            "capa_url": capa,
            "descricao": descricao
        }

        dados["filmes"].append(novo_filme)

        salvar_dados(dados)

        return redirect(url_for("catalogo"))

    filmes = calcular_estatisticas(dados)

    return render_template(
        "catalogo.html",
        filmes=filmes
    )

@app.route("/avaliacao", methods=["GET", "POST"])
def avaliacao():
    dados = carregar_dados()

    if request.method == "POST":

        filme_id = int(request.form["filme_id"])
        nota = float(request.form["nota"])
        comentario= request.form["comentario"]

        nova_avaliacao = {
            "id": len(dados["avaliacoes"]) + 1,
            "filme_id": filme_id,
            "nota": nota,
            "comentario": comentario
}

        dados["avaliacoes"].append(nova_avaliacao)

        salvar_dados(dados)

        return redirect(url_for("dashboard"))

    return render_template(
        "avaliacao.html",
        filmes=dados["filmes"]
    )

if __name__ == "__main__":
    app.run(debug=True)
