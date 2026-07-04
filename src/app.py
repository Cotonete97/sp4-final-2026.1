# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
"""Interface Streamlit do chatbot RAGnarok."""

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from __future__ import annotations

# Comentário explicativo: Importa o módulo `html` para ser usado neste arquivo.
import html
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from pathlib import Path
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from typing import Any

# Comentário explicativo: Importa o módulo `streamlit` para ser usado neste arquivo.
import streamlit as st


# Comentário explicativo: Define ou atualiza `PROJECT_ROOT` com o valor calculado à direita.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Comentário explicativo: Define ou atualiza `VECTOR_DB_PATH` com o valor calculado à direita.
VECTOR_DB_PATH = PROJECT_ROOT / "data" / "vector_db" / "chroma_data"
# Comentário explicativo: Define ou atualiza `COLLECTION_NAME` com o valor calculado à direita.
COLLECTION_NAME = "ragnarok_knowledge_base"
# Comentário explicativo: Define ou atualiza `DEFAULT_TOP_K` com o valor calculado à direita.
DEFAULT_TOP_K = 10


# Comentário explicativo: Define a função `_inject_styles`, que encapsula uma parte específica da lógica do projeto.
def _inject_styles() -> None:
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown(
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        """
                <style>
        :root { color-scheme: dark; }
        .stApp {
            background: #0b141a;
            color: #e9edef;
        }
        .main .block-container {
            max-width: 100%;
            padding: 1rem 1.25rem 6.75rem;
        }
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            background: transparent;
        }
        .stButton button,
        .stForm button {
            border-radius: 8px;
        }
        .rag-chat-wrap {
            max-width: 820px;
            height: calc(100vh - 2.2rem);
            min-height: 0;
            margin: 0 auto;
            padding: 0;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background: #0b141a;
        }
        .rag-chat-header {
            flex: 0 0 auto;
            z-index: 50;
            padding: 0.95rem 0.95rem 0.8rem;
            background: #202c33;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px 8px 0 0;
        }
        .rag-chat-scroll {
            flex: 1 1 auto;
            min-height: 0;
            height: 100%;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 1rem 0.95rem 7.25rem;
            scroll-behavior: smooth;
            overscroll-behavior: contain;
            scrollbar-gutter: stable;
            scrollbar-width: thin;
            scrollbar-color: rgba(134, 150, 160, 0.55) rgba(255, 255, 255, 0.04);
            background:
                linear-gradient(rgba(11, 20, 26, 0.93), rgba(11, 20, 26, 0.93)),
                repeating-linear-gradient(135deg, rgba(255,255,255,0.03) 0 1px, transparent 1px 18px);
        }
        .rag-chat-scroll::-webkit-scrollbar {
            width: 10px;
        }
        .rag-chat-scroll::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 999px;
        }
        .rag-chat-scroll::-webkit-scrollbar-thumb {
            background: rgba(134, 150, 160, 0.55);
            border-radius: 999px;
            border: 2px solid #0b141a;
        }
        .rag-chat-bottom {
            height: 1px;
            width: 100%;
        }
        .rag-title {
            font-size: 1.02rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.18rem;
            color: #e9edef;
        }
        .rag-subtitle {
            color: #8696a0;
            font-size: 0.82rem;
            line-height: 1.35;
        }
        .rag-empty-state {
            color: #d1d7db;
            font-size: 1.2rem;
            font-weight: 520;
            text-align: center;
            padding: 24vh 1rem 0;
        }
        .rag-side-panel {
            border-radius: 8px;
            padding: 1rem 0.95rem;
            background: rgba(8, 9, 12, 0.72);
            border: 1px solid rgba(255, 255, 255, 0.07);
            position: sticky;
            top: 1rem;
        }
        .rag-topk-panel {
            height: calc(100vh - 2.2rem);
            min-height: 0;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            padding: 0;
            background: #05090c;
            border-color: rgba(255, 255, 255, 0.08);
        }
        .rag-topk-header {
            flex: 0 0 auto;
            padding: 0.95rem 0.95rem 0.75rem;
            background: #0b141a;
            border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        }
        .rag-topk-scroll {
            flex: 1 1 auto;
            min-height: 0;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 0.75rem 0.95rem 0.95rem;
            overscroll-behavior: contain;
            scrollbar-gutter: stable;
            scrollbar-width: thin;
            scrollbar-color: rgba(134, 150, 160, 0.55) rgba(255, 255, 255, 0.04);
        }
        .rag-topk-scroll::-webkit-scrollbar {
            width: 10px;
        }
        .rag-topk-scroll::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 999px;
        }
        .rag-topk-scroll::-webkit-scrollbar-thumb {
            background: rgba(134, 150, 160, 0.55);
            border-radius: 999px;
            border: 2px solid #0b141a;
        }
        .rag-side-title {
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: 0.55rem;
        }
        .rag-side-kicker {
            color: rgba(243, 244, 246, 0.58);
            font-size: 0.82rem;
            line-height: 1.4;
            margin-bottom: 1rem;
        }
        .rag-topk-question {
            color: #cfd6dc;
            font-size: 0.82rem;
            line-height: 1.35;
            margin-top: 0.72rem;
            overflow-wrap: anywhere;
        }
        .rag-topk-empty {
            color: #8696a0;
            font-size: 0.88rem;
            line-height: 1.45;
            padding: 0.85rem 0.1rem;
        }
        .rag-message-row {
            display: flex;
            margin: 0.28rem 0;
            width: 100%;
        }
        .rag-message-row.user { justify-content: flex-end; }
        .rag-message-row.assistant { justify-content: flex-start; }
        .rag-message {
            position: relative;
            max-width: min(78%, 620px);
            line-height: 1.45;
            font-size: 0.96rem;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            padding: 0.52rem 0.72rem 1.22rem;
            box-shadow: 0 1px 0.5px rgba(0, 0, 0, 0.22);
        }
        .rag-message.user {
            background: #005c4b;
            border-radius: 8px 0 8px 8px;
            color: #e9edef;
        }
        .rag-message.user::after {
            content: "";
            position: absolute;
            right: -7px;
            top: 0;
            border-top: 8px solid #005c4b;
            border-right: 8px solid transparent;
        }
        .rag-message.assistant {
            background: #202c33;
            color: #e9edef;
            border-radius: 0 8px 8px 8px;
        }
        .rag-message.assistant::before {
            content: "";
            position: absolute;
            left: -7px;
            top: 0;
            border-top: 8px solid #202c33;
            border-left: 8px solid transparent;
        }
        .rag-message-meta {
            position: absolute;
            right: 0.58rem;
            bottom: 0.32rem;
            color: rgba(233, 237, 239, 0.56);
            font-size: 0.69rem;
            line-height: 1;
        }
        .rag-message.user .rag-message-meta::after {
            content: "  \2713\2713";
            color: #53bdeb;
            letter-spacing: -0.08rem;
        }
        .rag-details {
            margin-top: 0.56rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            padding-top: 0.5rem;
        }
        .rag-details summary {
            cursor: pointer;
            color: #53bdeb;
            font-size: 0.84rem;
            list-style: none;
        }
        .rag-details summary::-webkit-details-marker { display: none; }
        .rag-mini-card,
        .rag-rank-card {
            background: rgba(17, 27, 33, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 8px;
            padding: 0.72rem 0.82rem;
            margin-top: 0.62rem;
        }
        .rag-mini-title {
            color: #f3f4f6;
            font-weight: 750;
            margin-bottom: 0.35rem;
        }
        .rag-mini-body {
            color: rgba(243, 244, 246, 0.78);
            line-height: 1.55;
        }
        .rag-rank-card {
            overflow: hidden;
        }
        .rag-rank-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.45rem;
        }
        .rag-rank-number {
            color: #d7eafe;
            font-weight: 800;
            font-size: 1rem;
        }
        .rag-score {
            background: rgba(15, 58, 93, 0.9);
            color: #d7eafe;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .rag-rank-title {
            color: #f3f4f6;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 0.25rem;
        }
        .rag-rank-source,
        .rag-rank-preview {
            color: rgba(243, 244, 246, 0.72);
            font-size: 0.88rem;
            line-height: 1.45;
        }
        [data-testid="stChatInput"] {
            position: fixed;
            left: 50%;
            right: auto;
            bottom: 1.35rem;
            width: min(760px, calc(100vw - 33rem));
            transform: translateX(-50%);
            z-index: 100;
        }
        [data-testid="stChatInput"] > div {
            border-radius: 22px;
            background: #202123;
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 18px 42px rgba(0, 0, 0, 0.34);
        }
        @media (max-width: 1100px) {
            [data-testid="stChatInput"] {
                width: min(760px, calc(100vw - 2rem));
            }
            .rag-side-panel {
                position: static;
            }
        }
        @media (max-width: 900px) {
            .main .block-container { padding: 1rem 1rem 7rem; }
            [data-testid="stChatInput"] {
                left: 1rem;
                right: 1rem;
                width: auto;
                transform: none;
                bottom: 1rem;
            }
        }
        </style>
        """,
        # Comentário explicativo: Define ou atualiza `unsafe_allow_html` com o valor calculado à direita.
        unsafe_allow_html=True,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `_ensure_state`, que encapsula uma parte específica da lógica do projeto.
def _ensure_state() -> None:
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.setdefault("messages", [])
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.setdefault("last_top_k", [])
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.setdefault("last_question", "")
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.setdefault("pending_prompt", None)


# Comentário explicativo: Aplica um decorador à função abaixo, alterando/adicionando comportamento sem mudar a chamada da função.
@st.cache_resource(show_spinner=False)
# Comentário explicativo: Define a função `get_collection`, que encapsula uma parte específica da lógica do projeto.
def get_collection():
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Retorna a coleção Chroma usada pelo app."""
    # Comentário explicativo: Importa o módulo `chromadb` para ser usado neste arquivo.
    import chromadb
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from chromadb.config import Settings

    # Comentário explicativo: Define ou atualiza `client` com o valor calculado à direita.
    client = chromadb.PersistentClient(
        # Comentário explicativo: Define ou atualiza `path` com o valor calculado à direita.
        path=str(VECTOR_DB_PATH),
        # Comentário explicativo: Define ou atualiza `settings` com o valor calculado à direita.
        settings=Settings(anonymized_telemetry=False),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return client.get_or_create_collection(
        # Comentário explicativo: Define ou atualiza `name` com o valor calculado à direita.
        name=COLLECTION_NAME,
        # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
        metadata={"hnsw:space": "cosine"},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `get_indexed_count`, que encapsula uma parte específica da lógica do projeto.
def get_indexed_count() -> int:
    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return int(get_collection().count())
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except Exception:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return 0


# Comentário explicativo: Define a função `generate_answer`, que encapsula uma parte específica da lógica do projeto.
def generate_answer(question: str) -> dict[str, Any]:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Recupera contexto, registra o top-k e gera a resposta RAG."""
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from llm_integration import generate_rag_response
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from retrieval import retrieve_context

    # Comentário explicativo: Define ou atualiza `context` com o valor calculado à direita.
    context = retrieve_context(question, top_k=DEFAULT_TOP_K)
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.last_top_k = context
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.last_question = question
    
    # Comentário explicativo: Define ou atualiza `llm_config` com o valor calculado à direita.
    llm_config = {}
    # Comentário explicativo: Define ou atualiza `provider` com o valor calculado à direita.
    provider = st.session_state.get("llm_provider")
    # Comentário explicativo: Define ou atualiza `api_key` com o valor calculado à direita.
    api_key = st.session_state.get("api_key")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if provider:
        # Comentário explicativo: Define ou atualiza `llm_config["provider"]` com o valor calculado à direita.
        llm_config["provider"] = provider
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if api_key:
        # Comentário explicativo: Define ou atualiza `llm_config["api_key"]` com o valor calculado à direita.
        llm_config["api_key"] = api_key
        
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return generate_rag_response(question, context, llm_config)


# Comentário explicativo: Define a função `_clear_conversation`, que encapsula uma parte específica da lógica do projeto.
def _clear_conversation() -> None:
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.messages = []
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.last_top_k = []
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.last_question = ""
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.session_state.pending_prompt = None
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.rerun()


# Comentário explicativo: Define a função `render_metrics_panel`, que encapsula uma parte específica da lógica do projeto.
def render_metrics_panel() -> None:
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown('<div class="rag-side-panel">', unsafe_allow_html=True)
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown('<div class="rag-side-title">Métricas</div>', unsafe_allow_html=True)
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown(
        # Comentário explicativo: Define ou atualiza `'<div class` com o valor calculado à direita.
        '<div class="rag-side-kicker">Indicadores da base vetorial do projeto.</div>',
        # Comentário explicativo: Define ou atualiza `unsafe_allow_html` com o valor calculado à direita.
        unsafe_allow_html=True,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.metric("Chunks gerados", get_indexed_count())
    st.caption(f"Coleção: {COLLECTION_NAME}")


    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if st.button("Limpar conversa", use_container_width=True):
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        _clear_conversation()
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown("</div>", unsafe_allow_html=True)

    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown('<div class="rag-side-panel" style="margin-top: 1rem;">', unsafe_allow_html=True)
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown('<div class="rag-side-title">Configuração do LLM</div>', unsafe_allow_html=True)
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.selectbox("Provedor LLM", ["gemini", "deepseek", "local"], key="llm_provider")
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.text_input("Chave da API (Opcional)", type="password", key="api_key", help="Deixe em branco para usar o .env")
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown("</div>", unsafe_allow_html=True)




# Comentário explicativo: Define a função `_score_label`, que encapsula uma parte específica da lógica do projeto.
def _score_label(chunk: dict[str, Any]) -> str:
    # Comentário explicativo: Define ou atualiza `score` com o valor calculado à direita.
    score = chunk.get("score")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if isinstance(score, (int, float)):
        return f"{float(score):.4f}"
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "--"


# Comentário explicativo: Define a função `_topk_card_html`, que encapsula uma parte específica da lógica do projeto.
def _topk_card_html(index: int, chunk: dict[str, Any]) -> str:
    # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
    metadata = chunk.get("metadata", {}) if isinstance(chunk, dict) else {}
    # Comentário explicativo: Define ou atualiza `title` com o valor calculado à direita.
    title = metadata.get("titulo") or "Documento"
    # Comentário explicativo: Define ou atualiza `source` com o valor calculado à direita.
    source = metadata.get("fonte") or "documento"
    # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
    text = (chunk.get("texto", "") if isinstance(chunk, dict) else "").strip()
    # Comentário explicativo: Define ou atualiza `preview` com o valor calculado à direita.
    preview = text[:520] + ("..." if len(text) > 520 else "")

    return f"""
        <div class="rag-rank-card">
            <div class="rag-rank-head">
                <span class="rag-rank-number">#{index}</span>
                <span class="rag-score">score {_score_label(chunk)}</span>
            </div>
            <div class="rag-rank-title">{html.escape(str(title))}</div>
            <div class="rag-rank-source">Origem: {html.escape(str(source))}</div>
            <div class="rag-rank-preview">{html.escape(preview)}</div>
        </div>
    """


# Comentário explicativo: Define a função `render_top_k_panel`, que encapsula uma parte específica da lógica do projeto.
def render_top_k_panel() -> None:
    # Comentário explicativo: Define ou atualiza `top_k` com o valor calculado à direita.
    top_k = st.session_state.get("last_top_k") or []
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not top_k:
        # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
        st.html(
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            """
            <div class="rag-side-panel rag-topk-panel">
                <div class="rag-topk-header">
                    <div class="rag-side-title">Top-k encontrados</div>
                    <div class="rag-side-kicker">Ranking dos chunks retornados pela última pergunta, do melhor score para baixo.</div>
                </div>
                <div class="rag-topk-scroll">
                    <div class="rag-topk-empty">Faça uma pergunta para ver os chunks mais relevantes da base.</div>
                </div>
            </div>
            """
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
        # Comentário explicativo: Encerra a função neste ponto sem retornar um valor explícito.
        return

    # Comentário explicativo: Define ou atualiza `question_html` com o valor calculado à direita.
    question_html = ""
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if st.session_state.get("last_question"):
        question_html = f'<div class="rag-topk-question">Pergunta: {html.escape(str(st.session_state.last_question))}</div>'

    # Comentário explicativo: Define ou atualiza `ranked_chunks` com o valor calculado à direita.
    ranked_chunks = sorted(
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        top_k,
        # Comentário explicativo: Define ou atualiza `key` com o valor calculado à direita.
        key=lambda chunk: float(chunk.get("score", 0.0)) if isinstance(chunk, dict) else 0.0,
        # Comentário explicativo: Define ou atualiza `reverse` com o valor calculado à direita.
        reverse=True,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Define ou atualiza `cards_html` com o valor calculado à direita.
    cards_html = "".join(_topk_card_html(index, chunk) for index, chunk in enumerate(ranked_chunks, start=1))

    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.html(
        f"""
        <div class="rag-side-panel rag-topk-panel">
            <div class="rag-topk-header">
                <div class="rag-side-title">Top-k encontrados</div>
                <div class="rag-side-kicker">Ranking dos chunks retornados pela última pergunta, do melhor score para baixo.</div>
                {question_html}
            </div>
            <div class="rag-topk-scroll">
                {cards_html}
            </div>
        </div>
        """
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
# Comentário explicativo: Define a função `_text_to_html`, que encapsula uma parte específica da lógica do projeto.
def _text_to_html(value: Any) -> str:
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return html.escape(str(value or "")).replace("\n", "<br>")


# Comentário explicativo: Define a função `_response_details_html`, que encapsula uma parte específica da lógica do projeto.
def _response_details_html(response: dict[str, Any] | None) -> str:
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not response:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return ""

    # Comentário explicativo: Define ou atualiza `cards` com o valor calculado à direita.
    cards = []
    # Comentário explicativo: Define ou atualiza `detail_labels` com o valor calculado à direita.
    detail_labels = (
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ("resumo_busca", "Resumo da pesquisa"),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ("resumo_documento", "Sintese do documento"),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ("analise_documento", "Analise do conteudo"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for key, label in detail_labels:
        # Comentário explicativo: Define ou atualiza `value` com o valor calculado à direita.
        value = response.get(key)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if value:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            cards.append(
                # Comentário explicativo: Define ou atualiza `'<div class` com o valor calculado à direita.
                '<div class="rag-mini-card">'
                f'<div class="rag-mini-title">{html.escape(label)}</div>'
                f'<div class="rag-mini-body">{_text_to_html(value)}</div>'
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                '</div>'
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            )
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "".join(cards)


# Comentário explicativo: Define a função `_chat_message_html`, que encapsula uma parte específica da lógica do projeto.
def _chat_message_html(role: str, content: str, response: dict[str, Any] | None = None) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    normalized_role = "user" if role == "user" else "assistant"
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return (
        f'<div class="rag-message-row {normalized_role}">'
        f'<div class="rag-message {normalized_role}">{_text_to_html(content)}</div>'
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        '</div>'
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        + _response_details_html(response if normalized_role == "assistant" else None)
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `render_chat_history`, que encapsula uma parte específica da lógica do projeto.
def render_chat_history() -> None:
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if st.session_state.messages:
        # Comentário explicativo: Define ou atualiza `body` com o valor calculado à direita.
        body = "".join(
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            _chat_message_html(
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                message.get("role", "assistant"),
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                message.get("content", ""),
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                message.get("response"),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            )
            # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
            for message in st.session_state.messages
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
    # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
    else:
        # Comentário explicativo: Define ou atualiza `body` com o valor calculado à direita.
        body = '<div class="rag-empty-state">O que voce quer saber sobre a base?</div>'

    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.markdown(
        f"""
        <div class="rag-chat-wrap">
            <div class="rag-chat-header">
                <div class="rag-title">Chatbot Ragnarok</div>
                <div class="rag-subtitle">Analise de documentos com mini-RAG, resposta fundamentada e foco em PT-BR padrao.</div>
            </div>
            <div class="rag-chat-scroll">
                {body}
                <div class="rag-chat-bottom"></div>
            </div>
        </div>
        """,
        # Comentário explicativo: Define ou atualiza `unsafe_allow_html` com o valor calculado à direita.
        unsafe_allow_html=True,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `_auto_scroll_chat`, que encapsula uma parte específica da lógica do projeto.
def _auto_scroll_chat() -> None:
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.html(
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        """
        <script>
        const scrollChatToBottom = () => {
            const parentDoc = window.parent.document;
            const scrollArea = parentDoc.querySelector(".rag-chat-scroll");
            if (!scrollArea) return;

            scrollArea.scrollTo({
                top: scrollArea.scrollHeight,
                behavior: "smooth"
            });
        };

        const setupAutoScroll = () => {
            const parentDoc = window.parent.document;
            const scrollArea = parentDoc.querySelector(".rag-chat-scroll");
            if (!scrollArea) return;

            if (!scrollArea.dataset.autoScrollReady) {
                const observer = new MutationObserver(() => {
                    window.requestAnimationFrame(scrollChatToBottom);
                });
                observer.observe(scrollArea, { childList: true, subtree: true });
                scrollArea.dataset.autoScrollReady = "true";
            }

            scrollChatToBottom();
        };

        window.setTimeout(setupAutoScroll, 50);
        window.setTimeout(scrollChatToBottom, 250);
        window.setTimeout(scrollChatToBottom, 700);
        </script>
        """,
        # Comentário explicativo: Define ou atualiza `unsafe_allow_javascript` com o valor calculado à direita.
        unsafe_allow_javascript=True,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `render_chat_interface`, que encapsula uma parte específica da lógica do projeto.
def render_chat_interface() -> None:
    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
    st.set_page_config(page_title="Chatbot Ragnarok", page_icon="R", layout="wide")
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    _ensure_state()
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    _inject_styles()

    # Auto-inicialização do banco de dados na primeira execução
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if get_indexed_count() == 0:
        # Comentário explicativo: Abre um recurso com gerenciamento automático de fechamento/liberação ao final do bloco.
        with st.spinner("Inicializando base de conhecimento pela primeira vez (isso pode levar alguns segundos)..."):
            # Comentário explicativo: Importa o módulo `sys` para ser usado neste arquivo.
            import sys
            # Comentário explicativo: Importa o módulo `subprocess` para ser usado neste arquivo.
            import subprocess
            # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
            from pathlib import Path
            # Comentário explicativo: Define ou atualiza `script_path` com o valor calculado à direita.
            script_path = PROJECT_ROOT / "scripts" / "reingest_pdfs.py"
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if script_path.exists():
                # Comentário explicativo: Define ou atualiza `subprocess.run([sys.executable, str(script_path)], cwd` com o valor calculado à direita.
                subprocess.run([sys.executable, str(script_path)], cwd=str(PROJECT_ROOT), capture_output=True)
            # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
            st.rerun()

    # Comentário explicativo: Define ou atualiza `metrics_col, chat_col, top_k_col` com o valor calculado à direita.
    metrics_col, chat_col, top_k_col = st.columns([0.72, 2.25, 0.9], gap="large")

    # Comentário explicativo: Abre um recurso com gerenciamento automático de fechamento/liberação ao final do bloco.
    with metrics_col:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        render_metrics_panel()

    # Comentário explicativo: Abre um recurso com gerenciamento automático de fechamento/liberação ao final do bloco.
    with chat_col:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        render_chat_history()
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        _auto_scroll_chat()

        # Comentário explicativo: Define ou atualiza `pending_prompt` com o valor calculado à direita.
        pending_prompt = st.session_state.get("pending_prompt")
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if pending_prompt:
            # Comentário explicativo: Abre um recurso com gerenciamento automático de fechamento/liberação ao final do bloco.
            with st.spinner("Buscando contexto e gerando resposta..."):
                # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
                try:
                    # Comentário explicativo: Define ou atualiza `response` com o valor calculado à direita.
                    response = generate_answer(pending_prompt)
                # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
                except Exception as exc:
                    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
                    st.session_state.last_top_k = []
                    # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
                    st.session_state.last_question = pending_prompt
                    # Comentário explicativo: Define ou atualiza `response` com o valor calculado à direita.
                    response = {
                        "resposta_gerada": f"Nao foi possivel responder agora: {exc}",
                        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                        "fontes": [],
                        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                        "precisou_triagem": True,
                        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                        "confianca": 0.0,
                    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
                    }
            # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
            st.session_state.messages.append(
                # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
                {
                    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                    "role": "assistant",
                    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                    "content": response["resposta_gerada"],
                    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                    "response": response,
                # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
                }
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            )
            # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
            st.session_state.pending_prompt = None
            # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
            st.rerun()

        # Comentário explicativo: Define ou atualiza `prompt` com o valor calculado à direita.
        prompt = st.chat_input("Pergunte sobre os documentos da base")
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if prompt:
            # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
            st.session_state.pending_prompt = prompt
            # Comentário explicativo: Chama um recurso do Streamlit para montar ou atualizar a interface web.
            st.rerun()

    # Comentário explicativo: Abre um recurso com gerenciamento automático de fechamento/liberação ao final do bloco.
    with top_k_col:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        render_top_k_panel()


# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    render_chat_interface()
