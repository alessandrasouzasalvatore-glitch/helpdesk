import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_JSON = os.path.join(BASE_DIR, "chamados.json")

STATUS_VALIDOS = {"Aberto", "Em Andamento", "Concluída", "Cancelada"}


def carregar_chamados():
    if not os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return []
            dados = json.loads(conteudo)
            return dados if isinstance(dados, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def salvar_chamados(chamados):
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(chamados, f, ensure_ascii=False, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        solicitante = (request.form.get("solicitante") or "").strip()
        equipamento = (request.form.get("equipamento") or "").strip()
        descricao = (request.form.get("descricao") or "").strip()

        if solicitante and equipamento and descricao:
            chamados = carregar_chamados()
            novo_chamado = {
                "id": str(uuid.uuid4())[:8],
                "solicitante": solicitante,
                "equipamento": equipamento,
                "descricao": descricao,
                "status": "Aberto",
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            chamados.insert(0, novo_chamado)
            salvar_chamados(chamados)

        return redirect(url_for("chamados"))

    return render_template("index.html")


@app.route("/chamados")
def chamados():
    status_filtro = (request.args.get("status") or "Todos").strip()
    todos_chamados = carregar_chamados()

    total_abertos = sum(1 for c in todos_chamados if c.get("status") == "Aberto")
    total_concluidos = sum(1 for c in todos_chamados if c.get("status") == "Concluída")
    total_cancelados = sum(1 for c in todos_chamados if c.get("status") == "Cancelada")

    if status_filtro != "Todos":
        chamados_filtrados = [
            c for c in todos_chamados if c.get("status", "Aberto") == status_filtro
        ]
    else:
        chamados_filtrados = todos_chamados

    return render_template(
        "chamados.html",
        chamados=chamados_filtrados,
        status_atual=status_filtro,
        total_geral=len(todos_chamados),
        total_abertos=total_abertos,
        total_concluidos=total_concluidos,
        total_cancelados=total_cancelados,
    )


@app.route("/status/<id_chamado>/<novo_status>")
def alterar_status(id_chamado, novo_status):
    if novo_status in STATUS_VALIDOS:
        chamados = carregar_chamados()
        for chamado in chamados:
            if str(chamado.get("id")) == str(id_chamado):
                chamado["status"] = novo_status
                break
        salvar_chamados(chamados)

    return redirect(url_for("chamados"))


@app.route("/excluir/<id_chamado>", methods=["GET", "POST"])
def excluir(id_chamado):
    chamados = carregar_chamados()
    chamados_restantes = [
        c for c in chamados if str(c.get("id")) != str(id_chamado)
    ]
    salvar_chamados(chamados_restantes)
    return redirect(url_for("chamados"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)