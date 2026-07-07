const inputArquivo = document.getElementById("inputArquivo");
const selectFiltro = document.getElementById("selectFiltro");
const listaImagens = document.getElementById("listaImagens");
const imgResultado = document.getElementById("imgResultado");
const semResultado = document.getElementById("semResultado");
const statusMensagem = document.getElementById("statusMensagem");

function mostrarStatus(texto, erro = false) {
    statusMensagem.textContent = texto;
    statusMensagem.className = "alert " + (erro ? "alert-danger" : "alert-success");
}

function mostrarResultado(urlImagem) {
    
    imgResultado.src = urlImagem + "?t=" + Date.now();
    imgResultado.style.display = "inline-block";
    semResultado.style.display = "none";
}

async function carregarFiltros() {
    const resposta = await fetch("/api/filtros");
    const filtros = await resposta.json();
    selectFiltro.innerHTML = '<option value="">Selecione...</option>';
    filtros.forEach((nome) => {
        const opcao = document.createElement("option");
        opcao.value = nome;
        opcao.textContent = nome;
        selectFiltro.appendChild(opcao);
    });
}

// Opção 3: lista as imagens do diretório atual
async function atualizarListaImagens() {
    const resposta = await fetch("/api/listar");
    const dados = await resposta.json();

    listaImagens.innerHTML = "";
    if (dados.erro) {
        mostrarStatus(dados.erro, true);
        return;
    }
    dados.forEach((nomeArquivo) => {
        const item = document.createElement("li");
        item.className = "list-group-item list-group-item-action";
        item.style.cursor = "pointer";
        item.textContent = nomeArquivo;
        item.addEventListener("click", () => {
            carregarImagemExistente(nomeArquivo);
        });
        listaImagens.appendChild(item);
    });
}

// Opção 1: carrega a imagem escolhida no seletor de arquivos do computador
async function carregarImagem() {
    const arquivo = inputArquivo.files[0];
    if (!arquivo) {
        mostrarStatus("Selecione um arquivo de imagem no seu computador.", true);
        return;
    }

    mostrarStatus("Carregando imagem...");

    const formData = new FormData();
    formData.append("arquivo", arquivo);

    const resposta = await fetch("/api/carregar", {
        method: "POST",
        body: formData,
    });
    const dados = await resposta.json();

    if (!resposta.ok) {
        mostrarStatus(dados.erro || "Erro ao carregar imagem.", true);
        return;
    }

    mostrarStatus(`Imagem carregada: ${dados.nome_arquivo}`);
    atualizarListaImagens();
}

// Carrega uma imagem que já está no diretório atual (clicada na lista da opção 3)
async function carregarImagemExistente(nomeArquivo) {
    mostrarStatus("Carregando imagem...");

    const resposta = await fetch("/api/carregar_existente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome_arquivo: nomeArquivo }),
    });
    const dados = await resposta.json();

    if (!resposta.ok) {
        mostrarStatus(dados.erro || "Erro ao carregar imagem.", true);
        return;
    }

    mostrarStatus(`Imagem carregada: ${dados.nome_arquivo}`);
}

// Opção 2: aplica o filtro escolhido e mostra apenas o resultado
async function aplicarFiltro() {
    const nomeFiltro = selectFiltro.value;
    if (!nomeFiltro) {
        mostrarStatus("Escolha um filtro antes de aplicar.", true);
        return;
    }

    mostrarStatus("Aplicando filtro...");
    const resposta = await fetch("/api/filtro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome_filtro: nomeFiltro }),
    });
    const dados = await resposta.json();

    if (!resposta.ok) {
        mostrarStatus(dados.erro || "Erro ao aplicar filtro.", true);
        return;
    }

    mostrarResultado(dados.url_preview);
    mostrarStatus(`Filtro aplicado! Salvo em: ${dados.nome_saida}`);
    atualizarListaImagens();
}

document.getElementById("btnCarregar").addEventListener("click", carregarImagem);
document.getElementById("btnAplicarFiltro").addEventListener("click", aplicarFiltro);
document.getElementById("btnAtualizarLista").addEventListener("click", atualizarListaImagens);

// Ao abrir a página, já popula filtros e lista de imagens
carregarFiltros();
atualizarListaImagens();