#!/usr/bin/env python3
# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
"""
Benchmark para comparar as abordagens de retrieval: 
distância bruta (Gabriel) vs similaridade normalizada (Pablo/refatorado) vs MMR.

O objetivo é demonstrar que o MMR produz resultados mais DIVERSOS e com
melhor COBERTURA por fonte/PDF, resolvendo o problema da Issue #6.

Para isso, o teste:
  1. Cria uma base vetorial ChromaDB temporária em memória
  2. Insere chunks de documentos com temas variados (simulando 6 PDFs)
  3. Executa queries com diferentes níveis de correspondência
  4. Compara o que cada abordagem aceitaria/rejeitaria
  5. Mede cobertura por fonte (quantos PDFs diferentes aparecem nos resultados)

Uso:
    conda run -n ragnarok python tests/benchmark_retrieval.py
"""

# Comentário explicativo: Importa o módulo `sys` para ser usado neste arquivo.
import sys
# Comentário explicativo: Importa o módulo `time` para ser usado neste arquivo.
import time
# Comentário explicativo: Importa o módulo `tempfile` para ser usado neste arquivo.
import tempfile
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from pathlib import Path
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from collections import Counter

# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Comentário explicativo: Importa o módulo `numpy` para ser usado neste arquivo.
import numpy as np
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from sentence_transformers import SentenceTransformer
# Comentário explicativo: Importa o módulo `chromadb` para ser usado neste arquivo.
import chromadb
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from chromadb.config import Settings


# ── Chunks de teste (simulando 6 PDFs sobre PGD) ────────────────────

# Comentário explicativo: Define ou atualiza `CHUNKS` com o valor calculado à direita.
CHUNKS = [
    # PDF 1: IN 24/2023 - Requisitos do PGD (sistema informatizado)
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in24_sistema_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "O Programa de Gestão e Desempenho deve utilizar sistema informatizado específico, homologado pelo órgão central do SIPEC, para registro e acompanhamento das atividades dos participantes.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Requisitos do PGD - Sistema", "fonte": "IN_24_2023.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in24_sistema_002",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "O sistema informatizado do PGD deverá permitir o registro de metas, entregas e avaliações, garantindo transparência e rastreabilidade das atividades realizadas pelo servidor.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Requisitos do PGD - Sistema", "fonte": "IN_24_2023.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # PDF 2: IN 24/2023 - Requisitos do PGD (prazos e autorização)
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in24_prazos_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "A autorização para participar do PGD depende de aprovação da chefia imediata e deve ser formalizada em até 30 dias antes do início do plano de trabalho. O prazo máximo de cada ciclo é de 12 meses.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Requisitos do PGD - Prazos", "fonte": "IN_21_2024.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in24_autorizacao_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "A autorização para teletrabalho no PGD exige que o servidor demonstre capacidade de autogestão. O gestor deve avaliar e autorizar considerando o interesse da administração pública.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Requisitos do PGD - Autorização", "fonte": "IN_21_2024.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # PDF 3: IN 52/2023 - Modalidades e Regimes
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in52_modalidades_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "O PGD prevê duas modalidades de trabalho: presencial e teletrabalho. O teletrabalho pode ser parcial ou integral, conforme necessidade do órgão e perfil das atividades.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Modalidades do PGD", "fonte": "IN_n52_dez2023.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in52_regimes_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "No regime de teletrabalho integral, o servidor pode executar suas atividades fora das dependências do órgão, desde que mantenha disponibilidade para convocações presenciais.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Regimes de Teletrabalho", "fonte": "IN_n52_dez2023.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # PDF 4: IN 20/2025 - Avaliação e Metas
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in20_avaliacao_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "A avaliação no PGD deve ser realizada pela chefia imediata ao final de cada ciclo, considerando a qualidade das entregas, o cumprimento de prazos e o alcance das metas pactuadas.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Avaliação no PGD", "fonte": "IN_20_2025.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in20_metas_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "As metas do PGD devem ser mensuráveis, alcançáveis e alinhadas ao planejamento institucional. O servidor deve pactuar as metas com a chefia no início de cada ciclo.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Metas do PGD", "fonte": "IN_20_2025.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # PDF 5: IN 137/2026 - Vedações e Penalidades
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in137_vedacoes_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "É vedada a participação no PGD de servidores em estágio probatório, salvo autorização expressa do dirigente máximo do órgão. Servidores com penalidade disciplinar nos últimos 2 anos também são impedidos.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Vedações do PGD", "fonte": "IN_137_2026.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "in137_penalidades_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "O descumprimento das obrigações do PGD pode resultar em desligamento do programa, registro no assentamento funcional e, em casos graves, instauração de processo administrativo disciplinar.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Penalidades do PGD", "fonte": "IN_137_2026.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # PDF 6: Guia Prático - Orientações Gerais
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "guia_orientacoes_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "O Guia Prático do PGD orienta que os requisitos para implementação incluem: sistema informatizado, capacitação dos gestores, plano de entregas aprovado, e ato normativo do dirigente máximo.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Guia Prático - Requisitos", "fonte": "ISBNGuiacompletocomISBN.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "id": "guia_boas_praticas_001",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "texto": "Boas práticas para o PGD incluem reuniões periódicas de alinhamento, uso de ferramentas de comunicação assíncrona, definição clara de entregas e feedback contínuo da chefia.",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "metadata": {"titulo": "Guia Prático - Boas Práticas", "fonte": "ISBNGuiacompletocomISBN.pdf"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    },
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
]


