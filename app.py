from flask import Flask, render_template, request, redirect
from datetime import datetime
import json
import os

app = Flask(__name__)

ARQUIVO = "chamados.json"


def carregar_chamados():
    if not os.path.exists(ARQUIVO):
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except json.JSONDecodeError:
        return []


def salvar_chamados(chamados):
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(chamados, arquivo, indent=4, ensure_ascii=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/abrir", methods=["POST"])
def abrir():

    chamados = carregar_chamados()

    novo = {
        "id": len(chamados) + 1,
        "solicitante": request.form["solicitante"],
        "equipamento": request.form["equipamento"],
        "descricao": request.form["descricao"],
        "status": "Aberto",
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    chamados.append(novo)

    salvar_chamados(chamados)

    return redirect("/")


@app.route("/chamados")
def chamados():

    lista = carregar_chamados()

    filtro = request.args.get("status")


    if filtro and filtro != "Todos":

        lista = [
            chamado
            for chamado in lista
            if chamado["status"] == filtro
        ]


    return render_template(
        "chamados.html",
        chamados=lista
    )


# Rota para alterar o status do chamado
@app.route("/status/<int:id>/<novo_status>")
def alterar_status(id, novo_status):

    chamados = carregar_chamados()


    for chamado in chamados:

        if chamado["id"] == id:

            chamado["status"] = novo_status


    salvar_chamados(chamados)


    return redirect("/chamados")



# Rota para excluir chamado
@app.route("/excluir/<int:id>")
def excluir(id):

    chamados = carregar_chamados()


    chamados = [
        chamado
        for chamado in chamados
        if chamado["id"] != id
    ]


    salvar_chamados(chamados)


    return redirect("/chamados")



if __name__ == "__main__":
    app.run(debug=True)
    