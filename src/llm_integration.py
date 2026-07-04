# Tarefa 06: Orquestração do RAG e Integração com LLM

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from __future__ import annotations

# Comentário explicativo: Importa o módulo `os` para ser usado neste arquivo.
import os
# Comentário explicativo: Importa o módulo `re` para ser usado neste arquivo.
import re
# Comentário explicativo: Importa o módulo `unicodedata` para ser usado neste arquivo.
import unicodedata
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from collections import Counter
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from typing import Any, Dict, List, Sequence

# Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
try:
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from dotenv import load_dotenv
# Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
except ImportError:  # pragma: no cover - dependencia configuracional
    # Comentário explicativo: Define ou atualiza `load_dotenv` com o valor calculado à direita.
    load_dotenv = None

# Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
try:
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from langchain_google_genai import ChatGoogleGenerativeAI as _ChatGoogleGenerativeAI
# Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
except ImportError:  # pragma: no cover - permite fallback sem dependencia instalada
    # Comentário explicativo: Define ou atualiza `_ChatGoogleGenerativeAI` com o valor calculado à direita.
    _ChatGoogleGenerativeAI = None

# Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
try:
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from langchain_openai import ChatOpenAI as _ChatOpenAI
# Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
except ImportError:
    # Comentário explicativo: Define ou atualiza `_ChatOpenAI` com o valor calculado à direita.
    _ChatOpenAI = None

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from stopwordsiso import stopwords as _iso_stopwords

# Comentário explicativo: Define o score mínimo final para responder sem acionar triagem humana.
DEFAULT_SCORE_THRESHOLD = 0.50
# Comentário explicativo: Define ou atualiza `MAX_EXCERPT_LENGTH` com o valor calculado à direita.
MAX_EXCERPT_LENGTH = 320
# Comentário explicativo: Define ou atualiza `MAX_SENTENCES_PER_SUMMARY` com o valor calculado à direita.
MAX_SENTENCES_PER_SUMMARY = 8
# Comentário explicativo: Define ou atualiza `MAX_FACTS_PER_GROUP` com o valor calculado à direita.
MAX_FACTS_PER_GROUP = 8
# Comentário explicativo: Define ou atualiza `DEFAULT_GEMINI_MODEL` com o valor calculado à direita.
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
# Comentário explicativo: Define ou atualiza `DEFAULT_DEEPSEEK_MODEL` com o valor calculado à direita.
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
# Comentário explicativo: Define ou atualiza `DEEPSEEK_BASE_URL` com o valor calculado à direita.
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
if load_dotenv is not None:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    load_dotenv()
# Comentário explicativo: Define ou atualiza `DOMAIN_TERMS` com o valor calculado à direita.
DOMAIN_TERMS = {
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "api",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "apis",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "fastapi",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "git",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "github",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "gitlab",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "json",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "moodle",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "pydantic",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "python",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "rest",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    "sql",
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
}


# Comentário explicativo: Define a função `_load_stopwords`, que encapsula uma parte específica da lógica do projeto.
def _load_stopwords() -> set:
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return set(_iso_stopwords("pt")) - DOMAIN_TERMS


# Comentário explicativo: Define ou atualiza `STOPWORDS` com o valor calculado à direita.
STOPWORDS = _load_stopwords()


