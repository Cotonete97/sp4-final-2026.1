#!/usr/bin/env python3
# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
"""
Script de ingestão limpa dos PDFs do PGD.

Limpa o ChromaDB existente e re-ingere todos os PDFs de data/pdfs/
em uma única passada, sem duplicatas.

Uso:
    conda run -n chatbot python scripts/reingest_pdfs.py
"""

# Comentário explicativo: Importa o módulo `sys` para ser usado neste arquivo.
import sys
# Comentário explicativo: Importa o módulo `shutil` para ser usado neste arquivo.
import shutil
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from pathlib import Path
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from io import BytesIO
# Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
from datetime import datetime, timezone

# Adiciona src/ ao path
# Comentário explicativo: Define ou atualiza `PROJECT_ROOT` com o valor calculado à direita.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Comentário explicativo: Define ou atualiza `PDF_DIR` com o valor calculado à direita.
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"
# Comentário explicativo: Define ou atualiza `VECTOR_DB_PATH` com o valor calculado à direita.
VECTOR_DB_PATH = PROJECT_ROOT / "data" / "vector_db" / "chroma_data"
# Comentário explicativo: Define ou atualiza `COLLECTION_NAME` com o valor calculado à direita.
COLLECTION_NAME = "ragnarok_knowledge_base"


