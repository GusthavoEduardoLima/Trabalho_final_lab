import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from imagem import Imagem, listar_imagens_do_diretorio
from download import Download
from filtros import FILTROS_DISPONIVEIS

DIRETORIO_ATUAL = os.getcwd()

app = Flask(__name__, static_folder="static", static_url_path="")

estado = {"imagem_atual": None}


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/filtros", methods=["GET"])
def api_listar_filtros():
    """Devolve os nomes dos filtros disponíveis, para popular o <select>."""
    return jsonify(list(FILTROS_DISPONIVEIS.keys()))


@app.route("/api/listar", methods=["GET"])
def api_listar_imagens():
    """Lista imagens do diretório atual."""
    try:
        arquivos = listar_imagens_do_diretorio(DIRETORIO_ATUAL)
        return jsonify(arquivos)
    except Exception as erro:
        return jsonify({"erro": f"Erro ao listar diretório: {erro}"}), 400


@app.route("/api/carregar", methods=["POST"])
def api_carregar_imagem():
    """Recebe um arquivo enviado do computador do usuário."""
    arquivo = request.files.get("arquivo")

    if arquivo is None or arquivo.filename == "":
        return jsonify({"erro": "Selecione um arquivo de imagem no seu computador."}), 400

    nome_seguro = secure_filename(arquivo.filename)
    if not nome_seguro.lower().endswith(Imagem.EXTENSOES_VALIDAS):
        return jsonify({"erro": "Extensão inválida. Use apenas .jpg ou .png."}), 400

    caminho_destino = os.path.join(DIRETORIO_ATUAL, nome_seguro)

    base, extensao = os.path.splitext(caminho_destino)
    contador = 1
    while os.path.exists(caminho_destino):
        caminho_destino = f"{base}_{contador}{extensao}"
        contador += 1

    try:
        arquivo.save(caminho_destino)

        imagem = Imagem(caminho_destino)
        imagem.carregar()
        estado["imagem_atual"] = imagem

        return jsonify({"nome_arquivo": imagem.nome_arquivo(), "url_preview": f"/api/imagem/{imagem.nome_arquivo()}"})
    except Exception as erro:
        return jsonify({"erro": f"Erro ao processar arquivo: {erro}"}), 400


@app.route("/api/carregar_url", methods=["POST"])
def api_carregar_url():
    """Recebe uma URL, baixa a imagem e carrega no sistema."""
    dados = request.get_json(silent=True) or {}
    url = (dados.get("url") or "").strip()

    if not url:
        return jsonify({"erro": "Informe uma URL válida."}), 400

    try:
        download = Download(url, DIRETORIO_ATUAL)
        if download.eh_url():
            caminho_final = download.baixar()
        else:
            caminho_final = url # Caso não seja URL, tenta tratar como caminho local

        imagem = Imagem(caminho_final)
        imagem.carregar()
        estado["imagem_atual"] = imagem

        return jsonify({"nome_arquivo": imagem.nome_arquivo(), "url_preview": f"/api/imagem/{imagem.nome_arquivo()}"})
    except Exception as erro:
        return jsonify({"erro": f"Erro ao baixar a imagem: {erro}"}), 400


@app.route("/api/carregar_existente", methods=["POST"])
def api_carregar_imagem_existente():
    """Carrega uma imagem que já está no diretório atual (escolhida na lista)."""
    dados = request.get_json(silent=True) or {}
    nome_arquivo = (dados.get("nome_arquivo") or "").strip()

    if not nome_arquivo:
        return jsonify({"erro": "Nome de arquivo inválido."}), 400

    caminho = os.path.join(DIRETORIO_ATUAL, secure_filename(nome_arquivo))

    try:
        imagem = Imagem(caminho)
        imagem.carregar()
        estado["imagem_atual"] = imagem

        return jsonify({"nome_arquivo": imagem.nome_arquivo(), "url_preview": f"/api/imagem/{imagem.nome_arquivo()}"})
    except Exception as erro:
        return jsonify({"erro": f"Erro ao carregar imagem: {erro}"}), 400


@app.route("/api/filtro", methods=["POST"])
def api_aplicar_filtro():
    """Aplica o filtro escolhido na imagem carregada."""
    dados = request.get_json(silent=True) or {}
    nome_filtro = dados.get("nome_filtro")

    if not nome_filtro or nome_filtro not in FILTROS_DISPONIVEIS:
        return jsonify({"erro": "Escolha um filtro válido antes de aplicar."}), 400

    imagem_atual = estado.get("imagem_atual")
    if imagem_atual is None:
        return jsonify({"erro": "Carregue uma imagem antes de aplicar um filtro."}), 400

    try:
        imagem_pil = imagem_atual.carregar()
        filtro = FILTROS_DISPONIVEIS[nome_filtro]
        resultado = filtro.aplicar(imagem_pil)

        nome_saida = f"{imagem_atual.nome_sem_extensao()}{filtro.sufixo}{imagem_atual.extensao()}"
        caminho_saida = os.path.join(DIRETORIO_ATUAL, nome_saida)

        imagem_para_salvar = resultado
        if imagem_atual.extensao().lower() in (".jpg", ".jpeg") and resultado.mode not in ("RGB", "L"):
            imagem_para_salvar = resultado.convert("RGB")

        imagem_para_salvar.save(caminho_saida)

        return jsonify({
            "nome_saida": nome_saida,
            "url_preview": f"/api/imagem/{nome_saida}",
        })
    except Exception as erro:
        return jsonify({"erro": f"Erro inesperado ao aplicar filtro: {erro}"}), 400


@app.route("/api/imagem/<path:nome_arquivo>", methods=["GET"])
def api_servir_imagem(nome_arquivo):
    """Rota auxiliar para servir a imagem de volta para o navegador (preview)."""
    return send_from_directory(DIRETORIO_ATUAL, nome_arquivo)


if __name__ == "__main__":
    app.run(debug=True)