"""
Módulo com a Classe Principal (Aplicacao).

Integra as classes Imagem, Download e os Filtros em uma interface gráfica
feita com Tkinter, oferecendo as opções:
  1. Informar o caminho da imagem (local ou URL)
  2. Escolher o filtro a ser aplicado
  3. Listar arquivos de imagens do diretório corrente
  4. Sair
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import ImageTk

from imagem import Imagem, listar_imagens_do_diretorio
from download import Download
from filtros import FILTROS_DISPONIVEIS

DIRETORIO_ATUAL = os.getcwd()


class Aplicacao(tk.Tk):
    """Classe Principal: janela da aplicação e coordenação de todas as classes."""

    def __init__(self):
        super().__init__()
        self.title("Filtros de imagens")
        self.geometry("950x600")
        self.minsize(800, 500)

        # Estado da aplicação
        self.imagem_atual = None       # instância de Imagem
        self.imagem_pil_atual = None   # objeto PIL.Image carregado
        self._imagem_tk = None         # referência da imagem exibida 

        self._montar_layout()
        self._atualizar_lista_imagens()

    
    def _montar_layout(self):
        painel_esquerdo = ttk.Frame(self, padding=10)
        painel_esquerdo.pack(side="left", fill="y")

        # --- Opção 1: Informar caminho da imagem ---
        ttk.Label(painel_esquerdo, text="1. Caminho local ou URL da imagem:",
                  font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        self.entry_caminho = ttk.Entry(painel_esquerdo, width=42)
        self.entry_caminho.pack(fill="x", pady=(2, 5))

        frame_botoes_caminho = ttk.Frame(painel_esquerdo)
        frame_botoes_caminho.pack(fill="x", pady=(0, 10))
        ttk.Button(frame_botoes_caminho, text="Procurar arquivo...",
                   command=self._selecionar_arquivo).pack(side="left")
        ttk.Button(frame_botoes_caminho, text="Carregar",
                   command=self._carregar_imagem).pack(side="left", padx=5)

        ttk.Separator(painel_esquerdo).pack(fill="x", pady=8)

        # --- Opção 2: Escolher filtro ---
        ttk.Label(painel_esquerdo, text="2. Escolha o filtro a aplicar:",
                  font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        self.combo_filtro = ttk.Combobox(
            painel_esquerdo,
            values=list(FILTROS_DISPONIVEIS.keys()),
            state="readonly",
        )
        self.combo_filtro.pack(fill="x", pady=(2, 5))
        ttk.Button(painel_esquerdo, text="Aplicar filtro",
                   command=self._aplicar_filtro).pack(fill="x")

        ttk.Separator(painel_esquerdo).pack(fill="x", pady=8)

        # --- Opção 3: Listar imagens do diretório ---
        ttk.Label(painel_esquerdo, text="3. Imagens no diretório atual:",
                  font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        self.lista_imagens = tk.Listbox(painel_esquerdo, height=12)
        self.lista_imagens.pack(fill="both", expand=True, pady=(2, 5))
        self.lista_imagens.bind("<<ListboxSelect>>", self._selecionar_da_lista)

        frame_botoes_lista = ttk.Frame(painel_esquerdo)
        frame_botoes_lista.pack(fill="x")
        ttk.Button(frame_botoes_lista, text="Atualizar lista",
                   command=self._atualizar_lista_imagens).pack(side="left")

        # --- Opção 4: Sair ---
        ttk.Button(frame_botoes_lista, text="4. Sair",
                   command=self._sair).pack(side="right")

        # --- Painel direito: pré-visualização ---
        painel_direito = ttk.Frame(self, padding=10)
        painel_direito.pack(side="right", fill="both", expand=True)

        ttk.Label(painel_direito, text="Pré-visualização:",
                  font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        self.label_imagem = ttk.Label(painel_direito, relief="sunken", anchor="center")
        self.label_imagem.pack(fill="both", expand=True, pady=5)

        self.label_status = ttk.Label(painel_direito, text="Pronto.", foreground="blue",
                                       wraplength=500)
        self.label_status.pack(anchor="w", fill="x")

    # ---------------------------------------------------------------------
    # AÇÕES
    # ---------------------------------------------------------------------
    def _status(self, texto: str, erro: bool = False):
        self.label_status.config(text=texto, foreground="red" if erro else "blue")

    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.entry_caminho.delete(0, tk.END)
            self.entry_caminho.insert(0, caminho)

    def _carregar_imagem(self):
        """Opção 1 do menu: informa e carrega a imagem (local ou via download)."""
        caminho = self.entry_caminho.get().strip()
        if not caminho:
            messagebox.showwarning("Atenção", "Informe um caminho local ou uma URL de imagem.")
            return

        # Roda em thread separada para não travar a interface durante o download
        threading.Thread(target=self._tarefa_carregar_imagem, args=(caminho,), daemon=True).start()

    def _tarefa_carregar_imagem(self, caminho: str):
        try:
            # Cria um objeto Download já com o caminho e o diretório de destino
            download = Download(caminho, DIRETORIO_ATUAL)

            if download.eh_url():
                self.after(0, lambda: self._status("Baixando imagem da internet..."))
                caminho_final = download.baixar()
            else:
                caminho_final = caminho

            imagem = Imagem(caminho_final)
            imagem_pil = imagem.carregar()

            self.imagem_atual = imagem
            self.imagem_pil_atual = imagem_pil

            self.after(0, lambda: self._mostrar_preview(imagem_pil))
            self.after(0, lambda: self._status(f"Imagem carregada: {imagem.nome_arquivo()}"))
            self.after(0, self._atualizar_lista_imagens)

        except (ValueError, FileNotFoundError, IOError, ConnectionError,
                OSError, NotADirectoryError) as erro:
            mensagem = str(erro)
            self.after(0, lambda: self._status(mensagem, erro=True))
            self.after(0, lambda: messagebox.showerror("Erro ao carregar imagem", mensagem))
        except Exception as erro:  # salvaguarda contra erros inesperados
            mensagem = f"Erro inesperado: {erro}"
            self.after(0, lambda: messagebox.showerror("Erro inesperado", mensagem))

    def _aplicar_filtro(self):
        """Opção 2 do menu: aplica o filtro escolhido na imagem carregada."""
        nome_filtro = self.combo_filtro.get()
        if not nome_filtro:
            messagebox.showwarning("Atenção", "Escolha um filtro antes de aplicar.")
            return
        if self.imagem_pil_atual is None or self.imagem_atual is None:
            messagebox.showwarning("Atenção", "Carregue uma imagem antes de aplicar um filtro.")
            return

        try:
            filtro = FILTROS_DISPONIVEIS[nome_filtro]
            resultado = filtro.aplicar(self.imagem_pil_atual)

            nome_saida = f"{self.imagem_atual.nome_sem_extensao()}{filtro.sufixo}{self.imagem_atual.extensao()}"
            caminho_saida = os.path.join(DIRETORIO_ATUAL, nome_saida)

            # Formatos como '1' (preto e branco puro) não suportam salvar em JPEG
            imagem_para_salvar = resultado
            if self.imagem_atual.extensao().lower() in ('.jpg', '.jpeg') and resultado.mode not in ("RGB", "L"):
                imagem_para_salvar = resultado.convert("RGB")

            imagem_para_salvar.save(caminho_saida)

            self._mostrar_preview(resultado)
            self._status(f"Filtro '{nome_filtro}' aplicado com sucesso! Salvo em: {nome_saida}")
            self._atualizar_lista_imagens()

        except (OSError, ValueError) as erro:
            messagebox.showerror("Erro ao aplicar filtro", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro inesperado", f"Erro inesperado ao aplicar filtro: {erro}")

    def _mostrar_preview(self, imagem_pil):
        try:
            copia = imagem_pil.copy()
            copia.thumbnail((560, 500))
            if copia.mode not in ("RGB", "L", "RGBA"):
                copia = copia.convert("RGB")
            self._imagem_tk = ImageTk.PhotoImage(copia)
            self.label_imagem.config(image=self._imagem_tk, text="")
        except Exception as erro:
            messagebox.showerror("Erro ao exibir imagem", str(erro))

    def _atualizar_lista_imagens(self):
        """Opção 3 do menu: lista os arquivos de imagem do diretório atual."""
        try:
            arquivos = listar_imagens_do_diretorio(DIRETORIO_ATUAL)
            self.lista_imagens.delete(0, tk.END)
            for arquivo in arquivos:
                self.lista_imagens.insert(tk.END, arquivo)
        except (OSError, NotADirectoryError) as erro:
            messagebox.showerror("Erro ao listar diretório", str(erro))

    def _selecionar_da_lista(self, event):
        selecao = self.lista_imagens.curselection()
        if not selecao:
            return
        nome_arquivo = self.lista_imagens.get(selecao[0])
        self.entry_caminho.delete(0, tk.END)
        self.entry_caminho.insert(0, os.path.join(DIRETORIO_ATUAL, nome_arquivo))
        self._carregar_imagem()

    def _sair(self):
        """Opção 4 do menu: encerra a execução do programa."""
        self.destroy()


def executar():
    app = Aplicacao()
    app.mainloop()


if __name__ == "__main__":
    executar()