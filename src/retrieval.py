# Tarefa 05: Busca semântica com MMR (Maximal Marginal Relevance)
#
# Resolve Issue #6: retrieve_context com top_k=5 retornava chunks
# apenas por similaridade cosseno, resultando em resultados redundantes
# para perguntas amplas. Agora usamos MMR para diversificar os resultados.

# Comentário explicativo: Importa o módulo `numpy` para ser usado neste arquivo.
import numpy as np
# Comentário explicativo: Importa o módulo `chromadb` para ser usado neste arquivo.
import chromadb

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from model_cache import get_sentence_transformer

# Limiar de similaridade (0 a 1, maior = mais relevante).
# Chunks com score abaixo deste valor são marcados como evidência insuficiente.
# Este valor é CONSISTENTE com o DEFAULT_SCORE_THRESHOLD do llm_integration.py.
# Retrieval deve ser ABRANGENTE (trazer candidatos) — o LLM decide o corte final.
# Comentário explicativo: Define o limiar mínimo de similaridade para marcar evidência insuficiente no retrieval.
REFUSE_THRESHOLD = 0.12

# ── Parâmetros MMR ──────────────────────────────────────────────────
# N candidatos brutos buscados no ChromaDB antes da seleção MMR.
# Comentário explicativo: Define quantos candidatos brutos serão buscados antes do reranqueamento por MMR.
MMR_CANDIDATES = 15

# λ (lambda) controla o trade-off entre relevância e diversidade:
#   λ = 1.0 → 100% relevância (comportamento original, sem diversidade)
#   λ = 0.0 → 100% diversidade (ignora relevância)
#   λ = 0.65 → equilíbrio empírico bom para o domínio PGD
# Comentário explicativo: Define o equilíbrio do MMR entre relevância para a pergunta e diversidade entre chunks.
MMR_LAMBDA = 0.65

# Comentário explicativo: Define ou atualiza `_chroma_client` com o valor calculado à direita.
_chroma_client = None


