"""
Módulo com a classe Download.

Responsável por identificar se um caminho informado é uma URL pública
e por baixar a imagem correspondente, salvando-a localmente.

OBS: Versão simplificada, sem uso de decoradores (@staticmethod).
Agora o Download é criado com o caminho/URL e o diretório de destino,
e os métodos trabalham com esses dados guardados na própria instância.
"""

import os
from urllib.parse import urlparse

import requests


class Download:
    """Responsável por baixar arquivos de imagem a partir de uma URL pública."""

    EXTENSOES_VALIDAS = ('.jpg', '.jpeg', '.png')
    TIMEOUT_SEGUNDOS = 15

    def __init__(self, caminho: str, diretorio_destino: str = '.'):
        self.caminho = caminho
        self.diretorio_destino = diretorio_destino

    def eh_url(self) -> bool:
        """Retorna True se o caminho informado for uma URL http/https."""
        try:
            resultado = urlparse(self.caminho)
            return resultado.scheme in ('http', 'https') and bool(resultado.netloc)
        except ValueError:
            return False

    def baixar(self) -> str:
        """
        Baixa a imagem da URL informada e salva no diretório de destino.
        Retorna o caminho completo do arquivo salvo.
        """
        if not self.eh_url():
            raise ValueError(f"URL inválida: {self.caminho}")

        nome_arquivo = os.path.basename(urlparse(self.caminho).path)
        if not nome_arquivo or not nome_arquivo.lower().endswith(self.EXTENSOES_VALIDAS):
            nome_arquivo = "imagem_baixada.jpg"

        # Evita sobrescrever arquivos existentes
        caminho_destino = os.path.join(self.diretorio_destino, nome_arquivo)
        base, extensao = os.path.splitext(caminho_destino)
        contador = 1
        while os.path.exists(caminho_destino):
            caminho_destino = f"{base}_{contador}{extensao}"
            contador += 1

        try:
            resposta = requests.get(self.caminho, timeout=self.TIMEOUT_SEGUNDOS, stream=True)
            resposta.raise_for_status()
        except requests.RequestException as erro:
            raise ConnectionError(f"Erro ao baixar a imagem de '{self.caminho}': {erro}") from erro

        content_type = resposta.headers.get('Content-Type', '')
        if 'image' not in content_type.lower():
            raise ValueError(
                f"O conteúdo retornado pela URL não parece ser uma imagem (Content-Type: {content_type})."
            )

        try:
            with open(caminho_destino, 'wb') as arquivo:
                for pedaco in resposta.iter_content(chunk_size=8192):
                    arquivo.write(pedaco)
        except OSError as erro:
            raise IOError(f"Erro ao salvar a imagem em '{caminho_destino}': {erro}") from erro

        return caminho_destino