# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
"""Teste: palavra solta vs frase completa na busca semântica."""
# Comentário explicativo: Importa o módulo `sys` para ser usado neste arquivo.
import sys
# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
sys.path.insert(0, "src")

# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from sentence_transformers import SentenceTransformer
# Comentário explicativo: Importa o módulo `chromadb` para ser usado neste arquivo.
import chromadb
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from chromadb.config import Settings

# Comentário explicativo: Define ou atualiza `model` com o valor calculado à direita.
model = SentenceTransformer("all-MiniLM-L6-v2")
# Comentário explicativo: Define ou atualiza `client` com o valor calculado à direita.
client = chromadb.EphemeralClient()
# Comentário explicativo: Define ou atualiza `collection` com o valor calculado à direita.
collection = client.get_or_create_collection(
    # Comentário explicativo: Define ou atualiza `name` com o valor calculado à direita.
    name="test_words", metadata={"hnsw:space": "cosine"}
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
)

# Comentário explicativo: Define ou atualiza `chunks` com o valor calculado à direita.
chunks = [
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {"id": "c1", "texto": "Para recuperar a senha, o usuario deve acessar a pagina de login e clicar em Esqueci minha senha. Um e-mail sera enviado com o link de redefinicao."},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {"id": "c2", "texto": "O periodo de ferias deve ser solicitado com antecedencia minima de 30 dias. O RH analisa a solicitacao e aprova em ate 5 dias uteis."},
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    {"id": "c3", "texto": "A autenticacao em dois fatores adiciona uma camada extra de seguranca. O usuario deve confirmar o codigo enviado ao seu celular cadastrado."},
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
]
# Comentário explicativo: Define ou atualiza `texts` com o valor calculado à direita.
texts = [c["texto"] for c in chunks]
# Comentário explicativo: Define ou atualiza `embs` com o valor calculado à direita.
embs = model.encode(texts, normalize_embeddings=True).tolist()
# Comentário explicativo: Define ou atualiza `collection.add(ids` com o valor calculado à direita.
collection.add(ids=[c["id"] for c in chunks], embeddings=embs, documents=texts)

# Comentário explicativo: Define ou atualiza `queries` com o valor calculado à direita.
queries = [
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("senha", "Palavra solta"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("acesso senha", "Duas palavras"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("Como recuperar minha senha?", "Frase completa"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("ferias", "Palavra solta"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("solicitar ferias", "Duas palavras"),
    # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
    ("Como solicitar ferias?", "Frase completa"),
# Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
]

print(f"{'Query':45s} {'Chunk':6s} {'Score':8s}  {'Trecho'}")
# Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
print("-" * 110)
# Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
for q_text, q_desc in queries:
    # Comentário explicativo: Define ou atualiza `q_emb` com o valor calculado à direita.
    q_emb = model.encode(q_text, normalize_embeddings=True).tolist()
    # Comentário explicativo: Define ou atualiza `results` com o valor calculado à direita.
    results = collection.query(query_embeddings=[q_emb], n_results=1)
    # Comentário explicativo: Define ou atualiza `dist` com o valor calculado à direita.
    dist = results["distances"][0][0]
    # Comentário explicativo: Define ou atualiza `score` com o valor calculado à direita.
    score = 1.0 - (dist / 2.0)
    # Comentário explicativo: Define ou atualiza `cid` com o valor calculado à direita.
    cid = results["ids"][0][0]
    # Comentário explicativo: Define ou atualiza `preview` com o valor calculado à direita.
    preview = results["documents"][0][0][:55]
    label = f"{q_desc}: {q_text}"
    print(f"{label:45s} {cid:6s} {score:8.4f}  {preview}")