# Comentário explicativo: Define a função `_get_collection`, que encapsula uma parte específica da lógica do projeto.
def _get_collection():
    # Comentário explicativo: Indica que a variável usada dentro da função é a variável global do módulo.
    global _chroma_client
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if _chroma_client is None:
        # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
        from chromadb.config import Settings
        # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
        from pathlib import Path

        # Comentário explicativo: Define ou atualiza `db_path` com o valor calculado à direita.
        db_path = str(
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            Path(__file__).resolve().parent.parent
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            / "data"
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            / "vector_db"
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            / "chroma_data"
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
        # Comentário explicativo: Define ou atualiza `_chroma_client` com o valor calculado à direita.
        _chroma_client = chromadb.PersistentClient(
            # Comentário explicativo: Define ou atualiza `path` com o valor calculado à direita.
            path=db_path, settings=Settings(anonymized_telemetry=False)
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return _chroma_client.get_collection(name="ragnarok_knowledge_base")
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except Exception:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return None


# Comentário explicativo: Define a função `_cosine_similarity`, que encapsula uma parte específica da lógica do projeto.
def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Similaridade cosseno entre dois vetores normalizados ou não."""
    # Comentário explicativo: Define ou atualiza `dot` com o valor calculado à direita.
    dot = np.dot(a, b)
    # Comentário explicativo: Define ou atualiza `norm_a` com o valor calculado à direita.
    norm_a = np.linalg.norm(a)
    # Comentário explicativo: Define ou atualiza `norm_b` com o valor calculado à direita.
    norm_b = np.linalg.norm(b)
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if norm_a == 0 or norm_b == 0:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return 0.0
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return float(dot / (norm_a * norm_b))


# Comentário explicativo: Define a função `_apply_mmr`, que encapsula uma parte específica da lógica do projeto.
def _apply_mmr(
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    query_embedding: np.ndarray,
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    candidate_embeddings: list[np.ndarray],
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    candidate_scores: list[float],
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    top_k: int,
    # Comentário explicativo: Define ou atualiza `lambda_param: float` com o valor calculado à direita.
    lambda_param: float = MMR_LAMBDA,
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
) -> list[int]:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Seleciona top_k índices dos candidatos usando MMR.

    MMR = λ · sim(query, candidato) - (1-λ) · max(sim(candidato, já_selecionado))

    Isto garante que os resultados selecionados sejam tanto relevantes
    para a query quanto diversos entre si, evitando redundância temática.

    Parâmetros:
        query_embedding: Vetor da pergunta do usuário.
        candidate_embeddings: Lista de vetores dos chunks candidatos.
        candidate_scores: Similaridade normalizada (0-1) de cada candidato com a query.
        top_k: Número de resultados a selecionar.
        lambda_param: Peso de relevância vs diversidade (0-1).

    Retorno:
        Lista de índices selecionados (na ordem de seleção MMR).
    """
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not candidate_embeddings:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return []

    # Comentário explicativo: Define ou atualiza `n` com o valor calculado à direita.
    n = len(candidate_embeddings)
    # Comentário explicativo: Define ou atualiza `top_k` com o valor calculado à direita.
    top_k = min(top_k, n)

    # Comentário explicativo: Define ou atualiza `selected_indices: list[int]` com o valor calculado à direita.
    selected_indices: list[int] = []
    # Comentário explicativo: Define ou atualiza `remaining` com o valor calculado à direita.
    remaining = set(range(n))

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for _ in range(top_k):
        # Comentário explicativo: Define ou atualiza `best_idx` com o valor calculado à direita.
        best_idx = -1
        # Comentário explicativo: Define ou atualiza `best_mmr` com o valor calculado à direita.
        best_mmr = float("-inf")

        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for idx in remaining:
            # Componente de relevância: sim(query, candidato)
            # Comentário explicativo: Define ou atualiza `relevance` com o valor calculado à direita.
            relevance = candidate_scores[idx]

            # Componente de diversidade: max(sim(candidato, já_selecionados))
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if selected_indices:
                # Comentário explicativo: Define ou atualiza `max_sim_to_selected` com o valor calculado à direita.
                max_sim_to_selected = max(
                    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                    _cosine_similarity(
                        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                        candidate_embeddings[idx], candidate_embeddings[sel]
                    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
                    )
                    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
                    for sel in selected_indices
                # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
                )
            # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
            else:
                # Comentário explicativo: Define ou atualiza `max_sim_to_selected` com o valor calculado à direita.
                max_sim_to_selected = 0.0

            # Comentário explicativo: Define ou atualiza `mmr_score` com o valor calculado à direita.
            mmr_score = (
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                lambda_param * relevance
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                - (1 - lambda_param) * max_sim_to_selected
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            )

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
        selected_indices.append(best_idx)
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        remaining.discard(best_idx)

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return selected_indices


# Comentário explicativo: Define a função `retrieve_context`, que encapsula uma parte específica da lógica do projeto.
def retrieve_context(
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    query: str,
    # Comentário explicativo: Define ou atualiza `top_k: int` com o valor calculado à direita.
    top_k: int = 5,
    # Comentário explicativo: Define ou atualiza `use_mmr: bool` com o valor calculado à direita.
    use_mmr: bool = True,
    # Comentário explicativo: Define ou atualiza `mmr_lambda: float` com o valor calculado à direita.
    mmr_lambda: float = MMR_LAMBDA,
    # Comentário explicativo: Define ou atualiza `mmr_candidates: int` com o valor calculado à direita.
    mmr_candidates: int = MMR_CANDIDATES,
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
) -> list:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Recupera os chunks mais relevantes e diversos para a pergunta do usuário.

    Quando ``use_mmr=True`` (padrão), busca ``mmr_candidates`` resultados brutos
    do ChromaDB e aplica MMR para selecionar ``top_k`` chunks que maximizam
    tanto a relevância com a query quanto a diversidade entre si.

    O ChromaDB retorna distância cosseno bruta (0 = idêntico, 2 = oposto).
    Esta função converte para SIMILARIDADE (0 a 1, maior = melhor) e
    expõe o resultado como ``score`` — o padrão que o resto do pipeline
    (llm_integration, interface) espera consumir.

    Parâmetros:
        query (str): Pergunta original do usuário.
        top_k (int): Número de chunks desejados (padrão: 5).
        use_mmr (bool): Se True, aplica MMR para diversificação (padrão: True).
        mmr_lambda (float): Peso relevância vs diversidade (padrão: 0.65).
        mmr_candidates (int): Número de candidatos brutos para MMR (padrão: 15).

    Retorno:
        list: Lista de dicionários, cada um contendo:
            - id: Identificador do chunk
            - texto: Conteúdo textual do chunk
            - metadata: Metadados do documento de origem
            - score: Similaridade normalizada (0 a 1, maior = melhor)
            - score_distancia: Distância cosseno bruta do ChromaDB (debug)
            - evidencia_suficiente: bool
            - refuse_motivo: str (se evidencia_suficiente for False)
            - metodo: "mmr" ou "cosine" (indica qual método selecionou o chunk)
    """
    # Comentário explicativo: Define ou atualiza `collection` com o valor calculado à direita.
    collection = _get_collection()
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if collection is None:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return []

    # Passo A: Embedding da query usando o singleton compartilhado
    # Comentário explicativo: Define ou atualiza `embed_model` com o valor calculado à direita.
    embed_model = get_sentence_transformer()
    # Comentário explicativo: Define ou atualiza `query_embedding` com o valor calculado à direita.
    query_embedding = embed_model.encode(query)
    # Comentário explicativo: Define ou atualiza `query_embedding_list` com o valor calculado à direita.
    query_embedding_list = query_embedding.tolist()

    # Passo B: Busca bruta no banco vetorial
    # Se MMR está ativo, buscamos mais candidatos para ter pool de diversificação
    # Comentário explicativo: Define ou atualiza `n_fetch` com o valor calculado à direita.
    n_fetch = mmr_candidates if use_mmr else top_k
    # Garantir que não pedimos mais do que a collection tem
    # Comentário explicativo: Define ou atualiza `collection_count` com o valor calculado à direita.
    collection_count = collection.count()
    # Comentário explicativo: Define ou atualiza `n_fetch` com o valor calculado à direita.
    n_fetch = min(n_fetch, collection_count) if collection_count > 0 else top_k

    # Comentário explicativo: Define ou atualiza `results` com o valor calculado à direita.
    results = collection.query(
        # Comentário explicativo: Define ou atualiza `query_embeddings` com o valor calculado à direita.
        query_embeddings=[query_embedding_list],
        # Comentário explicativo: Define ou atualiza `n_results` com o valor calculado à direita.
        n_results=n_fetch,
        # Comentário explicativo: Define ou atualiza `include` com o valor calculado à direita.
        include=["documents", "metadatas", "distances", "embeddings"],
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
    documents = results.get("documents", [[]])[0]
    # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
    metadatas = results.get("metadatas", [[]])[0]
    # Comentário explicativo: Define ou atualiza `distances` com o valor calculado à direita.
    distances = results.get("distances", [[]])[0]
    # Comentário explicativo: Define ou atualiza `ids_list` com o valor calculado à direita.
    ids_list = results.get("ids", [[]])[0]
    # Comentário explicativo: Define ou atualiza `embeddings_list` com o valor calculado à direita.
    embeddings_list = results.get("embeddings", [[]])[0]

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not documents:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return []

    # Passo C: Converter distâncias para scores de similaridade
    # Comentário explicativo: Define ou atualiza `scores` com o valor calculado à direita.
    scores = [round(1.0 - (d / 2.0), 4) for d in distances]

    # Passo D: Selecionar índices — MMR ou top-k simples
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if use_mmr and len(documents) > top_k:
        # Converter embeddings para numpy arrays
        # Comentário explicativo: Define ou atualiza `candidate_embs` com o valor calculado à direita.
        candidate_embs = [np.array(e) for e in embeddings_list]
        # Comentário explicativo: Define ou atualiza `query_emb_np` com o valor calculado à direita.
        query_emb_np = np.array(query_embedding)

        # Comentário explicativo: Define ou atualiza `selected_indices` com o valor calculado à direita.
        selected_indices = _apply_mmr(
            # Comentário explicativo: Define ou atualiza `query_embedding` com o valor calculado à direita.
            query_embedding=query_emb_np,
            # Comentário explicativo: Define ou atualiza `candidate_embeddings` com o valor calculado à direita.
            candidate_embeddings=candidate_embs,
            # Comentário explicativo: Define ou atualiza `candidate_scores` com o valor calculado à direita.
            candidate_scores=scores,
            # Comentário explicativo: Define ou atualiza `top_k` com o valor calculado à direita.
            top_k=top_k,
            # Comentário explicativo: Define ou atualiza `lambda_param` com o valor calculado à direita.
            lambda_param=mmr_lambda,
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
        # Comentário explicativo: Define ou atualiza `metodo` com o valor calculado à direita.
        metodo = "mmr"
    # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
    else:
        # Comentário explicativo: Define ou atualiza `selected_indices` com o valor calculado à direita.
        selected_indices = list(range(min(top_k, len(documents))))
        # Comentário explicativo: Define ou atualiza `metodo` com o valor calculado à direita.
        metodo = "cosine"

    # Passo E: Montar resultado final
    # Comentário explicativo: Define ou atualiza `recuperados` com o valor calculado à direita.
    recuperados = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for i in selected_indices:
        # Comentário explicativo: Define ou atualiza `distancia` com o valor calculado à direita.
        distancia = distances[i]
        # Comentário explicativo: Define ou atualiza `score` com o valor calculado à direita.
        score = scores[i]

        # Comentário explicativo: Define ou atualiza `chunk_data` com o valor calculado à direita.
        chunk_data = {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "id": ids_list[i],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "texto": documents[i],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "metadata": metadatas[i],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "score": score,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "score_distancia": round(distancia, 4),
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "metodo": metodo,
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }

        # Lógica de Refuse: marca chunks com similaridade muito baixa
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if score < REFUSE_THRESHOLD:
            # Comentário explicativo: Define ou atualiza `chunk_data["evidencia_suficiente"]` com o valor calculado à direita.
            chunk_data["evidencia_suficiente"] = False
            # Comentário explicativo: Define ou atualiza `chunk_data["refuse_motivo"]` com o valor calculado à direita.
            chunk_data["refuse_motivo"] = (
                f"Similaridade {score:.2f} abaixo do limiar {REFUSE_THRESHOLD}"
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            )
        # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
        else:
            # Comentário explicativo: Define ou atualiza `chunk_data["evidencia_suficiente"]` com o valor calculado à direita.
            chunk_data["evidencia_suficiente"] = True

        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        recuperados.append(chunk_data)

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return recuperados
