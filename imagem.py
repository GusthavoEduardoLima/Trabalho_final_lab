"""
Módulo com a classe Imagem.

Representa um arquivo de imagem (.jpg ou .png), validando sua extensão,
carregando o conteúdo com Pillow e oferecendo utilitários relacionados
(como listar as imagens de um diretório).

OBS: Versão simplificada, sem uso de decoradores (@staticmethod, @property).
"""

import os
from PIL import Image


class Imagem:
    """Representa um arquivo de imagem no formato .jpg ou .png."""

    EXTENSOES_VALIDAS = ('.jpg', '.jpeg', '.png')

    def __init__(self, caminho: str):
        if not caminho:
            raise ValueError("O caminho da imagem não pode ser vazio.")
        self.caminho = caminho
        self._validar_extensao()
        self._imagem_pil = None

    def _validar_extensao(self):
        extensao = os.path.splitext(self.caminho)[1].lower()
        if extensao not in self.EXTENSOES_VALIDAS:
            raise ValueError(
                f"Extensão inválida '{extensao}'. Use apenas .jpg ou .png."
            )

    def carregar(self):
        """Carrega a imagem do disco usando Pillow e retorna o objeto PIL.Image."""
        if not os.path.isfile(self.caminho):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho}")
        try:
            imagem_pil = Image.open(self.caminho)
            imagem_pil.load()
        except Exception as erro:
            raise IOError(f"Erro ao abrir a imagem '{self.caminho}': {erro}") from erro

        self._imagem_pil = imagem_pil
        return self._imagem_pil

    def nome_arquivo(self) -> str:
        """Retorna o nome do arquivo (com extensão), ex: 'foto.jpg'."""
        return os.path.basename(self.caminho)

    def nome_sem_extensao(self) -> str:
        """Retorna o nome do arquivo sem a extensão, ex: 'foto'."""
        return os.path.splitext(self.nome_arquivo())[0]

    def extensao(self) -> str:
        """Retorna a extensão do arquivo, ex: '.jpg'."""
        return os.path.splitext(self.nome_arquivo())[1]

    def __repr__(self):
        return f"Imagem(caminho='{self.caminho}')"


def listar_imagens_do_diretorio(diretorio: str = '.') -> list:
    """
    Lista os arquivos .jpg/.png presentes em um diretório, em ordem alfabética.

    Ficou como uma função comum (fora da classe) porque não representa
    uma imagem específica: é apenas um utilitário do módulo.
    """
    if not os.path.isdir(diretorio):
        raise NotADirectoryError(f"Diretório inválido: {diretorio}")
    try:
        arquivos = [
            arquivo for arquivo in os.listdir(diretorio)
            if arquivo.lower().endswith(Imagem.EXTENSOES_VALIDAS)
        ]
    except OSError as erro:
        raise OSError(f"Erro ao listar o diretório '{diretorio}': {erro}") from erro

    return sorted(arquivos)