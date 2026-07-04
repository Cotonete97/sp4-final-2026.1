#!/usr/bin/env python3
# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
"""
Benchmark para o chunk_document() da Tarefa 02.

Métricas capturadas:
  - Número de chunks
  - Tamanho dos chunks (min, max, média, std)
  - Fronteiras: preview dos chunks gerados
  - Abreviações: análise detalhada de splits internos e externos
  - Ruído textual: artefatos como \n\n no meio de sentenças
  - Tempo de execução

Uso:
    python tests/benchmark_chunking.py             # roda e salva baseline
    python tests/benchmark_chunking.py --compare   # compara com baseline salvo
"""

# Comentário explicativo: Importa o módulo `json` para ser usado neste arquivo.
import json
# Comentário explicativo: Importa o módulo `re` para ser usado neste arquivo.
import re
# Comentário explicativo: Importa o módulo `sys` para ser usado neste arquivo.
import sys
# Comentário explicativo: Importa o módulo `time` para ser usado neste arquivo.
import time
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from pathlib import Path

# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from chunking import chunk_document, _SENTENCE_SEPARATOR_PATTERN

# Comentário explicativo: Define ou atualiza `BENCHMARK_FILE` com o valor calculado à direita.
BENCHMARK_FILE = Path(__file__).parent / "benchmark_chunking_result.json"

# =====================================================================
# TEXTOS DE TESTE
# =====================================================================

# Comentário explicativo: Define ou atualiza `TEXTO_CONTROLE` com o valor calculado à direita.
TEXTO_CONTROLE = """
Procedimento de recuperação de acesso ao sistema institucional.
O usuário deve acessar a página oficial de autenticação e selecionar
a opção Esqueci minha senha. Em seguida, deve informar o e-mail
institucional cadastrado e aguardar o envio da mensagem com o link
temporário de redefinição.

O link deve ser utilizado dentro do prazo informado na mensagem.
Caso o e-mail não seja recebido, o usuário deve verificar as pastas
de spam e lixo eletrônico.

Depois da redefinição, a nova senha deve respeitar os critérios
exibidos na tela, incluindo tamanho mínimo e combinação de letras,
números e caracteres especiais.

Quando a conta estiver bloqueada por excesso de tentativas, o usuário
deve aguardar o período indicado antes de tentar novamente. Se o
bloqueio permanecer, o chamado deve ser encaminhado ao atendimento
responsável por acessos.
""".strip()

# Comentário explicativo: Define ou atualiza `TEXTO_ABREVIACOES` com o valor calculado à direita.
TEXTO_ABREVIACOES = """
O Dr. Carlos Eduardo da Silva compareceu à reunião com a Sra. Maria
Aparecida para discutir o contrato. O Sr. João Pedro, representante
da empresa, apresentou os documentos necessários.

O Dr. Silva solicitou a análise do processo etc. O prazo estipulado
pela Sra. Maria foi de 30 dias corridos. Após esse período, o
contrato será automaticamente renovado.

A Sra. Aparecida confirmou que a empresa X Ltda. está apta a
participar da licitação. O Dr. Carlos fará a auditoria final.
""".strip()

