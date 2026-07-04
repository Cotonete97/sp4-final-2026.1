# Comentário explicativo: Importa o módulo `hashlib` para ser usado neste arquivo.
import hashlib
# Comentário explicativo: Importa o módulo `json` para ser usado neste arquivo.
import json
# Comentário explicativo: Importa o módulo `re` para ser usado neste arquivo.
import re

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Quantidade máxima de caracteres em cada chunk.
# Comentário explicativo: Define o tamanho máximo aproximado usado para cada chunk de texto.
CHUNK_SIZE = 1000

# Parte repetida entre chunks consecutivos para preservar o contexto quando uma informação fica próxima da divisão do texto.
# Comentário explicativo: Define quantos caracteres podem se repetir entre chunks vizinhos para preservar contexto.
CHUNK_OVERLAP = 200

# Modelo usado apenas como apoio interno para detectar mudança semântica entre trechos.
# Comentário explicativo: Define o modelo usado como apoio semântico temporário no chunking.
SEMANTIC_MODEL_NAME = "all-MiniLM-L6-v2"

# Quanto menor a similaridade entre trechos consecutivos, maior a chance de mudança de assunto.
# Comentário explicativo: Define o limiar que ajuda a detectar mudança de assunto entre trechos.
SEMANTIC_SIMILARITY_THRESHOLD = 0.45

# Evita criar chunks pequenos demais só porque duas frases tiveram baixa similaridade.
# Comentário explicativo: Define o tamanho mínimo para evitar chunks semânticos pequenos demais.
MIN_SEMANTIC_CHUNK_SIZE = 300

# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
_SENTENCE_SEPARATOR_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\[])")
# Comentário explicativo: Define ou atualiza `_PARAGRAPH_SEPARATOR_PATTERN` com o valor calculado à direita.
_PARAGRAPH_SEPARATOR_PATTERN = re.compile(r"\n\s*\n+")

# Abreviações conhecidas do português que NÃO devem ser confundidas com fim de frase.
# O split por sentenças protege estas abreviações temporariamente para evitar
# que o "." seja interpretado como pontuação de encerramento.
# Comentário explicativo: Define ou atualiza `_ABREVIACOES_CONHECIDAS` com o valor calculado à direita.
_ABREVIACOES_CONHECIDAS = re.compile(
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    r"\b(?:Dr|Sr|Sra|Srta|Srtas|Srs|Sras|etc|Ltda|obs|art|pág|vol|cap|ed|Ex|V)\.\s",
    # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
    re.UNICODE,
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
)
# Placeholder usado durante a proteção (caractere de controle não-imprimível).
# Durante a proteção, substitui o espaço após a abreviatura para que o
# separador de sentenças não confunda "Dr. " com fim de frase.
# Na restauração, o marcador é convertido de volta para um espaço simples.
# Comentário explicativo: Define ou atualiza `_ABBREV_MARKER` com o valor calculado à direita.
_ABBREV_MARKER = "\x00"

# Comentário explicativo: Define ou atualiza `_semantic_model` com o valor calculado à direita.
_semantic_model = None


# Comentário explicativo: Define a função `_get_semantic_model`, que encapsula uma parte específica da lógica do projeto.
def _get_semantic_model():
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """DEPRECATED: use model_cache.get_sentence_transformer().
    Mantido apenas para não quebrar imports externos."""
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from model_cache import get_sentence_transformer
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return get_sentence_transformer()


