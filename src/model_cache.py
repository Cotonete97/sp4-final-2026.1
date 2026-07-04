# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
"""Cache singleton para o modelo de embeddings SentenceTransformer.

Tanto a Tarefa 02 (chunking) quanto a Tarefa 03 (embeddings) usam o
mesmo modelo all-MiniLM-L6-v2. Este módulo garante que ele seja
carregado na memória apenas uma vez, evitando:

- ~2-3s extras de carregamento na transição entre tarefas
- ~80 MB de RAM duplicada durante a sobreposição

Uso:
    from model_cache import get_sentence_transformer
    model = get_sentence_transformer()
"""

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from sentence_transformers import SentenceTransformer

# Comentário explicativo: Define ou atualiza `_MODEL_NAME` com o valor calculado à direita.
_MODEL_NAME = "all-MiniLM-L6-v2"
# Comentário explicativo: Define ou atualiza `_model` com o valor calculado à direita.
_model = None


# Comentário explicativo: Define a função `get_sentence_transformer`, que encapsula uma parte específica da lógica do projeto.
def get_sentence_transformer() -> SentenceTransformer:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Retorna o modelo compartilhado de embeddings, carregando-o
    na primeira chamada (lazy initialization)."""
    # Comentário explicativo: Indica que a variável usada dentro da função é a variável global do módulo.
    global _model
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if _model is None:
        # Comentário explicativo: Define ou atualiza `_model` com o valor calculado à direita.
        _model = SentenceTransformer(_MODEL_NAME)
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return _model