# Comentário explicativo: Define ou atualiza `TEXTO_LONGO` com o valor calculado à direita.
TEXTO_LONGO = """
Seção 1: Introdução ao sistema de atendimento institucional.

O sistema de atendimento institucional foi desenvolvido para
centralizar as solicitações dos usuários e permitir o rastreamento
completo do ciclo de vida de cada chamado. Este documento descreve
os procedimentos operacionais padrão que devem ser seguidos por
todos os atendentes.

Seção 2: Abertura de chamados.

Para abrir um novo chamado, o atendente deve acessar o módulo de
cadastro e preencher os campos obrigatórios: nome do solicitante,
setor, descrição do problema e nível de urgência. O sistema
automaticamente atribuirá um número de protocolo.

A descrição do problema deve ser clara e objetiva. Evite termos
técnicos desnecessários. Inclua o passo a passo realizado até o
momento do erro. Informe também qual sistema estava sendo utilizado
e a mensagem de erro exibida.

Seção 3: Classificação e priorização.

Cada chamado recebe uma classificação baseada no tipo de solicitação:
incidente, requisição de serviço ou acesso à informação. A prioridade
é definida automaticamente pelo sistema com base na combinação de
urgência e impacto.

Chamados classificados como críticos devem ser atendidos em até
2 horas úteis. Chamados de alta prioridade têm prazo de 8 horas
úteis. Chamados de média prioridade têm prazo de 24 horas úteis.
Chamados de baixa prioridade têm prazo de 72 horas úteis.

Seção 4: Procedimentos de escalonamento.

Quando o atendente não conseguir resolver o chamado dentro do prazo
estabelecido, o caso deve ser escalonado para o nível 2 de suporte.
O escalonamento deve incluir um resumo do que já foi testado e o
motivo pelo qual o chamado não pôde ser resolvido no nível 1.

O nível 2 de suporte tem acesso a ferramentas administrativas e
pode realizar alterações na configuração dos sistemas. Caso o
chamado ainda não seja resolvido, ele é escalonado para o nível 3,
que corresponde à equipe de engenharia responsável pelo sistema.

Seção 5: Encerramento de chamados.

O chamado pode ser encerrado quando o usuário confirmar que o problema
foi resolvido. O atendente deve registrar a solução aplicada e o
tempo total de atendimento. Chamados encerrados sem confirmação do
usuário devem ser reabertos automaticamente.

Chamados que permanecerem sem atividade por mais de 15 dias úteis
são automaticamente suspensos. O usuário é notificado por e-mail
antes da suspensão e pode reativar o chamado dentro de 5 dias úteis.
""".strip()


# =====================================================================
# MÉTRICAS
# =====================================================================

# Lista de abreviações portuguesas que NÃO devem ser confundidas com fim de frase
# Comentário explicativo: Define ou atualiza `_ABREVIACOES_CONHECIDAS` com o valor calculado à direita.
_ABREVIACOES_CONHECIDAS = [
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "Dr", "Sr", "Sra", "Srta", "Srtas", "Srs", "Sras",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "etc", "Ltda",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "obs", "art", "pag", "vol", "cap", "ed",
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    "Ex", "V",  # Excelentíssimo, Vossa
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
]
# Comentário explicativo: Define ou atualiza `_PAT_ABREV_FIM` com o valor calculado à direita.
_PAT_ABREV_FIM = re.compile(
    # Comentário explicativo: Define ou atualiza `r"\b(" + "|".join(_ABREVIACOES_CONHECIDAS) + r")\.(?` com o valor calculado à direita.
    r"\b(" + "|".join(_ABREVIACOES_CONHECIDAS) + r")\.(?=\s)",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    re.UNICODE,
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
)

# Padrão para detectar abreviações que antecedem \n\n dentro de chunks
# Procura por abreviatura + "." + imediatamente seguido de \n\n (sem espaço entre)
# Comentário explicativo: Define ou atualiza `_PAT_ABREV_NN` com o valor calculado à direita.
_PAT_ABREV_NN = re.compile(
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    r"\b(" + "|".join(_ABREVIACOES_CONHECIDAS) + r")\.\n\n",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    re.UNICODE,
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
)