# Comentário explicativo: Define a função `_generate_doc_id`, que encapsula uma parte específica da lógica do projeto.
def _generate_doc_id(metadata: dict, cleaned_text: str) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Gera um identificador estável a partir dos metadados e do conteúdo do documento."""
    # Comentário explicativo: Define ou atualiza `metadata_serialized` com o valor calculado à direita.
    metadata_serialized = json.dumps(
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        metadata,
        # Comentário explicativo: Define ou atualiza `ensure_ascii` com o valor calculado à direita.
        ensure_ascii=False,
        # Comentário explicativo: Define ou atualiza `sort_keys` com o valor calculado à direita.
        sort_keys=True,
        # Comentário explicativo: Define ou atualiza `default` com o valor calculado à direita.
        default=str,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Comentário explicativo: Define ou atualiza `hash_metadata` com o valor calculado à direita.
    hash_metadata = hashlib.sha256(metadata_serialized.encode("utf-8")).hexdigest()
    # Comentário explicativo: Define ou atualiza `hash_content` com o valor calculado à direita.
    hash_content = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
    # Comentário explicativo: Define ou atualiza `hash_document` com o valor calculado à direita.
    hash_document = hashlib.sha256(
        f"{hash_metadata}:{hash_content}".encode("utf-8")
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ).hexdigest()

    return f"doc_{hash_document[:12]}"


# Comentário explicativo: Define a função `_split_long_text`, que encapsula uma parte específica da lógica do projeto.
def _split_long_text(text: str) -> list:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Divide trechos grandes demais usando o RecursiveCharacterTextSplitter como fallback."""
    # Comentário explicativo: Define ou atualiza `text_splitter` com o valor calculado à direita.
    text_splitter = RecursiveCharacterTextSplitter(
        # Comentário explicativo: Define ou atualiza `chunk_size` com o valor calculado à direita.
        chunk_size=CHUNK_SIZE,
        # Comentário explicativo: Define ou atualiza `chunk_overlap` com o valor calculado à direita.
        chunk_overlap=CHUNK_OVERLAP,
        # Comentário explicativo: Define ou atualiza `length_function` com o valor calculado à direita.
        length_function=len,
        # Comentário explicativo: Define ou atualiza `separators` com o valor calculado à direita.
        separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
        # Comentário explicativo: Define ou atualiza `keep_separator` com o valor calculado à direita.
        keep_separator="start",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # O keep_separator=\"start\" mantém o separador no início do chunk seguinte.
    # Removemos pontuação inicial (\". \", \", \") que ficou órfã, já que o
    # separador cumpriu seu papel de marcar a quebra — a pontuação pertence
    # ao chunk anterior, não ao atual.
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return [
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        chunk.lstrip(".!?;:,").strip()
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for chunk in text_splitter.split_text(text)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if chunk.strip()
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ]


# Comentário explicativo: Define a função `_protect_abbreviations`, que encapsula uma parte específica da lógica do projeto.
def _protect_abbreviations(text: str) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Protege abreviações conhecidas para o separador de sentenças não quebrá-las.

    Remove o espaço após a abreviatura e insere um marcador temporário no lugar.
    Ex: "Dr. Carlos" → "Dr.\\x00Carlos"

    Após o split por sentenças, _restore_abbreviations() converte o marcador
    de volta para um espaço simples, restaurando o texto original sem duplicação.
    """
    # Comentário explicativo: Define a função `_protect`, que encapsula uma parte específica da lógica do projeto.
    def _protect(match: re.Match) -> str:
        # match.group(0) é "Dr. " — remove o espaço final e coloca o marcador
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return match.group(0).rstrip() + _ABBREV_MARKER
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return _ABREVIACOES_CONHECIDAS.sub(_protect, text)


# Comentário explicativo: Define a função `_restore_abbreviations`, que encapsula uma parte específica da lógica do projeto.
def _restore_abbreviations(text: str) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Restaura os espaços removidos pela proteção de abreviações."""
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return text.replace(_ABBREV_MARKER, " ")


# Comentário explicativo: Define a função `_split_into_semantic_units`, que encapsula uma parte específica da lógica do projeto.
def _split_into_semantic_units(cleaned_text: str) -> list:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Quebra o texto em unidades de comparação semântica.

    Primeiro o texto é dividido por parágrafos e frases. Depois essas unidades
    são comparadas por embeddings temporários para decidir onde os chunks devem
    começar e terminar.

    Abreviações conhecidas (Dr., Sr., Sra., etc.) são protegidas antes do
    split por sentenças para evitar que o ponto final seja confundido com
    pontuação de encerramento de frase.
    """
    # Comentário explicativo: Define ou atualiza `paragraphs` com o valor calculado à direita.
    paragraphs = [
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        paragraph.strip()
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for paragraph in _PARAGRAPH_SEPARATOR_PATTERN.split(cleaned_text)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if paragraph.strip()
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ]

    # Comentário explicativo: Define ou atualiza `semantic_units` com o valor calculado à direita.
    semantic_units = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for paragraph in paragraphs:
        # Protege abreviações antes de dividir em sentenças
        # Comentário explicativo: Define ou atualiza `paragraph_protected` com o valor calculado à direita.
        paragraph_protected = _protect_abbreviations(paragraph)

        # Comentário explicativo: Define ou atualiza `sentences` com o valor calculado à direita.
        sentences = [
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            sentence.strip()
            # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
            for sentence in _SENTENCE_SEPARATOR_PATTERN.split(paragraph_protected)
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if sentence.strip()
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ]

        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not sentences:
            # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
            continue

        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for sentence in sentences:
            # Restaura abreviações em cada sentença
            # Comentário explicativo: Define ou atualiza `sentence` com o valor calculado à direita.
            sentence = _restore_abbreviations(sentence)

            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if len(sentence) <= CHUNK_SIZE:
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                semantic_units.append(sentence)
            # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
            else:
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                semantic_units.extend(_split_long_text(sentence))

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return semantic_units


# Comentário explicativo: Define a função `_encode_semantic_units`, que encapsula uma parte específica da lógica do projeto.
def _encode_semantic_units(semantic_units: list):
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Gera embeddings temporários(sem salvar nem retornar eles) apenas para comparar a semântica dos trechos.
    """
    # Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
    model = _get_semantic_model()
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return model.encode(
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        semantic_units,
        # Comentário explicativo: Define ou atualiza `show_progress_bar` com o valor calculado à direita.
        show_progress_bar=False,
        # Comentário explicativo: Define ou atualiza `batch_size` com o valor calculado à direita.
        batch_size=32,
        # Comentário explicativo: Define ou atualiza `normalize_embeddings` com o valor calculado à direita.
        normalize_embeddings=True,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )


# Comentário explicativo: Define a função `_join_units_by_indexes`, que encapsula uma parte específica da lógica do projeto.
def _join_units_by_indexes(semantic_units: list, indexes: list) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Junta unidades de texto preservando separação legível entre elas."""
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "\n\n".join(semantic_units[index] for index in indexes).strip()


# Comentário explicativo: Define a função `_cosine_similarity`, que encapsula uma parte específica da lógica do projeto.
def _cosine_similarity(normalized_embeddings, first_index: int, second_index: int) -> float:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Calcula similaridade de cosseno entre dois embeddings já normalizados."""
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return float(normalized_embeddings[first_index] @ normalized_embeddings[second_index])


# Comentário explicativo: Define a função `_get_overlap_indexes`, que encapsula uma parte específica da lógica do projeto.
def _get_overlap_indexes(current_indexes: list, semantic_units: list) -> list:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Mantém overlap reaproveitando unidades completas, sem começar no meio da frase."""
    # Comentário explicativo: Define ou atualiza `overlap_indexes` com o valor calculado à direita.
    overlap_indexes = []
    # Comentário explicativo: Define ou atualiza `overlap_size` com o valor calculado à direita.
    overlap_size = 0

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for index in reversed(current_indexes):
        # Comentário explicativo: Define ou atualiza `unit_size` com o valor calculado à direita.
        unit_size = len(semantic_units[index]) + (2 if overlap_indexes else 0)

        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if overlap_indexes and overlap_size + unit_size > CHUNK_OVERLAP:
            # Comentário explicativo: Interrompe o laço atual antes de percorrer todos os itens.
            break

        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        overlap_indexes.insert(0, index)
        # Comentário explicativo: Define ou atualiza `overlap_size +` com o valor calculado à direita.
        overlap_size += unit_size

        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if overlap_size >= CHUNK_OVERLAP:
            # Comentário explicativo: Interrompe o laço atual antes de percorrer todos os itens.
            break

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return overlap_indexes


# Comentário explicativo: Define a função `_build_semantic_chunks`, que encapsula uma parte específica da lógica do projeto.
def _build_semantic_chunks(semantic_units: list) -> list:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Monta chunks usando mudança semântica e limite máximo de tamanho."""
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not semantic_units:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return []

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if len(semantic_units) == 1:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return _split_long_text(semantic_units[0])

    # Comentário explicativo: Define ou atualiza `embeddings` com o valor calculado à direita.
    embeddings = _encode_semantic_units(semantic_units)
    # Comentário explicativo: Define ou atualiza `texts` com o valor calculado à direita.
    texts = []
    # Comentário explicativo: Define ou atualiza `current_indexes` com o valor calculado à direita.
    current_indexes = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for index, unit in enumerate(semantic_units):
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not current_indexes:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            current_indexes.append(index)
            # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
            continue

        # Comentário explicativo: Define ou atualiza `current_text` com o valor calculado à direita.
        current_text = _join_units_by_indexes(semantic_units, current_indexes)
        # Comentário explicativo: Define ou atualiza `candidate_text` com o valor calculado à direita.
        candidate_text = _join_units_by_indexes(semantic_units, current_indexes + [index])

        # Regra 1: nunca passar do tamanho máximo definido para o chunk.
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if len(candidate_text) > CHUNK_SIZE:
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            texts.append(current_text)
            # Comentário explicativo: Define ou atualiza `current_indexes` com o valor calculado à direita.
            current_indexes = _get_overlap_indexes(current_indexes, semantic_units)

            # Comentário explicativo: Define ou atualiza `candidate_text` com o valor calculado à direita.
            candidate_text = _join_units_by_indexes(semantic_units, current_indexes + [index])
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if len(candidate_text) > CHUNK_SIZE:
                # Comentário explicativo: Define ou atualiza `current_indexes` com o valor calculado à direita.
                current_indexes = []

        # Regra 2: se houve queda semântica relevante, abre um novo chunk.
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if current_indexes:
            # Comentário explicativo: Define ou atualiza `current_text` com o valor calculado à direita.
            current_text = _join_units_by_indexes(semantic_units, current_indexes)

            # Calcula a similaridade entre o CENTROIDE do chunk atual e a nova
            # unidade. Usar a média (centroide) de todos os embeddings do chunk
            # é mais estável do que comparar apenas com a última unidade, pois
            # evita que uma unidade de transição genérica (ex: "Siga as
            # instruções acima.") cause uma quebra falsa no chunk.
            # Comentário explicativo: Define ou atualiza `centroid` com o valor calculado à direita.
            centroid = embeddings[current_indexes].mean(axis=0)
            # Comentário explicativo: Define ou atualiza `similarity` com o valor calculado à direita.
            similarity = float(centroid @ embeddings[index])

            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if (
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                len(current_text) >= MIN_SEMANTIC_CHUNK_SIZE
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                and similarity < SEMANTIC_SIMILARITY_THRESHOLD
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            ):
                # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                texts.append(current_text)
                # Comentário explicativo: Define ou atualiza `current_indexes` com o valor calculado à direita.
                current_indexes = _get_overlap_indexes(current_indexes, semantic_units)

                # Comentário explicativo: Define ou atualiza `candidate_text` com o valor calculado à direita.
                candidate_text = _join_units_by_indexes(semantic_units, current_indexes + [index])
                # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
                if len(candidate_text) > CHUNK_SIZE:
                    # Comentário explicativo: Define ou atualiza `current_indexes` com o valor calculado à direita.
                    current_indexes = []

        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        current_indexes.append(index)

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if current_indexes:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        texts.append(_join_units_by_indexes(semantic_units, current_indexes))

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return texts


# Comentário explicativo: Define a função `chunk_document`, que encapsula uma parte específica da lógica do projeto.
def chunk_document(cleaned_text: str, metadata: dict) -> list:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Divide um texto limpo em chunks menores e associa os metadados do documento.

    Parâmetros:
        cleaned_text (str): Texto limpo e anonimizado recebido da issue do Felipe.
        metadata (dict): Metadados do documento, como título e fonte original.

    Retorno:
        list: Lista de dicionários com id, doc_id, texto e metadata.
    """
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not isinstance(cleaned_text, str):
        # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
        raise TypeError("cleaned_text deve ser uma string.")

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not isinstance(metadata, dict):
        # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
        raise TypeError("metadata deve ser um dicionário.")

    # Comentário explicativo: Define ou atualiza `cleaned_text` com o valor calculado à direita.
    cleaned_text = cleaned_text.strip()

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not cleaned_text:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return []

    # Comentário explicativo: Define ou atualiza `semantic_units` com o valor calculado à direita.
    semantic_units = _split_into_semantic_units(cleaned_text)
    # Comentário explicativo: Define ou atualiza `texts` com o valor calculado à direita.
    texts = _build_semantic_chunks(semantic_units)
    # Comentário explicativo: Define ou atualiza `doc_id` com o valor calculado à direita.
    doc_id = _generate_doc_id(metadata, cleaned_text)

    # Comentário explicativo: Define ou atualiza `chunks` com o valor calculado à direita.
    chunks = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for position, text in enumerate(texts, start=1):
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        chunks.append(
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            {
                "id": f"{doc_id}_chunk_{position:04d}",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "doc_id": doc_id,
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "texto": text,
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "metadata": metadata.copy(),
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            }
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return chunks


# Teste isolado da Tarefa 02.
# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":
    # SIMULAÇÃO 1:

    # Comentário explicativo: Define ou atualiza `exemplo_texto_limpo_1` com o valor calculado à direita.
    exemplo_texto_limpo_1 = """
    Procedimento de recuperação de acesso ao sistema institucional. A usuária
    [NOME REMOVIDO], inscrita no CPF [CPF REMOVIDO] e cadastrada com o e-mail
    [EMAIL REMOVIDO], informou que não consegue entrar no sistema de atendimento.
    Para iniciar a recuperação, o usuário deve acessar a página oficial de
    autenticação e selecionar a opção Esqueci minha senha. Em seguida, deve
    informar o e-mail institucional cadastrado e aguardar o envio da mensagem
    com o link temporário de redefinição. O link deve ser utilizado dentro do
    prazo informado na mensagem. Caso o e-mail não seja recebido, o usuário
    deve verificar as pastas de spam e lixo eletrônico. Se a mensagem continuar
    ausente, deve confirmar se o endereço institucional foi digitado corretamente.

    Depois da redefinição, a nova senha deve respeitar os critérios exibidos na
    tela, incluindo tamanho mínimo e combinação de letras, números e caracteres
    especiais. Quando a conta estiver bloqueada por excesso de tentativas, o
    usuário deve aguardar o período indicado antes de tentar novamente. Se o
    bloqueio permanecer, o chamado deve ser encaminhado ao atendimento
    responsável por acessos. O chamado deve informar o sistema utilizado, a
    mensagem de erro e o horário aproximado da tentativa, sem incluir senha ou
    outros dados sensíveis.

    Em erros de autenticação após a troca da senha, recomenda-se encerrar todas
    as sessões abertas, fechar o navegador, abri-lo novamente e repetir o acesso.
    Caso o sistema utilize autenticação em dois fatores, o usuário deve confirmar
    se o dispositivo cadastrado está disponível e com data e hora corretas.
    Códigos temporários expirados não devem ser reutilizados. Quando houver troca
    ou perda do dispositivo autenticador, a recuperação deverá seguir o
    procedimento institucional e poderá exigir validação humana.

    O atendente deve utilizar somente documentos oficiais da base de conhecimento.
    Quando os documentos recuperados não apresentarem evidência suficiente, o
    caso deverá ser encaminhado para triagem humana. A fonte original deverá
    permanecer associada aos trechos para que as próximas etapas consigam informar
    qual documento fundamentou a resposta.
    """

    # SIMULAÇÃO 2:
    # Este texto usa os MESMOS metadados do primeiro, mas possui conteúdo diferente.
    # Só tá aqui pra provar que vai gerar ids diferentes e resolveu o problema que achamos na call
    # Comentário explicativo: Define ou atualiza `exemplo_texto_limpo_2` com o valor calculado à direita.
    exemplo_texto_limpo_2 = """
    Procedimento de recuperação de acesso ao sistema institucional. O usuário
    informou que consegue acessar o sistema, mas não consegue validar o segundo
    fator de autenticação. A primeira orientação é confirmar se o aplicativo
    autenticador está instalado no dispositivo correto e se a data e hora do
    aparelho estão configuradas automaticamente.

    Caso o código temporário seja recusado, o usuário deve gerar um novo código
    e tentar novamente dentro do prazo de validade. Códigos antigos ou já
    utilizados não devem ser reaproveitados. Se o usuário tiver trocado de
    celular, perdido o dispositivo ou removido o aplicativo autenticador, o caso
    deve seguir o procedimento institucional de recuperação de segundo fator.

    Quando a recuperação automática não estiver disponível, o chamado deve ser
    encaminhado para triagem humana. O atendente deve registrar o sistema
    afetado, a mensagem exibida na tela e o horário aproximado da tentativa,
    sem solicitar senha, código temporário ou dados sensíveis do usuário.
    """

    # Comentário explicativo: Define ou atualiza `metadados_de_teste` com o valor calculado à direita.
    metadados_de_teste = {
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "titulo": "Procedimento de recuperação de acesso",
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        "fonte": "Manual interno de suporte - acesso institucional",
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    }

    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("TESTE ISOLADO DA MINHA ISSUE 2")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print(
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Este teste usa exemplos hipotéticos de textos sintéticos já limpos e anonimizados só pra testar se deu bom."
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print(
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Esse teste não executa nem recebe diretamente a Issue 1."
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print(
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Na integração final do projeto, para usar o texto REAL final, o parâmetro cleaned_text da minha issue receberá "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "diretamente o texto retornado por ingest_and_anonymize() da issue do Felipe.\n"
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print(
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "OBS: usei o all-MiniLM-L6-v2 só pra dividir os chuncks com base em semantica como me sugeriram. "
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        "Mas não salvei nem retornei os embeddings para não invadir as tarefas da issue 3.\n"
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Comentário explicativo: Define ou atualiza `resultado_1` com o valor calculado à direita.
    resultado_1 = chunk_document(
        # Comentário explicativo: Define ou atualiza `cleaned_text` com o valor calculado à direita.
        cleaned_text=exemplo_texto_limpo_1,
        # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
        metadata=metadados_de_teste,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Comentário explicativo: Define ou atualiza `resultado_2` com o valor calculado à direita.
    resultado_2 = chunk_document(
        # Comentário explicativo: Define ou atualiza `cleaned_text` com o valor calculado à direita.
        cleaned_text=exemplo_texto_limpo_2,
        # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
        metadata=metadados_de_teste,
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Comentário explicativo: Define ou atualiza `doc_id_1` com o valor calculado à direita.
    doc_id_1 = resultado_1[0]["doc_id"] if resultado_1 else None
    # Comentário explicativo: Define ou atualiza `doc_id_2` com o valor calculado à direita.
    doc_id_2 = resultado_2[0]["doc_id"] if resultado_2 else None

    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("TESTE DE UNICIDADE DO DOC_ID")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("Os dois documentos abaixo usam o MESMO título e a MESMA fonte.")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("Mesmo assim, como o conteúdo é diferente, os doc_ids também devem ser diferentes.\n")

    print(f"DOC_ID DO DOCUMENTO 1: {doc_id_1}")
    print(f"DOC_ID DO DOCUMENTO 2: {doc_id_2}")

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if doc_id_1 != doc_id_2:
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("RESULTADO: OK - Os doc_ids ficaram diferentes mesmo com título/fonte iguais.\n")
    # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
    else:
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("RESULTADO: ERRO - Os doc_ids ficaram iguais. Isso indicaria risco de colisão.\n")

    print(f"A função chunk_document() gerou {len(resultado_1)} chunks para o documento 1.\n")

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in resultado_1:
        print(f"ID DO CHUNK: {chunk['id']}")
        print(f"DOC_ID: {chunk['doc_id']}")
        print(f"METADATA: {chunk['metadata']}")
        print(f"TEXTO ({len(chunk['texto'])} caracteres):")
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print(chunk["texto"])
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("-" * 70)

    print(f"\nA função chunk_document() gerou {len(resultado_2)} chunks para o documento 2.\n")

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in resultado_2:
        print(f"ID DO CHUNK: {chunk['id']}")
        print(f"DOC_ID: {chunk['doc_id']}")
        print(f"METADATA: {chunk['metadata']}")
        print(f"TEXTO ({len(chunk['texto'])} caracteres):")
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print(chunk["texto"])
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("-" * 70)
