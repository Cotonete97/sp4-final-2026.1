# Tarefa 04: Armazenamento vetorial

# Comentário explicativo: Importa o módulo `chromadb` para ser usado neste arquivo.
import chromadb
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from chromadb.config import Settings

# Comentário explicativo: Define a função `store_in_vector_db`, que encapsula uma parte específica da lógica do projeto.
def store_in_vector_db(embedded_chunks: list) -> bool:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Armazena os chunks, embeddings e metadados no ChromaDB para busca semântica.
    
    Parâmetros:
        embedded_chunks (list): Lista de dicionários, onde cada dicionário contém:
                                - 'id': Identificador único do chunk
                                - 'texto': O texto original do chunk (conforme Tarefas 02 e 03)
                                - 'embedding': A lista de floats representando o vetor
                                - 'metadata': Dicionário com a fonte, página, etc.
                            
    Retorno:
        bool: True se a persistência for bem-sucedida, False caso contrário.
    """
    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Inicializa o ChromaDB com persistência em disco (evitando perda de dados) 
        # e desativa o envio de telemetria padrão para não expor a base.
        # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
        from pathlib import Path
        # Comentário explicativo: Define ou atualiza `db_path` com o valor calculado à direita.
        db_path = str(
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            Path(__file__).resolve().parent.parent / "data" / "vector_db" / "chroma_data"
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
        # Comentário explicativo: Define ou atualiza `client` com o valor calculado à direita.
        client = chromadb.PersistentClient(
            # Comentário explicativo: Define ou atualiza `path` com o valor calculado à direita.
            path=db_path,
            # Comentário explicativo: Define ou atualiza `settings` com o valor calculado à direita.
            settings=Settings(anonymized_telemetry=False)    
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

        # Cria ou recupera a coleção vetorial configurando o algoritmo HNSW para usar
        # similaridade de cosseno, o que otimiza a busca para o modelo SentenceTransformer.
        # Comentário explicativo: Define ou atualiza `collection` com o valor calculado à direita.
        collection = client.get_or_create_collection(
            # Comentário explicativo: Define ou atualiza `name` com o valor calculado à direita.
            name="ragnarok_knowledge_base",
            # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
            metadata={"hnsw:space": "cosine"}
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

        # Comentário explicativo: Define ou atualiza `ids` com o valor calculado à direita.
        ids = []
        # Comentário explicativo: Define ou atualiza `embeddings` com o valor calculado à direita.
        embeddings = []
        # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
        documents = []
        # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
        metadatas = []

        # Prepara os dados para inserção em lote (batch), extraindo os dicionários e
        # agrupando IDs, vetores, textos e metadados em listas contínuas na memória.
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for idx, chunk in enumerate(embedded_chunks):
            doc_id = chunk.get("id", f"doc_chunk_{idx}")
            
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            ids.append(doc_id)
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            embeddings.append(chunk["embedding"])
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            documents.append(chunk["texto"])
            
            # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
            metadata = chunk.get("metadata", {"source": "documento_desconhecido"})
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            metadatas.append(metadata)

        # Consolida a indexação: salva textos e metadados no SQLite e injeta os vetores
        # no grafo vetorial HNSW para busca semântica. IDs duplicados são rejeitados.
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        collection.add(
            # Comentário explicativo: Define ou atualiza `ids` com o valor calculado à direita.
            ids=ids,
            # Comentário explicativo: Define ou atualiza `embeddings` com o valor calculado à direita.
            embeddings=embeddings,
            # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
            documents=documents,
            # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
            metadatas=metadatas
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return True

    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except Exception as e:
        print(f"Erro ao persistir no banco vetorial: {e}")
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return False