# Comentário explicativo: Define a função `extract_pdf_text`, que encapsula uma parte específica da lógica do projeto.
def extract_pdf_text(raw_content: bytes) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Extrai texto de um PDF usando pymupdf, pypdf ou PyPDF2."""
    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Importa o módulo `fitz` para ser usado neste arquivo.
        import fitz  # pymupdf
        # Comentário explicativo: Define ou atualiza `doc` com o valor calculado à direita.
        doc = fitz.open(stream=raw_content, filetype="pdf")
        # Comentário explicativo: Define ou atualiza `pages` com o valor calculado à direita.
        pages = []
        # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
        for i, page in enumerate(doc, start=1):
            # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
            text = page.get_text().strip()
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if text:
                pages.append(f"\n\n[Página {i}]\n{text}")
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return "\n".join(pages)
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except ImportError:
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        pass

    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
        from pypdf import PdfReader
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except ImportError:
        # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
        try:
            # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
            from PyPDF2 import PdfReader
        # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
        except ImportError:
            # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
            raise RuntimeError("Instale pymupdf, pypdf ou PyPDF2 para ler PDFs.")

    # Comentário explicativo: Define ou atualiza `reader` com o valor calculado à direita.
    reader = PdfReader(BytesIO(raw_content))
    # Comentário explicativo: Define ou atualiza `pages` com o valor calculado à direita.
    pages = []
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for i, page in enumerate(reader.pages, start=1):
        # Comentário explicativo: Define ou atualiza `text` com o valor calculado à direita.
        text = (page.extract_text() or "").strip()
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if text:
            pages.append(f"\n\n[Página {i}]\n{text}")
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return "\n".join(pages)


# Comentário explicativo: Define a função `main`, que encapsula uma parte específica da lógica do projeto.
def main():
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 70)
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("  REINGESTÃO LIMPA — PDFs do PGD")
    # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
    print("=" * 70)

    # ── Passo 1: Listar PDFs ──────────────────────────────────────────
    # Comentário explicativo: Define ou atualiza `pdf_files` com o valor calculado à direita.
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not pdf_files:
        print(f"\n  ❌ Nenhum PDF encontrado em {PDF_DIR}")
        # Comentário explicativo: Encerra a função neste ponto sem retornar um valor explícito.
        return

    print(f"\n  📄 {len(pdf_files)} PDFs encontrados em {PDF_DIR}:")
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for f in pdf_files:
        # Comentário explicativo: Define ou atualiza `size_kb` com o valor calculado à direita.
        size_kb = f.stat().st_size / 1024
        print(f"     • {f.name} ({size_kb:.0f} KB)")

    # ── Passo 2: Limpar ChromaDB existente ────────────────────────────
    print(f"\n  🗑️  Limpando ChromaDB em {VECTOR_DB_PATH}...")

    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if VECTOR_DB_PATH.exists():
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

        # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
        try:
            # Comentário explicativo: Define ou atualiza `col` com o valor calculado à direita.
            col = client.get_collection(name=COLLECTION_NAME)
            # Comentário explicativo: Define ou atualiza `old_count` com o valor calculado à direita.
            old_count = col.count()
            # Comentário explicativo: Define ou atualiza `client.delete_collection(name` com o valor calculado à direita.
            client.delete_collection(name=COLLECTION_NAME)
            print(f"     ✓ Collection '{COLLECTION_NAME}' removida ({old_count} chunks antigos)")
        # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
        except Exception:
            print(f"     ✓ Collection '{COLLECTION_NAME}' não existia")

        # Recriar collection limpa
        # Comentário explicativo: Define ou atualiza `collection` com o valor calculado à direita.
        collection = client.get_or_create_collection(
            # Comentário explicativo: Define ou atualiza `name` com o valor calculado à direita.
            name=COLLECTION_NAME,
            # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
            metadata={"hnsw:space": "cosine"},
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
    # Comentário explicativo: Define o caminho executado quando nenhuma condição anterior foi satisfeita.
    else:
        # Comentário explicativo: Importa o módulo `chromadb` para ser usado neste arquivo.
        import chromadb
        # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
        from chromadb.config import Settings

        # Comentário explicativo: Define ou atualiza `VECTOR_DB_PATH.mkdir(parents` com o valor calculado à direita.
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        # Comentário explicativo: Define ou atualiza `client` com o valor calculado à direita.
        client = chromadb.PersistentClient(
            # Comentário explicativo: Define ou atualiza `path` com o valor calculado à direita.
            path=str(VECTOR_DB_PATH),
            # Comentário explicativo: Define ou atualiza `settings` com o valor calculado à direita.
            settings=Settings(anonymized_telemetry=False),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )
        # Comentário explicativo: Define ou atualiza `collection` com o valor calculado à direita.
        collection = client.get_or_create_collection(
            # Comentário explicativo: Define ou atualiza `name` com o valor calculado à direita.
            name=COLLECTION_NAME,
            # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
            metadata={"hnsw:space": "cosine"},
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

    print(f"     ✓ Collection limpa criada")

    # ── Passo 3: Pipeline de ingestão ─────────────────────────────────
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from ingestion import ingest_and_anonymize
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from chunking import chunk_document
    # Comentário explicativo: Importa partes específicas de outro módulo/biblioteca para evitar escrever o caminho completo toda vez.
    from embeddings import generate_embeddings

    # Comentário explicativo: Define ou atualiza `total_chunks` com o valor calculado à direita.
    total_chunks = 0
    # Comentário explicativo: Define ou atualiza `resultados` com o valor calculado à direita.
    resultados = []

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for pdf_file in pdf_files:
        print(f"\n  📖 Processando: {pdf_file.name}...")

        # 3a. Extrair texto do PDF
        # Comentário explicativo: Define ou atualiza `raw_content` com o valor calculado à direita.
        raw_content = pdf_file.read_bytes()
        # Comentário explicativo: Define ou atualiza `raw_text` com o valor calculado à direita.
        raw_text = extract_pdf_text(raw_content)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not raw_text.strip():
            print(f"     ⚠️  PDF vazio ou sem texto extraível")
            # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
            continue

        # 3b. Anonimizar
        # Comentário explicativo: Define ou atualiza `cleaned_text` com o valor calculado à direita.
        cleaned_text = ingest_and_anonymize(raw_text)

        # 3c. Chunking semântico
        # Comentário explicativo: Define ou atualiza `metadata` com o valor calculado à direita.
        metadata = {
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "titulo": "Documento carregado",
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "fonte": pdf_file.name,
            # Comentário explicativo: Inclui este item/argumento dentro da estrutura ou chamada multilinha atual.
            "created_at": datetime.now(timezone.utc).isoformat(),
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        }
        # Comentário explicativo: Define ou atualiza `chunks` com o valor calculado à direita.
        chunks = chunk_document(cleaned_text, metadata)

        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if not chunks:
            print(f"     ⚠️  Nenhum chunk gerado")
            # Comentário explicativo: Pula o restante da iteração atual e continua o laço no próximo item.
            continue

        # 3d. Gerar embeddings
        # Comentário explicativo: Define ou atualiza `embedded_chunks` com o valor calculado à direita.
        embedded_chunks = generate_embeddings(chunks)

        # 3e. Persistir no ChromaDB
        # Comentário explicativo: Define ou atualiza `ids` com o valor calculado à direita.
        ids = [c["id"] for c in embedded_chunks]
        # Comentário explicativo: Define ou atualiza `embeddings` com o valor calculado à direita.
        embeddings = [c["embedding"] for c in embedded_chunks]
        # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
        documents = [c["texto"] for c in embedded_chunks]
        # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
        metadatas = [c["metadata"] for c in embedded_chunks]

        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        collection.add(
            # Comentário explicativo: Define ou atualiza `ids` com o valor calculado à direita.
            ids=ids,
            # Comentário explicativo: Define ou atualiza `embeddings` com o valor calculado à direita.
            embeddings=embeddings,
            # Comentário explicativo: Define ou atualiza `documents` com o valor calculado à direita.
            documents=documents,
            # Comentário explicativo: Define ou atualiza `metadatas` com o valor calculado à direita.
            metadatas=metadatas,
        # Comentário explicativo: Abre ou fecha uma estrutura de dados/chamada multilinha usada no bloco atual.
        )

        # Comentário explicativo: Define ou atualiza `total_chunks +` com o valor calculado à direita.
        total_chunks += len(embedded_chunks)
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        resultados.append((pdf_file.name, len(embedded_chunks)))
        print(f"     ✓ {len(embedded_chunks)} chunks indexados")

    # ── Passo 4: Resumo ──────────────────────────────────────────────
    print(f"\n  {'=' * 66}")
    print(f"  RESUMO DA INGESTÃO")
    print(f"  {'=' * 66}")
    print(f"\n  {'PDF':<40} {'Chunks':>8}")
    print(f"  {'─' * 48}")
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for nome, n in resultados:
        print(f"  {nome:<40} {n:>8}")
    print(f"  {'─' * 48}")
    print(f"  {'TOTAL':<40} {total_chunks:>8}")
    print(f"\n  ✅ Base limpa com {total_chunks} chunks únicos (collection: {COLLECTION_NAME})")
    print(f"  {'=' * 66}")


# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    main()
