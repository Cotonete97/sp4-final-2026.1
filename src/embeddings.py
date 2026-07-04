
# Esta tarefa converte os chunks de texto (saída da Tarefa 02) em vetores
# numéricos densos (embeddings) utilizando o modelo Sentence-Transformer
# do BERT-base. A arquitetura funciona assim:
#
#   1. Tokenização: texto → tokens (subword/WordPiece)
#   2. Transformer L6: 6 camadas de self-attention + feed-forward
#   3. Pooling: média dos tokens de saída → vetor 384-d
#   4. Normalização: L2-normalização (vetor unitário)
#
# A dimensão 384 é um bom balanço entre capacidade expressiva e custo
# computacional. O "v2" indica melhorias no treinamento contrastivo
# (siamese networks com triplet loss / cosine similarity loss).

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from model_cache import get_sentence_transformer

# CONFIGURAÇÃO

# Comentário explicativo: Define ou atualiza `MODEL_NAME` com o valor calculado à direita.
MODEL_NAME = "all-MiniLM-L6-V2"

# FUNÇÃO PRINCIPAL

# Comentário explicativo: Define a função `generate_embeddings`, que encapsula uma parte específica da lógica do projeto.
def generate_embeddings(chunks_list: list) -> list:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Gera vetores de embeddings para cada chunk de texto processado.

    A função percorre a lista de chunks, extrai o texto de cada um (chave
    ``"texto"``, conforme gerado pela Tarefa 02), e utiliza o modelo
    Sentence-Transformer ``all-MiniLM-L6-v2`` para converter cada texto em
    um vetor numérico de 384 dimensões.

    O embedding gerado é um **vetor denso** que representa o significado
    semântico do texto. Quanto mais próximo dois embeddings estiverem no
    espaço 384-dimensional (medido por cosseno ou dot product), mais
    semanticamente relacionados são os textos originais. Isto permite:

      • Busca semântica (Tarefa 05): encontrar chunks relevantes para
        uma pergunta mesmo sem correspondência exata de palavras.
      • Clustering: agrupar chunks por tópico.
      • Classificação: categorizar automaticamente o conteúdo.

    Parâmetros:
        chunks_list (list): Lista de dicionários (chunks) gerada na
            Tarefa 02 (chunking.py). Cada dicionário deve conter pelo
            menos a chave ``"texto"`` com o conteúdo textual do chunk.

    Retorno:
        list: A mesma lista recebida, mas com a chave ``"embedding"``
        adicionada a cada dicionário. O valor é uma lista de floats
        de 384 posições representando o vetor de embedding.

    Levanta:
        TypeError: Se chunks_list não for uma lista ou se algum item
            não for um dicionário.
        KeyError: Se um chunk não contiver a chave ``"texto"``.
        RuntimeError: Se o modelo não puder ser carregado.

    Exemplo de saída de um chunk processado:

    .. code-block:: python

        {
            "id": "doc_abc123_chunk_0001",
            "doc_id": "doc_abc123",
            "texto": "Procedimento de recuperação de acesso ao sistema...",
            "metadata": {...},
            "embedding": [0.0234, -0.1567, 0.0892, ..., 0.0123]  # 384 floats
        }
    """
    # Validação de entrada (defensive programming)

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not isinstance(chunks_list, list):
        # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
        raise TypeError(
            f"chunks_list deve ser uma lista, recebeu {type(chunks_list).__name__}."
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not chunks_list:
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return []

    # Extração dos textos - valida estrutura de cada chunk

    # Comentário explicativo: Define ou atualiza `textos` com o valor calculado à direita.
    textos = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for i, chunk in enumerate(chunks_list):
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not isinstance(chunk, dict):
            # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
            raise TypeError(
                f"Item na posição {i} não é um dicionário, "
                f"recebeu {type(chunk).__name__}."
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            )
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if "texto" not in chunk:
            # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
            raise KeyError(
                f"Chunk na posição {i} não possui a chave 'texto'. "
                f"Chaves encontradas: {list(chunk.keys())}"
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            )
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        textos.append(chunk["texto"])

    # Carregamento do modelo (cache compartilhado com chunking.py)

    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
        model = get_sentence_transformer()
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except Exception as exc:
        # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
        raise RuntimeError(
            f"Não foi possível carregar o modelo '{MODEL_NAME}'. "
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "Verifique sua conexão com a internet para o download inicial."
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        ) from exc

    # O método encode() do SentenceTransformer processa em batch e
    # utiliza aceleração GPU se disponível (CUDA / MPS).
    # show_progress_bar=False mantém a saída limpa em produção; mude
    # para True para depuração com muitos chunks.
    # Comentário explicativo: Define ou atualiza `embeddings` com o valor calculado à direita.
    embeddings = model.encode(
        # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
        textos,
        # Comentário explicativo: Define ou atualiza `show_progress_bar` com o valor calculado à direita.
        show_progress_bar=False,
        # Comentário explicativo: Define ou atualiza `batch_size` com o valor calculado à direita.
        batch_size=32,  # Ajustável; 32 é um bom padrão para CPU/GPU
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    )

    # Acoplar embeddings aos chunks originais

    # embeddings retorna um np.ndarray de shape (n_chunks, 384).
    # Convertemos para lista de floats com .tolist() para que seja
    # serializável em JSON (importante para persistência no banco vetorial).
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for i, embedding in enumerate(embeddings):
        # Comentário explicativo: Define ou atualiza `chunks_list[i]["embedding"]` com o valor calculado à direita.
        chunks_list[i]["embedding"] = embedding.tolist()

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return chunks_list


# TESTE ISOLADO DA TAREFA 03

# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("═" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  TESTE ISOLADO DA TAREFA 03 — GERAÇÃO DE EMBEDDINGS")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("═" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  Simula a saída da Tarefa 02 (chunking.py) e gera embeddings")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  para cada chunk usando all-MiniLM-L6-v2 (384 dimensões).")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()

    # ── Chunks de exemplo simulando a saída da Tarefa 02 ──

    # Comentário explicativo: Define ou atualiza `chunks_teste` com o valor calculado à direita.
    chunks_teste = [
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "id": "doc_exemplo_chunk_0001",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "doc_id": "doc_exemplo",
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "texto": "Procedimento de recuperação de acesso ao sistema institucional. "
                     # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                     "Para iniciar a recuperação, o usuário deve acessar a página "
                     # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                     "oficial de autenticação e selecionar a opção Esqueci minha senha.",
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "metadata": {
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "titulo": "Procedimento de recuperação de acesso",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "fonte": "Manual interno - acesso institucional",
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            },
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        },
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "id": "doc_exemplo_chunk_0002",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "doc_id": "doc_exemplo",
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "texto": "Depois da redefinição, a nova senha deve respeitar os critérios "
                     # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                     "exibidos na tela, incluindo tamanho mínimo e combinação de letras, "
                     # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                     "números e caracteres especiais.",
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "metadata": {
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "titulo": "Procedimento de recuperação de acesso",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "fonte": "Manual interno - acesso institucional",
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            },
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        },
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "id": "doc_exemplo_chunk_0003",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "doc_id": "doc_exemplo",
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "texto": "Para iniciar a recuperação, o usuário deve acessar a página "
                     # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
                     "oficial de autenticação e selecionar a opção Esqueci minha senha. "
                     # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                     "Em seguida, deve informar o e-mail institucional cadastrado.",
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            "metadata": {
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "titulo": "Procedimento de recuperação de acesso",
                # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
                "fonte": "Manual interno - acesso institucional",
            # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
            },
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        },
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ]

    print(f"  📦 Chunks de teste: {len(chunks_teste)} chunks")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()

    # Comentário explicativo: Define ou atualiza `resultado` com o valor calculado à direita.
    resultado = generate_embeddings(chunks_teste)

    print(f"  ✅ Chunks processados: {len(resultado)}")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print()

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for chunk in resultado:
        print(f"  ┌─ ID: {chunk['id']}")
        # Comentário explicativo: Define ou atualiza `texto_preview` com o valor calculado à direita.
        texto_preview = chunk["texto"][:70].replace("\n", " ")
        print(f"  ├─ Texto: \"{texto_preview}...\"")
        # Comentário explicativo: Define ou atualiza `emb` com o valor calculado à direita.
        emb = chunk["embedding"]
        # Comentário explicativo: Define ou atualiza `dimensoes` com o valor calculado à direita.
        dimensoes = len(emb)
        print(f"  ├─ Embedding: {dimensoes} dimensões")

        # Mostra os 5 primeiros valores com 4 casas decimais
        preview_emb = ", ".join(f"{v:+.4f}" for v in emb[:5])
        print(f"  ├─ Primeiros valores: [{preview_emb}, ...]")

        # Calcula a norma L2 — deve ser aproximadamente 1.0 (normalização)
        # Comentário explicativo: Define ou atualiza `norma` com o valor calculado à direita.
        norma = sum(x ** 2 for x in emb) ** 0.5
        print(f"  └─ Norma L2: {norma:.6f}  (esperado ≈ 1.0)")
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print()

    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("═" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  TESTE CONCLUÍDO COM SUCESSO!")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("═" * 70)
