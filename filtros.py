"""
Módulo com as classes de Filtros.

Cada filtro é uma classe própria que herda de Filtro e implementa o método
aplicar(), recebendo uma imagem PIL.Image e retornando a imagem já filtrada.

OBS: Versão simplificada, sem uso de decoradores/classe abstrata (ABC,
@abstractmethod). O "contrato" de que todo filtro precisa ter um método
aplicar() agora é garantido apenas por convenção: a classe-mãe Filtro
já define aplicar() lançando um erro, então se uma subclasse esquecer de
sobrescrever esse método, o erro avisa na hora de usar.
"""

from PIL import Image, ImageFilter, ImageOps, ImageChops


class Filtro:
    """Classe base para todos os filtros de imagem."""

    nome = "Filtro"
    sufixo = "_filtro"

    def aplicar(self, imagem_pil: Image.Image) -> Image.Image:
        """Recebe uma imagem PIL e retorna a imagem filtrada."""
        raise NotImplementedError("Subclasses devem implementar o método aplicar().")


class FiltroEscalaCinza(Filtro):
    """Converte a imagem para tons de cinza."""

    nome = "Escala de Cinza"
    sufixo = "_cinza"

    def aplicar(self, imagem_pil: Image.Image) -> Image.Image:
        return imagem_pil.convert("L")


class FiltroPretoBranco(Filtro):
    """Converte a imagem para preto e branco puro (1 bit), via limiarização."""

    nome = "Preto e Branco"
    sufixo = "_pb"

    def aplicar(self, imagem_pil: Image.Image) -> Image.Image:
        cinza = imagem_pil.convert("L")
        return cinza.point(lambda pixel: 255 if pixel > 128 else 0, mode='1')


class FiltroNegativo(Filtro):
    """Inverte as cores da imagem (modo foto negativa)."""

    nome = "Foto Negativa"
    sufixo = "_negativo"

    def aplicar(self, imagem_pil: Image.Image) -> Image.Image:
        rgb = imagem_pil.convert("RGB")
        return ImageOps.invert(rgb)


class FiltroContorno(Filtro):
    """Realça o contorno (bordas) da imagem."""

    nome = "Modo Contorno"
    sufixo = "_contorno"

    def aplicar(self, imagem_pil: Image.Image) -> Image.Image:
        return imagem_pil.convert("RGB").filter(ImageFilter.CONTOUR)


class FiltroBlur(Filtro):
    """Aplica desfoque gaussiano na imagem."""

    nome = "Modo Blurred"
    sufixo = "_blur"
    RAIO = 5

    def aplicar(self, imagem_pil: Image.Image) -> Image.Image:
        return imagem_pil.convert("RGB").filter(ImageFilter.GaussianBlur(radius=self.RAIO))


class FiltroCartoon(Filtro):
    """
    Simula um efeito 'cartoon': reduz a quantidade de cores (posterização)
    e sobrepõe as bordas detectadas na imagem em tons de cinza.
    """

    nome = "Filtro Cartoon"
    sufixo = "_cartoon"

    def aplicar(self, imagem_pil: Image.Image) -> Image.Image:
        rgb = imagem_pil.convert("RGB")

        # 1. Suaviza a imagem preservando regiões de cor (reduz ruído)
        suavizada = rgb.filter(ImageFilter.SMOOTH_MORE)

        # 2. Reduz a quantidade de cores para dar o aspecto "desenhado"
        posterizada = ImageOps.posterize(suavizada, bits=4)

        # 3. Detecta as bordas a partir da versão em cinza
        cinza = rgb.convert("L")
        cinza_suave = cinza.filter(ImageFilter.MedianFilter(size=7))
        bordas = cinza_suave.filter(ImageFilter.FIND_EDGES)
        # bordas fortes viram preto (0), o resto vira branco (255)
        bordas = bordas.point(lambda pixel: 0 if pixel > 20 else 255)
        bordas_rgb = bordas.convert("RGB")

        # 4. Combina bordas (pretas) com a imagem posterizada por multiplicação
        resultado = ImageChops.multiply(posterizada, bordas_rgb)
        return resultado


# Mapeamento central com todos os filtros disponíveis na aplicação.
FILTROS_DISPONIVEIS = {
    FiltroEscalaCinza.nome: FiltroEscalaCinza(),
    FiltroPretoBranco.nome: FiltroPretoBranco(),
    FiltroCartoon.nome: FiltroCartoon(),
    FiltroNegativo.nome: FiltroNegativo(),
    FiltroContorno.nome: FiltroContorno(),
    FiltroBlur.nome: FiltroBlur(),
}