# Comentário explicativo: Define a função `_gemini_config`, que encapsula uma parte específica da lógica do projeto.
def _gemini_config() -> Dict[str, str]:
    # Comentário explicativo: Define ou atualiza `api_key` com o valor calculado à direita.
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not api_key or "SuaChave" in api_key:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return {}
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "api_key": api_key,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "model": os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# Comentário explicativo: Define a função `_deepseek_config`, que encapsula uma parte específica da lógica do projeto.
def _deepseek_config() -> Dict[str, str]:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Lê configuração do DeepSeek das variáveis de ambiente."""
    # Comentário explicativo: Define ou atualiza `api_key` com o valor calculado à direita.
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not api_key:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return {}
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "api_key": api_key,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "model": os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL).strip() or DEFAULT_DEEPSEEK_MODEL,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# Comentário explicativo: Define a função `_build_provider_prompt`, que encapsula uma parte específica da lógica do projeto.
def _build_provider_prompt(query: str, retrieved_context: Sequence[Dict[str, Any]]) -> str:
    # Comentário explicativo: Define ou atualiza `context_lines` com o valor calculado à direita.
    context_lines = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for index, chunk in enumerate(retrieved_context, start=1):
        # Comentário explicativo: Define ou atualiza `source_ref` com o valor calculado à direita.
        source_ref = _format_source_ref(chunk)
        # Comentário explicativo: Define ou atualiza `source_label` com o valor calculado à direita.
        source_label = _format_source_label(chunk)
        # Comentário explicativo: Define ou atualiza `source_origin` com o valor calculado à direita.
        source_origin = _format_source_origin(chunk)
        # Comentário explicativo: Define ou atualiza `source_page` com o valor calculado à direita.
        source_page = _format_source_page(chunk)
        page_part = f", {source_page}" if source_page else ""
        # Comentário explicativo: Define ou atualiza `excerpt` com o valor calculado à direita.
        excerpt = _format_context_excerpt(chunk, 900)
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        context_lines.append(
            f"[{index}] [Fonte: {source_ref}] {source_label} ({source_origin}{page_part})\n{excerpt}"
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

    # Comentário explicativo: Define ou atualiza `context_block` com o valor calculado à direita.
    context_block = "\n\n".join(context_lines)
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return (
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Você é um assistente especializado exclusivamente no PGD "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "(Programa de Gestão de Desempenho) da Administração Pública Federal. "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Responda em português brasileiro padrão, de forma clara e objetiva. "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Você NÃO possui conhecimento externo, enciclopédico ou de senso comum. "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Você conhece APENAS o conteúdo dos documentos oficiais fornecidos como "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "contexto abaixo (Instruções Normativas e Guia Prático do PGD).\n\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "REGRAS OBRIGATÓRIAS:\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "1. Use exclusivamente o CONTEXTO RECUPERADO para responder.\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "2. CITExA FONTE no formato [Fonte: id] para cada afirmação que fizer.\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "3. Se a pergunta NÃO tiver NENHUMA relação com PGD, responda:\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "   \"Não posso ajudar com isso. Sou especializado apenas em PGD "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "(Programa de Gestão de Desempenho). Por favor, consulte a área responsável.\"\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "4. Se a pergunta for sobre o PGD, mas a resposta não estiver "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "sustentada pelo contexto recuperado abaixo, NÃO invente — diga "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "apenas que não encontrou informação suficiente na base atual "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "para responder com precisão e sugira consultar a norma oficial.\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "5. Não invente números, artigos, parágrafos, prazos, valores ou "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "interpretações que não estejam explicitamente no contexto.\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "6. Se citar um artigo ou parágrafo, informe o número exato conforme "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "a fonte.\n\n"
        f"PERGUNTA DO USUÁRIO:\n{query}\n\n"
        f"CONTEXTO RECUPERADO:\n{context_block}\n\n"
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "RESPOSTA (com fontes citadas):"
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `_call_gemini_llm`, que encapsula uma parte específica da lógica do projeto.
def _call_gemini_llm(query: str, retrieved_context: Sequence[Dict[str, Any]], config_override: dict = None) -> str:
    # Comentário explicativo: Define ou atualiza `config` com o valor calculado à direita.
    config = _gemini_config()
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if config_override:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        config.update({k: v for k, v in config_override.items() if v})
    
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not config or _ChatGoogleGenerativeAI is None:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return ""

    # Comentário explicativo: Define ou atualiza `api_key` com o valor calculado à direita.
    api_key = config.get("api_key", "")
    # Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
    model = config.get("model", DEFAULT_GEMINI_MODEL)
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not api_key:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return ""

    # Comentário explicativo: Define ou atualiza `prompt` com o valor calculado à direita.
    prompt = _build_provider_prompt(query, retrieved_context)
    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Define ou atualiza `llm` com o valor calculado à direita.
        llm = _ChatGoogleGenerativeAI(
            # Comentário explicativo: Define ou atualiza `google_api_key` com o valor calculado à direita.
            google_api_key=api_key,
            # Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
            model=model,
            # Comentário explicativo: Define ou atualiza `temperature` com o valor calculado à direita.
            temperature=0.1,
            # Comentário explicativo: Define ou atualiza `max_output_tokens` com o valor calculado à direita.
            max_output_tokens=900,
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
        # Comentário explicativo: Define ou atualiza `response` com o valor calculado à direita.
        response = llm.invoke([
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            (
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "system",
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "Você é um assistente especializado exclusivamente em PGD "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "(Programa de Gestão de Desempenho). Você NÃO possui conhecimento "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "externo. Responda SOMENTE com base no contexto. Se a resposta não "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "estiver no contexto, avise o usuário sem inventar. Sempre cite "
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "a fonte no formato [Fonte: id]. Não invente artigos, prazos ou valores.",
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ("human", prompt),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ])
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return str(getattr(response, "content", response)).strip()
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except Exception:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return ""


# Comentário explicativo: Define a função `_call_deepseek_llm`, que encapsula uma parte específica da lógica do projeto.
def _call_deepseek_llm(query: str, retrieved_context: Sequence[Dict[str, Any]], config_override: dict = None) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Chama o DeepSeek via API compatível com OpenAI."""
    # Comentário explicativo: Define ou atualiza `config` com o valor calculado à direita.
    config = _deepseek_config()
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if config_override:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        config.update({k: v for k, v in config_override.items() if v})
        
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not config or _ChatOpenAI is None:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return ""

    # Comentário explicativo: Define ou atualiza `api_key` com o valor calculado à direita.
    api_key = config.get("api_key", "")
    # Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
    model = config.get("model", DEFAULT_DEEPSEEK_MODEL)
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not api_key:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return ""

    # Comentário explicativo: Define ou atualiza `prompt` com o valor calculado à direita.
    prompt = _build_provider_prompt(query, retrieved_context)
    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Define ou atualiza `llm` com o valor calculado à direita.
        llm = _ChatOpenAI(
            # Comentário explicativo: Define ou atualiza `api_key` com o valor calculado à direita.
            api_key=api_key,
            # Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
            model=model,
            # Comentário explicativo: Define ou atualiza `base_url` com o valor calculado à direita.
            base_url=DEEPSEEK_BASE_URL,
            # Comentário explicativo: Define ou atualiza `temperature` com o valor calculado à direita.
            temperature=0.1,
            # Comentário explicativo: Define ou atualiza `max_tokens` com o valor calculado à direita.
            max_tokens=900,
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
        # Comentário explicativo: Define ou atualiza `response` com o valor calculado à direita.
        response = llm.invoke([
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            (
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "system",
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "Você é um assistente especializado exclusivamente em PGD "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "(Programa de Gestão de Desempenho). Você NÃO possui conhecimento "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "externo. Responda SOMENTE com base no contexto. Se a resposta não "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "estiver no contexto, avise o usuário sem inventar. Sempre cite "
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "a fonte no formato [Fonte: id]. Não invente artigos, prazos ou valores.",
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ("human", prompt),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ])
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return str(getattr(response, "content", response)).strip()
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except Exception:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return ""


# Comentário explicativo: Define a função `_call_configured_llm`, que encapsula uma parte específica da lógica do projeto.
def _call_configured_llm(query: str, retrieved_context: Sequence[Dict[str, Any]], llm_config: dict = None) -> tuple[str, str]:
    # Comentário explicativo: Define ou atualiza `provider` com o valor calculado à direita.
    provider = (llm_config or {}).get("provider", "")

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if provider == "deepseek" or (not provider and _deepseek_config()):
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        deepseek_config = llm_config if provider == "deepseek" else None
        # Comentário explicativo: Define ou atualiza `deepseek_answer` com o valor calculado à direita.
        deepseek_answer = _call_deepseek_llm(query, retrieved_context, deepseek_config)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if deepseek_answer:
            # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
            return deepseek_answer, "deepseek"

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if provider == "gemini" or (not provider and _gemini_config()):
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        gemini_config = llm_config if provider == "gemini" else None
        # Comentário explicativo: Define ou atualiza `gemini_answer` com o valor calculado à direita.
        gemini_answer = _call_gemini_llm(query, retrieved_context, gemini_config)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if gemini_answer:
            # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
            return gemini_answer, "gemini"

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "", "local"

# Comentário explicativo: Define ou atualiza `WORD_RE` com o valor calculado à direita.
WORD_RE = re.compile(r"\b[\wÀ-ÿ]+\b", re.UNICODE)
# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
# Comentário explicativo: Define ou atualiza `DATE_RE` com o valor calculado à direita.
DATE_RE = re.compile(r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\b")
# Comentário explicativo: Define ou atualiza `MONEY_RE` com o valor calculado à direita.
MONEY_RE = re.compile(r"(?:R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\$\s?\d+(?:\.\d{2})?)")
# Comentário explicativo: Define ou atualiza `PERCENT_RE` com o valor calculado à direita.
PERCENT_RE = re.compile(r"\b\d+(?:,\d+)?%\b")
# Comentário explicativo: Define ou atualiza `NUMBER_RE` com o valor calculado à direita.
NUMBER_RE = re.compile(r"\b\d+(?:[\.,]\d+)?\b")
# Comentário explicativo: Define ou atualiza `ACTION_RE` com o valor calculado à direita.
ACTION_RE = re.compile(
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    r"\b(deve|deverá|devera|precisa|necessita|solicita|solicitado|aprovado|indeferido|autorizado|proibido|prazo|vencimento|valor|data|responsável|responsavel|obrigatório|obrigatorio)\b",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    re.IGNORECASE,
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
)


# Comentário explicativo: Define a função `_normalize_text`, que encapsula uma parte específica da lógica do projeto.
def _normalize_text(text: str) -> str:
    # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
    text = unicodedata.normalize("NFKD", text or "")
    # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
    text = "".join(char for char in text if not unicodedata.combining(char))
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return re.sub(r"\s+", " ", text).strip()


# Comentário explicativo: Define a função `_tokenize`, que encapsula uma parte específica da lógica do projeto.
def _tokenize(text: str) -> List[str]:
    # Comentário explicativo: Define ou atualiza `normalized` com o valor calculado à direita.
    normalized = _normalize_text(text).lower()
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return [token for token in WORD_RE.findall(normalized) if token and token not in STOPWORDS]


# Comentário explicativo: Define a função `_split_sentences`, que encapsula uma parte específica da lógica do projeto.
def _split_sentences(text: str) -> List[str]:
    # Comentário explicativo: Define ou atualiza `normalized` com o valor calculado à direita.
    normalized = _normalize_text(text)
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not normalized:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return []
    # Comentário explicativo: Define ou atualiza `sentences` com o valor calculado à direita.
    sentences = [sentence.strip() for sentence in SENTENCE_RE.split(normalized) if sentence.strip()]
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if sentences:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return sentences
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return [normalized]


# Comentário explicativo: Define a função `_format_source_label`, que encapsula uma parte específica da lógica do projeto.
def _format_source_label(chunk: Dict[str, Any]) -> str:
    # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
    metadata = chunk.get("metadata", {})
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if isinstance(metadata, dict):
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return metadata.get("titulo") or "Documento"
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "Documento"


# Comentário explicativo: Define a função `_format_source_ref`, que encapsula uma parte específica da lógica do projeto.
def _format_source_ref(chunk: Dict[str, Any]) -> str:
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return str(chunk.get("id") or chunk.get("doc_id") or _format_source_label(chunk))


# Comentário explicativo: Define a função `_format_source_origin`, que encapsula uma parte específica da lógica do projeto.
def _format_source_origin(chunk: Dict[str, Any]) -> str:
    # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
    metadata = chunk.get("metadata", {})
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if isinstance(metadata, dict):
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return metadata.get("fonte") or "documento"
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "documento"


# Comentário explicativo: Define a função `_format_source_page`, que encapsula uma parte específica da lógica do projeto.
def _format_source_page(chunk: Dict[str, Any]) -> str:
    # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
    metadata = chunk.get("metadata", {})
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if isinstance(metadata, dict):
        # Comentário explicativo: Define ou atualiza `page_number` com o valor calculado à direita.
        page_number = metadata.get("page_number")
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if page_number is not None:
            return f"página {page_number}"
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return ""


# Comentário explicativo: Define a função `_format_score`, que encapsula uma parte específica da lógica do projeto.
def _format_score(chunk: Dict[str, Any]) -> str:
    # Comentário explicativo: Define ou atualiza `score` com o valor calculado à direita.
    score = chunk.get("score")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if isinstance(score, (int, float)):
        return f"{float(score):.4f}"
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "n/d"


# Comentário explicativo: Define a função `_format_context_excerpt`, que encapsula uma parte específica da lógica do projeto.
def _format_context_excerpt(chunk: Dict[str, Any], max_length: int = MAX_EXCERPT_LENGTH) -> str:
    # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
    text = (chunk.get("texto", "") or "").strip()
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if len(text) <= max_length:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return text
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return text[: max_length - 3].rstrip() + "..."


# Comentário explicativo: Define a função `_collect_relevant_terms`, que encapsula uma parte específica da lógica do projeto.
def _collect_relevant_terms(query: str, retrieved_context: Sequence[Dict[str, Any]]) -> List[str]:
    # Comentário explicativo: Define ou atualiza `query_terms` com o valor calculado à direita.
    query_terms = set(_tokenize(query))
    # Comentário explicativo: Define ou atualiza `counter: Counter[str]` com o valor calculado à direita.
    counter: Counter[str] = Counter()
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in retrieved_context:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        counter.update(_tokenize(str(chunk.get("texto", ""))))
        # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
        metadata = chunk.get("metadata", {})
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if isinstance(metadata, dict):
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            counter.update(_tokenize(str(metadata.get("titulo", ""))))
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            counter.update(_tokenize(str(metadata.get("fonte", ""))))
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        counter.update(chunk.get("match_terms", []))
    # Comentário explicativo: Define ou atualiza `terms` com o valor calculado à direita.
    terms = [term for term, _count in counter.most_common() if term not in query_terms and len(term) > 2 and not term.isdigit()]
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return terms[:6]


# Comentário explicativo: Define a função `_summarize_chunks`, que encapsula uma parte específica da lógica do projeto.
def _summarize_chunks(retrieved_context: Sequence[Dict[str, Any]]) -> str:
    # Comentário explicativo: Define ou atualiza `sentences: List[str]` com o valor calculado à direita.
    sentences: List[str] = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in retrieved_context:
        # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
        text = (chunk.get("texto", "") or "").strip()
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not text:
            # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
            continue
        # Comentário explicativo: Define ou atualiza `chunk_sentences` com o valor calculado à direita.
        chunk_sentences = _split_sentences(text)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if chunk_sentences:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            sentences.append(chunk_sentences[0])
    # Comentário explicativo: Define ou atualiza `unique_sentences` com o valor calculado à direita.
    unique_sentences = []
    # Comentário explicativo: Define ou atualiza `seen` com o valor calculado à direita.
    seen = set()
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for sentence in sentences:
        # Comentário explicativo: Define ou atualiza `normalized` com o valor calculado à direita.
        normalized = sentence.lower()
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if normalized in seen:
            # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
            continue
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        seen.add(normalized)
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        unique_sentences.append(sentence)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if len(unique_sentences) >= MAX_SENTENCES_PER_SUMMARY:
            # Comentário explicativo: Interrompe o laço atual antes de percorrer todos os itens.
            break
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return " ".join(unique_sentences)


# Comentário explicativo: Define a função `_collect_document_text`, que encapsula uma parte específica da lógica do projeto.
def _collect_document_text(retrieved_context: Sequence[Dict[str, Any]]) -> str:
    # Comentário explicativo: Define ou atualiza `parts: List[str]` com o valor calculado à direita.
    parts: List[str] = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in retrieved_context:
        # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
        text = (chunk.get("texto", "") or "").strip()
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if text:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            parts.append(text)
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "\n".join(parts)


# Comentário explicativo: Define a função `_extract_key_facts`, que encapsula uma parte específica da lógica do projeto.
def _extract_key_facts(text: str) -> Dict[str, List[str]]:
    # Comentário explicativo: Define ou atualiza `facts` com o valor calculado à direita.
    facts = {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "dates": list(dict.fromkeys(DATE_RE.findall(text)))[:MAX_FACTS_PER_GROUP],
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "money": list(dict.fromkeys(MONEY_RE.findall(text)))[:MAX_FACTS_PER_GROUP],
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "percentages": list(dict.fromkeys(PERCENT_RE.findall(text)))[:MAX_FACTS_PER_GROUP],
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "numbers": list(dict.fromkeys(NUMBER_RE.findall(text)))[:MAX_FACTS_PER_GROUP],
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }
    # Comentário explicativo: Define ou atualiza `action_sentences` com o valor calculado à direita.
    action_sentences = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for sentence in _split_sentences(text):
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if ACTION_RE.search(sentence):
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            action_sentences.append(sentence.strip())
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if len(action_sentences) >= MAX_FACTS_PER_GROUP:
            # Comentário explicativo: Interrompe o laço atual antes de percorrer todos os itens.
            break
    # Comentário explicativo: Define ou atualiza `facts["actions"]` com o valor calculado à direita.
    facts["actions"] = action_sentences
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return facts


# Comentário explicativo: Define ou atualiza `BULLET_RE` com o valor calculado à direita.
BULLET_RE = re.compile(r"^\s*(?:[\u25cf\u2022*\-]|\d+[.)])\s+")


# Comentário explicativo: Define a função `_clean_list_item`, que encapsula uma parte específica da lógica do projeto.
def _clean_list_item(line: str) -> str:
    # Comentário explicativo: Define ou atualiza `line` com o valor calculado à direita.
    line = re.sub(r"\s+", " ", line or "").strip()
    # Comentário explicativo: Define ou atualiza `line` com o valor calculado à direita.
    line = BULLET_RE.sub("", line).strip()
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return line.rstrip(";.")


# Comentário explicativo: Define a função `_extract_section_insights`, que encapsula uma parte específica da lógica do projeto.
def _extract_section_insights(retrieved_context: Sequence[Dict[str, Any]]) -> List[str]:
    # Comentário explicativo: Define ou atualiza `sections: Dict[str, Dict[str, Any]]` com o valor calculado à direita.
    sections: Dict[str, Dict[str, Any]] = {}
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in retrieved_context:
        # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
        metadata = chunk.get("metadata", {})
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if isinstance(metadata, dict):
            # Comentário explicativo: Define ou atualiza `section` com o valor calculado à direita.
            section = metadata.get("section_path") or metadata.get("section_title") or "Documento"
        # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
        else:
            # Comentário explicativo: Define ou atualiza `section` com o valor calculado à direita.
            section = "Documento"
        # Comentário explicativo: Define ou atualiza `bucket` com o valor calculado à direita.
        bucket = sections.setdefault(section, {"text": [], "items": []})
        # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
        text = (chunk.get("texto", "") or "").strip()
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not text:
            # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
            continue
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        bucket["text"].append(text)
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for raw_line in text.splitlines():
            # Comentário explicativo: Define ou atualiza `item` com o valor calculado à direita.
            item = _clean_list_item(raw_line)
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if not item or len(item) < 4:
                # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
                continue
            # Comentário explicativo: Define ou atualiza `normalized` com o valor calculado à direita.
            normalized = _normalize_text(item).lower()
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if normalized == _normalize_text(section).lower():
                # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
                continue
            # Comentário explicativo: Define ou atualiza `is_bullet` com o valor calculado à direita.
            is_bullet = bool(BULLET_RE.match(raw_line))
            # Comentário explicativo: Define ou atualiza `is_relevant_line` com o valor calculado à direita.
            is_relevant_line = is_bullet or ACTION_RE.search(item) or normalized in {
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "python",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "fastapi",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "pydantic",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "sql",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "git",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "github",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "gitlab",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "rest api",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "json",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "moodle",
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            }
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if is_relevant_line and item not in bucket["items"]:
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                bucket["items"].append(item)

    # Comentário explicativo: Define ou atualiza `insights: List[str]` com o valor calculado à direita.
    insights: List[str] = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for section, data in sections.items():
        # Comentário explicativo: Define ou atualiza `items` com o valor calculado à direita.
        items = data["items"][:6]
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not items:
            # Comentário explicativo: Define ou atualiza `combined` com o valor calculado à direita.
            combined = " ".join(data["text"])
            # Comentário explicativo: Define ou atualiza `items` com o valor calculado à direita.
            items = _split_sentences(combined)[:2]
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if items:
            insights.append(f"{section}: " + "; ".join(items))
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if len(insights) >= 8:
            # Comentário explicativo: Interrompe o laço atual antes de percorrer todos os itens.
            break
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return insights


# Comentário explicativo: Define a função `_select_supporting_sentences`, que encapsula uma parte específica da lógica do projeto.
def _select_supporting_sentences(query: str, retrieved_context: Sequence[Dict[str, Any]]) -> List[str]:
    # Comentário explicativo: Define ou atualiza `query_terms` com o valor calculado à direita.
    query_terms = set(_tokenize(query))
    # Comentário explicativo: Define ou atualiza `sentences: List[str]` com o valor calculado à direita.
    sentences: List[str] = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in retrieved_context:
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for sentence in _split_sentences(chunk.get("texto", "")):
            # Comentário explicativo: Define ou atualiza `sentence_terms` com o valor calculado à direita.
            sentence_terms = set(_tokenize(sentence))
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if not sentence_terms:
                # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
                continue
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if query_terms & sentence_terms or ACTION_RE.search(sentence):
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                sentences.append(sentence)
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if len(sentences) >= MAX_SENTENCES_PER_SUMMARY:
                # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
                return sentences
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return sentences


# Comentário explicativo: Define a função `_build_document_summary`, que encapsula uma parte específica da lógica do projeto.
def _build_document_summary(query: str, retrieved_context: Sequence[Dict[str, Any]]) -> str:
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not retrieved_context:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return "Não encontrei um resumo confiável porque não havia trechos suficientes para análise."

    # Comentário explicativo: Define ou atualiza `top_titles: List[str]` com o valor calculado à direita.
    top_titles: List[str] = []
    # Comentário explicativo: Define ou atualiza `pages: List[str]` com o valor calculado à direita.
    pages: List[str] = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in retrieved_context[:4]:
        # Comentário explicativo: Define ou atualiza `title` com o valor calculado à direita.
        title = _format_source_label(chunk)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if title not in top_titles:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            top_titles.append(title)
        # Comentário explicativo: Define ou atualiza `page` com o valor calculado à direita.
        page = _format_source_page(chunk)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if page and page not in pages:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            pages.append(page)

    # Comentário explicativo: Define ou atualiza `terms` com o valor calculado à direita.
    terms = _collect_relevant_terms(query, retrieved_context)
    # Comentário explicativo: Define ou atualiza `summary_text` com o valor calculado à direita.
    summary_text = _summarize_chunks(retrieved_context)
    # Comentário explicativo: Define ou atualiza `facts` com o valor calculado à direita.
    facts = _extract_key_facts(_collect_document_text(retrieved_context))
    # Comentário explicativo: Define ou atualiza `section_insights` com o valor calculado à direita.
    section_insights = _extract_section_insights(retrieved_context)
    # Comentário explicativo: Define ou atualiza `title_block` com o valor calculado à direita.
    title_block = ", ".join(top_titles)
    # Comentário explicativo: Define ou atualiza `topic_block` com o valor calculado à direita.
    topic_block = ", ".join(terms) if terms else "o conteúdo principal do documento"
    page_block = f" Páginas observadas: {', '.join(pages)}." if pages else ""

    # Comentário explicativo: Define ou atualiza `fact_parts` com o valor calculado à direita.
    fact_parts = []
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["dates"]:
        fact_parts.append(f"datas encontradas: {', '.join(facts['dates'])}")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["money"]:
        fact_parts.append(f"valores encontrados: {', '.join(facts['money'])}")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["percentages"]:
        fact_parts.append(f"percentuais encontrados: {', '.join(facts['percentages'])}")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["actions"]:
        fact_parts.append(f"trechos de ação/decisão: {' | '.join(facts['actions'])}")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if section_insights:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        fact_parts.append("estrutura do documento: " + " | ".join(section_insights[:4]))

    analytical_block = f" Informações identificadas: {'; '.join(fact_parts)}." if fact_parts else ""

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if summary_text:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return (
            f"Os trechos mais relevantes vêm de {title_block}. "
            f"Pelos termos encontrados, o documento gira em torno de {topic_block}.{page_block}"
            f" Resumo do que foi localizado: {summary_text}.{analytical_block}"
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return (
        f"Os trechos mais relevantes vêm de {title_block}. "
        f"Pelos termos encontrados, o documento gira em torno de {topic_block}.{page_block}{analytical_block}"
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `_build_search_overview`, que encapsula uma parte específica da lógica do projeto.
def _build_search_overview(query: str, retrieved_context: Sequence[Dict[str, Any]]) -> str:
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not retrieved_context:
        return f"Busquei por '{query}' na base de conhecimento, mas não encontrei evidências suficientes."

    # Comentário explicativo: Define ou atualiza `sources` com o valor calculado à direita.
    sources = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in retrieved_context[:5]:
        # Comentário explicativo: Define ou atualiza `label` com o valor calculado à direita.
        label = _format_source_label(chunk)
        # Comentário explicativo: Define ou atualiza `source_ref` com o valor calculado à direita.
        source_ref = _format_source_ref(chunk)
        # Comentário explicativo: Define ou atualiza `source` com o valor calculado à direita.
        source = _format_source_origin(chunk)
        # Comentário explicativo: Define ou atualiza `page` com o valor calculado à direita.
        page = _format_source_page(chunk)
        # Comentário explicativo: Define ou atualiza `score` com o valor calculado à direita.
        score = _format_score(chunk)
        # Comentário explicativo: Define ou atualiza `match_terms` com o valor calculado à direita.
        match_terms = chunk.get("match_terms") or []
        page_part = f", {page}" if page else ""
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if match_terms:
            sources.append(f"[Fonte: {source_ref}] {label} ({source}{page_part}, score {score}, termos: {', '.join(match_terms[:4])})")
        # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
        else:
            sources.append(f"[Fonte: {source_ref}] {label} ({source}{page_part}, score {score})")

    # Comentário explicativo: Define ou atualiza `source_block` com o valor calculado à direita.
    source_block = "; ".join(sources)
    return f"Busquei a pergunta '{query}' priorizando os trechos mais próximos semanticamente e, em seguida, refinei com termos em comum. Fontes priorizadas: {source_block}."


# Comentário explicativo: Define a função `_build_analytical_answer`, que encapsula uma parte específica da lógica do projeto.
def _build_analytical_answer(query: str, retrieved_context: List[Dict[str, Any]], llm_config: dict = None) -> Dict[str, str]:
    # Comentário explicativo: Define ou atualiza `search_overview` com o valor calculado à direita.
    search_overview = _build_search_overview(query, retrieved_context)
    # Comentário explicativo: Define ou atualiza `document_summary` com o valor calculado à direita.
    document_summary = _build_document_summary(query, retrieved_context)
    # Comentário explicativo: Define ou atualiza `supporting_sentences` com o valor calculado à direita.
    supporting_sentences = _select_supporting_sentences(query, retrieved_context)
    # Comentário explicativo: Define ou atualiza `facts` com o valor calculado à direita.
    facts = _extract_key_facts(_collect_document_text(retrieved_context))
    # Comentário explicativo: Define ou atualiza `section_insights` com o valor calculado à direita.
    section_insights = _extract_section_insights(retrieved_context)
    # Comentário explicativo: Define ou atualiza `llm_answer, llm_provider` com o valor calculado à direita.
    llm_answer, llm_provider = _call_configured_llm(query, retrieved_context, llm_config)

    # Comentário explicativo: Define ou atualiza `source_lines` com o valor calculado à direita.
    source_lines = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for index, chunk in enumerate(retrieved_context, start=1):
        # Comentário explicativo: Define ou atualiza `source_label` com o valor calculado à direita.
        source_label = _format_source_label(chunk)
        # Comentário explicativo: Define ou atualiza `source_ref` com o valor calculado à direita.
        source_ref = _format_source_ref(chunk)
        # Comentário explicativo: Define ou atualiza `source_origin` com o valor calculado à direita.
        source_origin = _format_source_origin(chunk)
        # Comentário explicativo: Define ou atualiza `source_page` com o valor calculado à direita.
        source_page = _format_source_page(chunk)
        # Comentário explicativo: Define ou atualiza `score_label` com o valor calculado à direita.
        score_label = _format_score(chunk)
        # Comentário explicativo: Define ou atualiza `excerpt` com o valor calculado à direita.
        excerpt = _format_context_excerpt(chunk)
        # Comentário explicativo: Define ou atualiza `match_terms` com o valor calculado à direita.
        match_terms = chunk.get("match_terms") or []
        # Comentário explicativo: Define ou atualiza `title_match_terms` com o valor calculado à direita.
        title_match_terms = chunk.get("title_match_terms") or []
        # Comentário explicativo: Define ou atualiza `detail_bits` com o valor calculado à direita.
        detail_bits = []
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if source_page:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            detail_bits.append(source_page)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if match_terms:
            detail_bits.append(f"termos recuperados: {', '.join(match_terms[:5])}")
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if title_match_terms:
            detail_bits.append(f"correspondência no título: {', '.join(title_match_terms[:3])}")
        detail_block = f" | {'; '.join(detail_bits)}" if detail_bits else ""
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        source_lines.append(
            f"- [Fonte: {source_ref}] {source_label} ({source_origin}{detail_block}, score {score_label})"
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

    # Comentário explicativo: Define ou atualiza `facts_block` com o valor calculado à direita.
    facts_block = []
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["dates"]:
        facts_block.append(f"Datas/prazos: {', '.join(facts['dates'])}")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["money"]:
        facts_block.append(f"Valores: {', '.join(facts['money'])}")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["percentages"]:
        facts_block.append(f"Percentuais: {', '.join(facts['percentages'])}")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if facts["actions"]:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        facts_block.append("Ações/decisões: " + " | ".join(facts["actions"]))
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if section_insights:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        facts_block.append("Análise por seções: " + " | ".join(section_insights))
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not facts_block:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        facts_block.append("Não identifiquei datas, valores ou ações explícitas nos trechos recuperados.")

    # ── resposta_gerada concisa ──
    # Comentário explicativo: Define ou atualiza `answer_parts` com o valor calculado à direita.
    answer_parts = []
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if llm_answer:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        answer_parts.append(llm_answer)
    # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
    else:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        answer_parts.append("⚠️ **MODO LOCAL ATIVADO (SEM LLM)**: Nenhuma chave de API de Inteligência Artificial foi detectada nas suas variáveis de ambiente ou arquivo `.env`. Estou exibindo apenas a recuperação bruta dos trechos.\n")
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        answer_parts.append(search_overview)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if supporting_sentences:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            answer_parts.append("")
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            answer_parts.append(" || ".join(supporting_sentences))

    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    answer_parts.append("")
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    answer_parts.append("---")
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    answer_parts.append("**Fontes consultadas:**")
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    answer_parts.extend(source_lines)
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    answer_parts.append("")
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    answer_parts.append("---")
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    answer_parts.append("*Resposta construída com base exclusivamente nos trechos recuperados, sem adicionar informações externas.*")

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "resposta_gerada": "\n".join(answer_parts),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "resumo_busca": search_overview,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "resumo_documento": document_summary,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "analise_documento": "\n".join(facts_block),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "usou_llm_externo": bool(llm_answer),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "provedor_llm": llm_provider,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# Comentário explicativo: Define a função `generate_rag_response`, que encapsula uma parte específica da lógica do projeto.
def generate_rag_response(query: str, retrieved_context: list, llm_config: dict = None) -> dict:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Gera uma resposta fundamentada nos contextos recuperados.
    
    Args:
        query: Pergunta do usuário.
        retrieved_context: Lista de chunks retornados pelo retrieval.
        llm_config: Opcional. Dict com provider, model, api_key para
                    sobrepor as variáveis de ambiente.
    """
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not isinstance(query, str):
        # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
        raise TypeError("query deve ser uma string.")
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not isinstance(retrieved_context, list):
        # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
        raise TypeError("retrieved_context deve ser uma lista.")

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not retrieved_context:
        # Comentário explicativo: Define ou atualiza `search_overview` com o valor calculado à direita.
        search_overview = _build_search_overview(query, [])
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return {
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "resposta_gerada": (
                f"{search_overview}\n\n"
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "Não encontrei informações suficientes na minha base de conhecimento "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "para responder a essa pergunta. "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "Infelizmente, não posso ajudar com isso no momento.\n\n"
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "Por favor, procure ajuda humana para obter a informação correta."
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ),
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "resumo_busca": search_overview,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "resumo_documento": "Não foi possível sintetizar um documento de referência porque nenhum trecho relevante foi recuperado.",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "analise_documento": "Sem dados suficientes para an\u00e1lise.",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "fontes": [],
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "usou_llm_externo": False,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "provedor_llm": "local",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "precisou_triagem": True,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "confianca": 0.0,
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }

    # Comentário explicativo: Define ou atualiza `top_score` com o valor calculado à direita.
    top_score = max(float(chunk.get("score", 0.0)) for chunk in retrieved_context)
    # Comentário explicativo: Define ou atualiza `search_overview` com o valor calculado à direita.
    search_overview = _build_search_overview(query, retrieved_context)
    # Comentário explicativo: Define ou atualiza `document_summary` com o valor calculado à direita.
    document_summary = _build_document_summary(query, retrieved_context)

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if top_score < DEFAULT_SCORE_THRESHOLD:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return {
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "resposta_gerada": (
                f"Pesquisa realizada:\n{search_overview}\n\n"
                f"Síntese do conteúdo:\n{document_summary}\n\n"
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "A evidência disponível é muito fraca para uma resposta confiável. "
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "Não posso ajudar com essa pergunta no momento.\n\n"
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                "Por favor, procure ajuda humana ou inclua documentos mais específicos na base de conhecimento."
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ),
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "resumo_busca": search_overview,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "resumo_documento": document_summary,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "analise_documento": "Sem dados suficientes para an\u00e1lise.",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "fontes": retrieved_context,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "usou_llm_externo": False,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "provedor_llm": "local",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "precisou_triagem": True,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "confianca": round(top_score, 4),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }

    # Comentário explicativo: Define ou atualiza `response_parts` com o valor calculado à direita.
    response_parts = _build_analytical_answer(query, retrieved_context, llm_config)
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "resposta_gerada": response_parts["resposta_gerada"],
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "resumo_busca": response_parts["resumo_busca"],
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "resumo_documento": response_parts["resumo_documento"],
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "analise_documento": response_parts["analise_documento"],
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "fontes": retrieved_context,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "usou_llm_externo": response_parts.get("usou_llm_externo", False),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "provedor_llm": response_parts.get("provedor_llm", "local"),
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "precisou_triagem": False,
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "confianca": round(top_score, 4),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }


# Comentário explicativo: Define a função `generate_response`, que encapsula uma parte específica da lógica do projeto.
def generate_response(query: str, retrieved_context: list, llm_config: dict = None) -> dict:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Alias compatível com a interface."""
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return generate_rag_response(query, retrieved_context, llm_config)


# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":  # pragma: no cover - teste manual
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print(generate_rag_response("Como recuperar acesso?", []))