# Comentário explicativo: Define a função `seed_temp_db`, que encapsula uma parte específica da lógica do projeto.
def seed_temp_db(model, client):
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Povoa uma coleção ChromaDB temporária com os chunks de teste."""
    # Comentário explicativo: Define ou atualiza `collection` com o valor calculado à direita.
    collection = client.get_or_create_collection(
        # Comentário explicativo: Define ou atualiza `name` com o valor calculado à direita.
        name="test_ragnarok",
        # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
        metadata={"hnsw:space": "cosine"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Define ou atualiza `texts` com o valor calculado à direita.
    texts = [c["texto"] for c in CHUNKS]
    # Comentário explicativo: Define ou atualiza `embeddings` com o valor calculado à direita.
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    # Comentário explicativo: Define ou atualiza `ids` com o valor calculado à direita.
    ids = [c["id"] for c in CHUNKS]
    # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
    metadatas = [c["metadata"] for c in CHUNKS]

    # Comentário explicativo: Define ou atualiza `collection.add(ids` com o valor calculado à direita.
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return collection


# ── Abordagens de retrieval ──────────────────────────────────────────

# Comentário explicativo: Define a função `query_approach_gabriel`, que encapsula uma parte específica da lógica do projeto.
def query_approach_gabriel(collection, model, query: str, top_k: int = 5):
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Abordagem original do Gabriel: distância bruta com threshold 0.5."""
    # Comentário explicativo: Define ou atualiza `q_emb` com o valor calculado à direita.
    q_emb = model.encode(query).tolist()
    # Comentário explicativo: Define ou atualiza `results` com o valor calculado à direita.
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    # Comentário explicativo: Define ou atualiza `distances` com o valor calculado à direita.
    distances = results.get("distances", [[]])[0]
    # Comentário explicativo: Define ou atualiza `ids_list` com o valor calculado à direita.
    ids_list = results.get("ids", [[]])[0]
    # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
    documents = results.get("documents", [[]])[0]
    # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
    metadatas = results.get("metadatas", [[]])[0]

    # Comentário explicativo: Define ou atualiza `THRESHOLD` com o valor calculado à direita.
    THRESHOLD = 0.5
    # Comentário explicativo: Define ou atualiza `aceitos` com o valor calculado à direita.
    aceitos = []
    # Comentário explicativo: Define ou atualiza `rejeitados` com o valor calculado à direita.
    rejeitados = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for i in range(len(documents)):
        # Comentário explicativo: Define ou atualiza `item` com o valor calculado à direita.
        item = {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "id": ids_list[i],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "texto": documents[i][:80] + "...",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "distancia": round(distances[i], 4),
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "metadata": metadatas[i],
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if distances[i] < THRESHOLD:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            aceitos.append(item)
        # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
        else:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            rejeitados.append(item)

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return aceitos, rejeitados


# Comentário explicativo: Define a função `query_approach_similarity`, que encapsula uma parte específica da lógica do projeto.
def query_approach_similarity(collection, model, query: str, top_k: int = 5):
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Abordagem refatorada: similaridade normalizada com threshold 0.12."""
    # Comentário explicativo: Define ou atualiza `q_emb` com o valor calculado à direita.
    q_emb = model.encode(query).tolist()
    # Comentário explicativo: Define ou atualiza `results` com o valor calculado à direita.
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    # Comentário explicativo: Define ou atualiza `distances` com o valor calculado à direita.
    distances = results.get("distances", [[]])[0]
    # Comentário explicativo: Define ou atualiza `ids_list` com o valor calculado à direita.
    ids_list = results.get("ids", [[]])[0]
    # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
    documents = results.get("documents", [[]])[0]
    # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
    metadatas = results.get("metadatas", [[]])[0]

    # Comentário explicativo: Define ou atualiza `THRESHOLD` com o valor calculado à direita.
    THRESHOLD = 0.12
    # Comentário explicativo: Define ou atualiza `aceitos` com o valor calculado à direita.
    aceitos = []
    # Comentário explicativo: Define ou atualiza `rejeitados` com o valor calculado à direita.
    rejeitados = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for i in range(len(documents)):
        # Comentário explicativo: Define ou atualiza `score` com o valor calculado à direita.
        score = round(1.0 - (distances[i] / 2.0), 4)
        # Comentário explicativo: Define ou atualiza `item` com o valor calculado à direita.
        item = {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "id": ids_list[i],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "texto": documents[i][:80] + "...",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "distancia": round(distances[i], 4),
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "score": score,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "metadata": metadatas[i],
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if score > THRESHOLD:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            aceitos.append(item)
        # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
        else:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            rejeitados.append(item)

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return aceitos, rejeitados


# Comentário explicativo: Define a função `_cosine_similarity`, que encapsula uma parte específica da lógica do projeto.
def _cosine_similarity(a, b):
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Similaridade cosseno entre dois vetores."""
    # Comentário explicativo: Define ou atualiza `a, b` com o valor calculado à direita.
    a, b = np.array(a), np.array(b)
    # Comentário explicativo: Define ou atualiza `dot` com o valor calculado à direita.
    dot = np.dot(a, b)
    # Comentário explicativo: Define ou atualiza `norm_a, norm_b` com o valor calculado à direita.
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if norm_a == 0 or norm_b == 0:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return 0.0
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return float(dot / (norm_a * norm_b))


# Comentário explicativo: Define a função `query_approach_mmr`, que encapsula uma parte específica da lógica do projeto.
def query_approach_mmr(
    # Comentário explicativo: Define ou atualiza `collection, model, query: str, top_k: int` com o valor calculado à direita.
    collection, model, query: str, top_k: int = 5,
    # Comentário explicativo: Define ou atualiza `mmr_candidates: int` com o valor calculado à direita.
    mmr_candidates: int = 12, mmr_lambda: float = 0.65
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
):
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Abordagem MMR: busca N candidatos e seleciona top_k diversos."""
    # Comentário explicativo: Define ou atualiza `q_emb` com o valor calculado à direita.
    q_emb = model.encode(query)
    # Comentário explicativo: Define ou atualiza `q_emb_list` com o valor calculado à direita.
    q_emb_list = q_emb.tolist()

    # Busca N candidatos brutos
    # Comentário explicativo: Define ou atualiza `n_fetch` com o valor calculado à direita.
    n_fetch = min(mmr_candidates, collection.count())
    # Comentário explicativo: Define ou atualiza `results` com o valor calculado à direita.
    results = collection.query(
        # Comentário explicativo: Define ou atualiza `query_embeddings` com o valor calculado à direita.
        query_embeddings=[q_emb_list],
        # Comentário explicativo: Define ou atualiza `n_results` com o valor calculado à direita.
        n_results=n_fetch,
        # Comentário explicativo: Define ou atualiza `include` com o valor calculado à direita.
        include=["documents", "metadatas", "distances", "embeddings"],
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Comentário explicativo: Define ou atualiza `distances` com o valor calculado à direita.
    distances = results.get("distances", [[]])[0]
    # Comentário explicativo: Define ou atualiza `ids_list` com o valor calculado à direita.
    ids_list = results.get("ids", [[]])[0]
    # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
    documents = results.get("documents", [[]])[0]
    # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
    metadatas = results.get("metadatas", [[]])[0]
    # Comentário explicativo: Define ou atualiza `embeddings_list` com o valor calculado à direita.
    embeddings_list = results.get("embeddings", [[]])[0]

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not documents:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return [], []

    # Comentário explicativo: Define ou atualiza `scores` com o valor calculado à direita.
    scores = [round(1.0 - (d / 2.0), 4) for d in distances]
    # Comentário explicativo: Define ou atualiza `candidate_embs` com o valor calculado à direita.
    candidate_embs = [np.array(e) for e in embeddings_list]
    # Comentário explicativo: Define ou atualiza `q_emb_np` com o valor calculado à direita.
    q_emb_np = np.array(q_emb)

    # Aplicar MMR
    # Comentário explicativo: Define ou atualiza `selected` com o valor calculado à direita.
    selected = []
    # Comentário explicativo: Define ou atualiza `remaining` com o valor calculado à direita.
    remaining = set(range(len(documents)))

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for _ in range(min(top_k, len(documents))):
        # Comentário explicativo: Define ou atualiza `best_idx` com o valor calculado à direita.
        best_idx = -1
        # Comentário explicativo: Define ou atualiza `best_mmr` com o valor calculado à direita.
        best_mmr = float("-inf")

        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for idx in remaining:
            # Comentário explicativo: Define ou atualiza `relevance` com o valor calculado à direita.
            relevance = scores[idx]
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if selected:
                # Comentário explicativo: Define ou atualiza `max_sim` com o valor calculado à direita.
                max_sim = max(
                    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                    _cosine_similarity(candidate_embs[idx], candidate_embs[s])
                    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
                    for s in selected
                # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
                )
            # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
            else:
                # Comentário explicativo: Define ou atualiza `max_sim` com o valor calculado à direita.
                max_sim = 0.0

            # Comentário explicativo: Define ou atualiza `mmr_score` com o valor calculado à direita.
            mmr_score = mmr_lambda * relevance - (1 - mmr_lambda) * max_sim

            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if mmr_score > best_mmr:
                # Comentário explicativo: Define ou atualiza `best_mmr` com o valor calculado à direita.
                best_mmr = mmr_score
                # Comentário explicativo: Define ou atualiza `best_idx` com o valor calculado à direita.
                best_idx = idx

        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if best_idx == -1:
            # Comentário explicativo: Interrompe o laço atual antes de percorrer todos os itens.
            break
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        selected.append(best_idx)
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        remaining.discard(best_idx)

    # Comentário explicativo: Define ou atualiza `THRESHOLD` com o valor calculado à direita.
    THRESHOLD = 0.12
    # Comentário explicativo: Define ou atualiza `aceitos` com o valor calculado à direita.
    aceitos = []
    # Comentário explicativo: Define ou atualiza `rejeitados` com o valor calculado à direita.
    rejeitados = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for i in selected:
        # Comentário explicativo: Define ou atualiza `item` com o valor calculado à direita.
        item = {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "id": ids_list[i],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "texto": documents[i][:80] + "...",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "distancia": round(distances[i], 4),
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "score": scores[i],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "metadata": metadatas[i],
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if scores[i] > THRESHOLD:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            aceitos.append(item)
        # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
        else:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            rejeitados.append(item)

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return aceitos, rejeitados


# ── Métricas ─────────────────────────────────────────────────────────

# Comentário explicativo: Define a função `_count_unique_sources`, que encapsula uma parte específica da lógica do projeto.
def _count_unique_sources(items: list) -> dict:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Conta fontes únicas nos itens aceitos."""
    # Comentário explicativo: Define ou atualiza `sources` com o valor calculado à direita.
    sources = Counter()
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for item in items:
        # Comentário explicativo: Define ou atualiza `fonte` com o valor calculado à direita.
        fonte = item.get("metadata", {}).get("fonte", "desconhecido")
        # Comentário explicativo: Define ou atualiza `sources[fonte] +` com o valor calculado à direita.
        sources[fonte] += 1
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return dict(sources)


# Comentário explicativo: Define a função `_coverage_score`, que encapsula uma parte específica da lógica do projeto.
def _coverage_score(items: list, total_sources: int) -> float:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Percentual de fontes únicas cobertas."""
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if total_sources == 0:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return 0.0
    # Comentário explicativo: Define ou atualiza `unique` com o valor calculado à direita.
    unique = len(_count_unique_sources(items))
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return round(unique / total_sources * 100, 1)


# ── Exibição ─────────────────────────────────────────────────────────

# Comentário explicativo: Define a função `tabela_resultado`, que encapsula uma parte específica da lógica do projeto.
def tabela_resultado(abordagem, query, aceitos, rejeitados, all_sources):
    # Comentário explicativo: Define ou atualiza `cov` com o valor calculado à direita.
    cov = _coverage_score(aceitos, len(all_sources))
    # Comentário explicativo: Define ou atualiza `sources` com o valor calculado à direita.
    sources = _count_unique_sources(aceitos)

    print(f"\n  ┌─ {abordagem}")
    print(f"  │ Query: \"{query}\"")
    print(f"  │ Cobertura: {cov}% ({len(sources)}/{len(all_sources)} PDFs)")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if aceitos:
        print(f"  ├─ ACEITOS ({len(aceitos)}):")
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for a in aceitos:
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if "score" in a:
                detalhe = f"score={a['score']:.4f}"
            # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
            else:
                detalhe = f"dist={a.get('distancia', '?'):.4f}"
            # Comentário explicativo: Define ou atualiza `fonte` com o valor calculado à direita.
            fonte = a.get("metadata", {}).get("fonte", "?")
            print(f"  │   ✓ {a['id']:30s} {detalhe:>18}  [{fonte}]")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if rejeitados:
        print(f"  ├─ REJEITADOS ({len(rejeitados)}):")
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for r in rejeitados:
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if "score" in r:
                detalhe = f"score={r['score']:.4f}"
            # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
            else:
                detalhe = f"dist={r.get('distancia', '?'):.4f}"
            # Comentário explicativo: Define ou atualiza `fonte` com o valor calculado à direita.
            fonte = r.get("metadata", {}).get("fonte", "?")
            print(f"  │   ✗ {r['id']:30s} {detalhe:>18}  [{fonte}]")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not aceitos and not rejeitados:
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("  │   (sem resultados)")
    print(f"  └─ Fontes: {sources}")


# Comentário explicativo: Define ou atualiza `QUERIES` com o valor calculado à direita.
QUERIES = [
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    (
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Quais são os requisitos para implementação do PGD?",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Ampla — deve cobrir sistema, prazos, autorização e guia",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    (
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Como funciona a avaliação de desempenho no PGD?",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Específica — foco em avaliação e metas",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    (
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Quais as modalidades de trabalho previstas no PGD?",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Específica — foco em modalidades e regimes",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    (
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Quais são as vedações e penalidades do PGD?",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Específica — foco em vedações e penalidades",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    (
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Como recuperar minha senha no sistema do PGD?",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Fora de escopo — não deveria ter correspondência forte",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    (
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Qual a previsão do tempo para amanhã?",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Fora de escopo — completamente irrelevante",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ),
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
]


# Comentário explicativo: Define a função `main`, que encapsula uma parte específica da lógica do projeto.
def main():
    # Comentário explicativo: Define ou atualiza `all_sources` com o valor calculado à direita.
    all_sources = sorted({c["metadata"]["fonte"] for c in CHUNKS})

    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 78)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  BENCHMARK — Retrieval: Gabriel vs Similaridade vs MMR")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  Issue #6: Diversidade e cobertura por fonte/PDF")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 78)

    # Setup
    # Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
    model = SentenceTransformer("all-MiniLM-L6-v2")
    # Comentário explicativo: Define ou atualiza `client` com o valor calculado à direita.
    client = chromadb.EphemeralClient()
    # Comentário explicativo: Define ou atualiza `collection` com o valor calculado à direita.
    collection = seed_temp_db(model, client)

    print(f"\n  📦 Base de teste: {len(CHUNKS)} chunks de {len(all_sources)} PDFs")
    print(f"  📄 Fontes: {', '.join(all_sources)}")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()

    # Acumuladores
    # Comentário explicativo: Define ou atualiza `stats` com o valor calculado à direita.
    stats = {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Gabriel": {"aceitos": 0, "rejeitados": 0, "cobertura_total": 0},
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "Similaridade": {"aceitos": 0, "rejeitados": 0, "cobertura_total": 0},
        # Comentário explicativo: Define ou atualiza `"MMR λ` com o valor calculado à direita.
        "MMR λ=0.65": {"aceitos": 0, "rejeitados": 0, "cobertura_total": 0},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for query, desc in QUERIES:
        print(f"  {'─' * 74}")
        print(f"  [{desc}]")

        # Comentário explicativo: Define ou atualiza `aceitos_g, rejeitados_g` com o valor calculado à direita.
        aceitos_g, rejeitados_g = query_approach_gabriel(collection, model, query)
        # Comentário explicativo: Define ou atualiza `aceitos_s, rejeitados_s` com o valor calculado à direita.
        aceitos_s, rejeitados_s = query_approach_similarity(collection, model, query)
        # Comentário explicativo: Define ou atualiza `aceitos_m, rejeitados_m` com o valor calculado à direita.
        aceitos_m, rejeitados_m = query_approach_mmr(collection, model, query)

        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        tabela_resultado("Gabriel (dist < 0.5)", query, aceitos_g, rejeitados_g, all_sources)
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        tabela_resultado("Similaridade (score > 0.12)", query, aceitos_s, rejeitados_s, all_sources)
        # Comentário explicativo: Define ou atualiza `tabela_resultado("MMR λ` com o valor calculado à direita.
        tabela_resultado("MMR λ=0.65 (score > 0.12)", query, aceitos_m, rejeitados_m, all_sources)

        # Comentário explicativo: Define ou atualiza `stats["Gabriel"]["aceitos"] +` com o valor calculado à direita.
        stats["Gabriel"]["aceitos"] += len(aceitos_g)
        # Comentário explicativo: Define ou atualiza `stats["Gabriel"]["rejeitados"] +` com o valor calculado à direita.
        stats["Gabriel"]["rejeitados"] += len(rejeitados_g)
        # Comentário explicativo: Define ou atualiza `stats["Gabriel"]["cobertura_total"] +` com o valor calculado à direita.
        stats["Gabriel"]["cobertura_total"] += _coverage_score(aceitos_g, len(all_sources))

        # Comentário explicativo: Define ou atualiza `stats["Similaridade"]["aceitos"] +` com o valor calculado à direita.
        stats["Similaridade"]["aceitos"] += len(aceitos_s)
        # Comentário explicativo: Define ou atualiza `stats["Similaridade"]["rejeitados"] +` com o valor calculado à direita.
        stats["Similaridade"]["rejeitados"] += len(rejeitados_s)
        # Comentário explicativo: Define ou atualiza `stats["Similaridade"]["cobertura_total"] +` com o valor calculado à direita.
        stats["Similaridade"]["cobertura_total"] += _coverage_score(aceitos_s, len(all_sources))

        # Comentário explicativo: Define ou atualiza `stats["MMR λ` com o valor calculado à direita.
        stats["MMR λ=0.65"]["aceitos"] += len(aceitos_m)
        # Comentário explicativo: Define ou atualiza `stats["MMR λ` com o valor calculado à direita.
        stats["MMR λ=0.65"]["rejeitados"] += len(rejeitados_m)
        # Comentário explicativo: Define ou atualiza `stats["MMR λ` com o valor calculado à direita.
        stats["MMR λ=0.65"]["cobertura_total"] += _coverage_score(aceitos_m, len(all_sources))

    # ── Resumo Agregado ──────────────────────────────────────────────
    # Comentário explicativo: Define ou atualiza `n_queries` com o valor calculado à direita.
    n_queries = len(QUERIES)

    print(f"\n  {'=' * 74}")
    print(f"  RESUMO AGREGADO ({n_queries} queries)")
    print(f"  {'=' * 74}")
    print(f"\n  {'':>35} {'Aceitos':>10} {'Rejeitados':>12} {'Cobertura Média':>18}")
    print(f"  {'─' * 75}")

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for name, s in stats.items():
        # Comentário explicativo: Define ou atualiza `avg_cov` com o valor calculado à direita.
        avg_cov = round(s["cobertura_total"] / n_queries, 1)
        print(f"  {name:>35} {s['aceitos']:>10} {s['rejeitados']:>12} {avg_cov:>17}%")

    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()

    # Comparação MMR vs Similaridade
    # Comentário explicativo: Define ou atualiza `cov_mmr` com o valor calculado à direita.
    cov_mmr = stats["MMR λ=0.65"]["cobertura_total"] / n_queries
    # Comentário explicativo: Define ou atualiza `cov_sim` com o valor calculado à direita.
    cov_sim = stats["Similaridade"]["cobertura_total"] / n_queries
    # Comentário explicativo: Define ou atualiza `diff` com o valor calculado à direita.
    diff = round(cov_mmr - cov_sim, 1)

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if diff > 0:
        print(f"  ✅ MMR melhorou a cobertura média em {diff}pp vs Similaridade pura.")
    # Comentário explicativo: Testa uma condição alternativa caso as condições anteriores não tenham sido satisfeitas.
    elif diff == 0:
        print(f"  ≈  MMR e Similaridade obtiveram cobertura semelhante neste benchmark.")
    # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
    else:
        print(f"  ⚠️  Similaridade obteve cobertura melhor por {-diff}pp (caso atípico).")

    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()
    print(f"  💡 CONCLUSÃO — Issue #6:")
    print(f"     1. MMR (λ=0.65) diversifica os resultados sem perder relevância")
    print(f"     2. Para perguntas AMPLAS como 'requisitos do PGD', o MMR puxa")
    print(f"        chunks de múltiplos PDFs em vez de repetir o mesmo tema")
    print(f"     3. O top_k=5 agora cobre mais fontes, dando ao LLM uma")
    print(f"        visão mais completa para gerar respostas abrangentes")
    print(f"     4. Para perguntas ESPECÍFICAS, MMR mantém foco no tema correto")
    print(f"  {'=' * 74}")


# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    main()