# Comentário explicativo: Define a função `analisar_abreviacoes`, que encapsula uma parte específica da lógica do projeto.
def analisar_abreviacoes(texto_original: str, chunks: list) -> dict:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Analisa como as abreviações foram tratadas no chunking.

    1. Conta abreviações no texto original
    2. Verifica se dentro dos chunks alguma abreviatura foi seguida
       de \n\n (artefato do split incorreto)
    3. Verifica se alguma abreviatura ficou como última palavra de um chunk
    """
    # Encontra todas as abreviações no texto original
    # Comentário explicativo: Define ou atualiza `ocorrencias` com o valor calculado à direita.
    ocorrencias = list(_PAT_ABREV_FIM.finditer(texto_original))
    # Comentário explicativo: Define ou atualiza `total_abrev` com o valor calculado à direita.
    total_abrev = len(ocorrencias)

    # Procura por "Abrev.\n\n" dentro de cada chunk
    # Comentário explicativo: Define ou atualiza `abrev_com_artefato` com o valor calculado à direita.
    abrev_com_artefato = 0
    # Comentário explicativo: Define ou atualiza `abrev_quebrada` com o valor calculado à direita.
    abrev_quebrada = 0
    # Comentário explicativo: Define ou atualiza `artefatos_detectados` com o valor calculado à direita.
    artefatos_detectados = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in chunks:
        # Comentário explicativo: Define ou atualiza `texto` com o valor calculado à direita.
        texto = chunk["texto"]

        # Método 1: procura diretamente por "Abrev.\n\n" no chunk
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for m in _PAT_ABREV_NN.finditer(texto):
            # Comentário explicativo: Define ou atualiza `abrev_com_artefato +` com o valor calculado à direita.
            abrev_com_artefato += 1
            # Comentário explicativo: Define ou atualiza `ctx` com o valor calculado à direita.
            ctx = texto[max(0, m.start() - 10):m.end() + 15].replace("\n", "\\n")
            # Comentário explicativo: Define ou atualiza `grp` com o valor calculado à direita.
            grp = m.group().replace(chr(10), "\\n")
            artefatos_detectados.append(f"'{grp}' em '{ctx}'")

        # Método 2: verifica se chunk termina com abreviatura
        # Comentário explicativo: Define ou atualiza `texto_clean` com o valor calculado à direita.
        texto_clean = texto.rstrip()
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for m in _PAT_ABREV_FIM.finditer(texto_clean):
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if m.end() == len(texto_clean):
                # Comentário explicativo: Define ou atualiza `abrev_quebrada +` com o valor calculado à direita.
                abrev_quebrada += 1

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "total_abreviacoes": total_abrev,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "com_artefato_nn": abrev_com_artefato,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "no_fim_do_chunk": abrev_quebrada,
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "integridade_pct": round(
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            (1 - (abrev_com_artefato + abrev_quebrada) / total_abrev) * 100, 1
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ) if total_abrev > 0 else 100.0,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "artefatos": artefatos_detectados[:10],
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# Comentário explicativo: Define a função `medir_tamanhos_chunks`, que encapsula uma parte específica da lógica do projeto.
def medir_tamanhos_chunks(chunks: list) -> dict:
    # Comentário explicativo: Define ou atualiza `tamanhos` com o valor calculado à direita.
    tamanhos = [len(c["texto"]) for c in chunks]
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not tamanhos:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return {"min": 0, "max": 0, "media": 0, "std": 0, "total": 0}

    # Comentário explicativo: Define ou atualiza `media` com o valor calculado à direita.
    media = sum(tamanhos) / len(tamanhos)
    # Comentário explicativo: Define ou atualiza `var` com o valor calculado à direita.
    var = sum((t - media) ** 2 for t in tamanhos) / len(tamanhos)
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "min": min(tamanhos),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "max": max(tamanhos),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "media": round(media, 1),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "std": round(var ** 0.5, 1),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "total": len(chunks),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# Comentário explicativo: Define a função `medir_ruido_sentenca`, que encapsula uma parte específica da lógica do projeto.
def medir_ruido_sentenca(chunks: list) -> dict:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Detecta \n\n no meio de sentenças (artefato de split incorreto).

    Um \n\n é considerado ruído quando:
    - Não está após pontuação de fim de frase VÁLIDA
    - OU está após uma abreviatura conhecida (Dr., Sr., etc.)
    """
    # Comentário explicativo: Define ou atualiza `total_nn_interno` com o valor calculado à direita.
    total_nn_interno = 0
    # Comentário explicativo: Define ou atualiza `locais` com o valor calculado à direita.
    locais = []

    # Pattern para detectar abreviação antes de \n\n
    # Comentário explicativo: Define ou atualiza `abrev_antes_nn` com o valor calculado à direita.
    abrev_antes_nn = re.compile(
        # Comentário explicativo: Define ou atualiza `r"\b(" + "|".join(_ABREVIACOES_CONHECIDAS) + r")\.(?` com o valor calculado à direita.
        r"\b(" + "|".join(_ABREVIACOES_CONHECIDAS) + r")\.(?=\s*\n\n)",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        re.UNICODE,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in chunks:
        # Comentário explicativo: Define ou atualiza `texto` com o valor calculado à direita.
        texto = chunk["texto"]
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for m in re.finditer(r"\n\n", texto):
            # Comentário explicativo: Define ou atualiza `pos` com o valor calculado à direita.
            pos = m.start()
            # Comentário explicativo: Define ou atualiza `antes` com o valor calculado à direita.
            antes = texto[pos - 1] if pos > 0 else " "

            # Se antes do \n\n tem uma abreviatura → ruído
            # Verifica olhando pra trás
            # Comentário explicativo: Define ou atualiza `trecho_anterior` com o valor calculado à direita.
            trecho_anterior = texto[max(0, pos - 10):pos]
            # Comentário explicativo: Define ou atualiza `eh_abrev` com o valor calculado à direita.
            eh_abrev = bool(abrev_antes_nn.search(trecho_anterior + "\n\n"))

            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if eh_abrev:
                # Comentário explicativo: Define ou atualiza `total_nn_interno +` com o valor calculado à direita.
                total_nn_interno += 1
            # Comentário explicativo: Testa uma condição alternativa caso as condições anteriores não tenham sido satisfeitas.
            elif antes not in (".", "!", "?", ":", ";"):
                # Comentário explicativo: Define ou atualiza `total_nn_interno +` com o valor calculado à direita.
                total_nn_interno += 1
            # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
            else:
                # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
                continue  # \n\n em fim de frase legítimo

            # Comentário explicativo: Define ou atualiza `ctx` com o valor calculado à direita.
            ctx = texto[max(0, pos - 15):pos + 15].replace("\n", "\\n")
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            locais.append(ctx[:50])

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "total_nn_interno": total_nn_interno,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "locais": locais[:8],
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# =====================================================================
# MAIN
# =====================================================================

# Comentário explicativo: Define ou atualiza `METADATA_PADRAO` com o valor calculado à direita.
METADATA_PADRAO = {
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "titulo": "Benchmark - Procedimentos Operacionais",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "fonte": "Documento de teste - benchmark interno",
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
}

# Comentário explicativo: Define ou atualiza `CENARIOS` com o valor calculado à direita.
CENARIOS = [
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("controle", TEXTO_CONTROLE, "Texto controle — sem abreviações complicadas"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("abreviacoes", TEXTO_ABREVIACOES, "Texto rico em abreviações (Dr., Sr., Sra., etc.)"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("longo", TEXTO_LONGO, "Texto longo — múltiplas seções e parágrafos"),
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
]


# Comentário explicativo: Define a função `benchmark_texto`, que encapsula uma parte específica da lógica do projeto.
def benchmark_texto(nome: str, texto: str, metadata: dict) -> dict:
    # Comentário explicativo: Define ou atualiza `t0` com o valor calculado à direita.
    t0 = time.perf_counter()
    # Comentário explicativo: Define ou atualiza `chunks` com o valor calculado à direita.
    chunks = chunk_document(texto, metadata)
    # Comentário explicativo: Define ou atualiza `elapsed` com o valor calculado à direita.
    elapsed = time.perf_counter() - t0

    # Comentário explicativo: Define ou atualiza `tamanhos` com o valor calculado à direita.
    tamanhos = medir_tamanhos_chunks(chunks)
    # Comentário explicativo: Define ou atualiza `abreviacoes` com o valor calculado à direita.
    abreviacoes = analisar_abreviacoes(texto, chunks)
    # Comentário explicativo: Define ou atualiza `ruido` com o valor calculado à direita.
    ruido = medir_ruido_sentenca(chunks)

    # Comentário explicativo: Define ou atualiza `fronteiras` com o valor calculado à direita.
    fronteiras = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for c in chunks:
        # Comentário explicativo: Define ou atualiza `preview` com o valor calculado à direita.
        preview = c["texto"][:80].replace("\n", " ").strip()
        fronteiras.append(f"Chunk {c['id']}: \"{preview}\"")

    # Detalhe dos splits internos (mostra a posição de cada \n\n)
    # Comentário explicativo: Define ou atualiza `splits_internos` com o valor calculado à direita.
    splits_internos = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for c in chunks:
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for m in re.finditer(r"\n\n", c["texto"]):
            # Comentário explicativo: Define ou atualiza `ctx` com o valor calculado à direita.
            ctx = c["texto"][max(0, m.start() - 20):m.end() + 20]
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            splits_internos.append(ctx.replace("\n", "\\n").strip())

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "nome": nome,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto_len": len(texto),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "tempo_seg": round(elapsed, 4),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "chunks": tamanhos,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "abreviacoes": abreviacoes,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "ruido": ruido,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "fronteiras": fronteiras,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "splits_internos": splits_internos[:10],
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# Comentário explicativo: Define a função `rodar_benchmark`, que encapsula uma parte específica da lógica do projeto.
def rodar_benchmark() -> dict:
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  BENCHMARK — chunk_document() da Tarefa 02")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()

    # Comentário explicativo: Define ou atualiza `resultados` com o valor calculado à direita.
    resultados = {}
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for nome, texto, desc in CENARIOS:
        print(f"  [{nome}] {desc}")
        print(f"         {len(texto)} caracteres")
        # Comentário explicativo: Define ou atualiza `r` com o valor calculado à direita.
        r = benchmark_texto(nome, texto, METADATA_PADRAO)
        # Comentário explicativo: Define ou atualiza `resultados[nome]` com o valor calculado à direita.
        resultados[nome] = r
        print(f"         → {r['chunks']['total']} chunks em {r['tempo_seg']:.4f}s")
        # Comentário explicativo: Define ou atualiza `a` com o valor calculado à direita.
        a = r["abreviacoes"]
        print(f"         → abreviações: {a['total_abreviacoes']} total, "
              f"{a['com_artefato_nn']} com \\n\\n, {a['no_fim_do_chunk']} no fim")
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if a["artefatos"]:
            # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
            for art in a["artefatos"][:3]:
                print(f"           • {art}")
        # Comentário explicativo: Define ou atualiza `ruido` com o valor calculado à direita.
        ruido = r["ruido"]
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if ruido["total_nn_interno"]:
            print(f"         → ⚠️ {ruido['total_nn_interno']} quebras \\n\\n no meio de sentenças")
            # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
            for loc in ruido["locais"][:3]:
                print(f"           • {loc}")
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if r["splits_internos"]:
            print(f"         → splits \\n\\n detectados no chunk:")
            # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
            for s in r["splits_internos"][:3]:
                print(f"           • ...{s}...")
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print()

    # Comentário explicativo: Define ou atualiza `total_chunks` com o valor calculado à direita.
    total_chunks = sum(r["chunks"]["total"] for r in resultados.values())
    # Comentário explicativo: Define ou atualiza `total_artefatos` com o valor calculado à direita.
    total_artefatos = sum(r["abreviacoes"]["com_artefato_nn"] for r in resultados.values())
    # Comentário explicativo: Define ou atualiza `total_quebradas` com o valor calculado à direita.
    total_quebradas = sum(r["abreviacoes"]["no_fim_do_chunk"] for r in resultados.values())
    # Comentário explicativo: Define ou atualiza `total_abrev` com o valor calculado à direita.
    total_abrev = sum(r["abreviacoes"]["total_abreviacoes"] for r in resultados.values())
    # Comentário explicativo: Define ou atualiza `total_ruido` com o valor calculado à direita.
    total_ruido = sum(r["ruido"]["total_nn_interno"] for r in resultados.values())
    # Comentário explicativo: Define ou atualiza `tempo_total` com o valor calculado à direita.
    tempo_total = sum(r["tempo_seg"] for r in resultados.values())

    # Comentário explicativo: Define ou atualiza `resumo` com o valor calculado à direita.
    resumo = {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "versao": "baseline",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "cenarios": resultados,
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "agregado": {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "total_chunks": total_chunks,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "abreviacoes_total": total_abrev,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "abreviacoes_com_artefato": total_artefatos,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "abreviacoes_quebradas": total_quebradas,
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "abreviacoes_integridade_pct": round(
                # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
                (1 - (total_artefatos + total_quebradas) / total_abrev) * 100, 1
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ) if total_abrev > 0 else 100.0,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "ruido_nn_interno": total_ruido,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "tempo_total_seg": round(tempo_total, 4),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }

    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("-" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  RESUMO AGREGADO")
    print(f"    Total de chunks:               {resumo['agregado']['total_chunks']}")
    print(f"    Abreviações com artefato:       {resumo['agregado']['abreviacoes_com_artefato']}/{resumo['agregado']['abreviacoes_total']}")
    print(f"    Abreviações no fim do chunk:    {resumo['agregado']['abreviacoes_quebradas']}/{resumo['agregado']['abreviacoes_total']}")
    print(f"    Integridade abreviações:        {resumo['agregado']['abreviacoes_integridade_pct']}%")
    print(f"    Ruído \\n\\n em sentenças:         {resumo['agregado']['ruido_nn_interno']}")
    print(f"    Tempo total:                    {resumo['agregado']['tempo_total_seg']}s")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 70)

    # Comentário explicativo: Define ou atualiza `BENCHMARK_FILE.write_text(json.dumps(resumo, ensure_ascii` com o valor calculado à direita.
    BENCHMARK_FILE.write_text(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(f"\n  Resultados salvos em: {BENCHMARK_FILE}")
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return resumo


# Comentário explicativo: Define a função `comparar_com_baseline`, que encapsula uma parte específica da lógica do projeto.
def comparar_com_baseline():
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not BENCHMARK_FILE.exists():
        print(f"  Arquivo de baseline não encontrado: {BENCHMARK_FILE}")
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("  Rode primeiro sem --compare para gerar a baseline.")
        # Comentário explicativo: Encerra a função neste ponto sem retornar um valor explícito.
        return

    # Comentário explicativo: Define ou atualiza `baseline` com o valor calculado à direita.
    baseline = json.loads(BENCHMARK_FILE.read_text())
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  COMPARAÇÃO — baseline vs versão atual")
    print(f"  Baseline: {baseline['timestamp']} (versao: {baseline['versao']})")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 70)

    # Comentário explicativo: Define ou atualiza `resultados_atuais` com o valor calculado à direita.
    resultados_atuais = {}
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for nome, texto, desc in CENARIOS:
        # Comentário explicativo: Define ou atualiza `resultados_atuais[nome]` com o valor calculado à direita.
        resultados_atuais[nome] = benchmark_texto(nome, texto, METADATA_PADRAO)

    # Salva resultado atual para comparação
    # Comentário explicativo: Define ou atualiza `atual` com o valor calculado à direita.
    atual = {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "versao": "atual",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "cenarios": resultados_atuais,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }

    print(f"\n{'':>30} {'Baseline':>12} {'Agora':>12} {'Δ':>10}")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("-" * 66)

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for nome, _, _ in CENARIOS:
        # Comentário explicativo: Define ou atualiza `bl` com o valor calculado à direita.
        bl = baseline["cenarios"][nome]
        # Comentário explicativo: Define ou atualiza `at` com o valor calculado à direita.
        at = resultados_atuais[nome]
        print(f"  [{nome}]")

        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for rotulo, chave in [
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ("Chunks", "chunks.total"),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ("Tempo (s)", "tempo_seg"),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ("Abrev. c/ artefato", "abreviacoes.com_artefato_nn"),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ("Abrev. quebradas", "abreviacoes.no_fim_do_chunk"),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ("Ruido \\n\\n sentenca", "ruido.total_nn_interno"),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ]:
            # Comentário explicativo: Define ou atualiza `v_bl` com o valor calculado à direita.
            v_bl = bl
            # Comentário explicativo: Define ou atualiza `v_at` com o valor calculado à direita.
            v_at = at
            # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
            for k in chave.split("."):
                # Comentário explicativo: Define ou atualiza `v_bl` com o valor calculado à direita.
                v_bl = v_bl[k]
                # Comentário explicativo: Define ou atualiza `v_at` com o valor calculado à direita.
                v_at = v_at[k]
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if isinstance(v_bl, float):
                print(f"  {rotulo:>30} {v_bl:>12.4f} {v_at:>12.4f} {v_at - v_bl:>+10.4f}")
            # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
            else:
                print(f"  {rotulo:>30} {v_bl:>12} {v_at:>12} {v_at - v_bl:>+10}")

        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print()

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return atual


# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if "--compare" in sys.argv:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        comparar_com_baseline()
    # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
    else:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        rodar_benchmark()
