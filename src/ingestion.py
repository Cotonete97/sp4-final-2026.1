# Comentário explicativo: Importa o módulo `re` para ser usado neste arquivo.
import re
# Comentário explicativo: Importa o módulo `spacy` para ser usado neste arquivo.
import spacy

# 🟡 4. CORREÇÃO: Variável global para lazy loading do spaCy
# Comentário explicativo: Define ou atualiza `_nlp` com o valor calculado à direita.
_nlp = None

# Comentário explicativo: Define a função `carregar_spacy`, que encapsula uma parte específica da lógica do projeto.
def carregar_spacy():
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Carrega o modelo do spaCy apenas quando necessário (Lazy Loading)."""
    # Comentário explicativo: Indica que a variável usada dentro da função é a variável global do módulo.
    global _nlp
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if _nlp is None:
        # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
        try:
            # Comentário explicativo: Define ou atualiza `_nlp` com o valor calculado à direita.
            _nlp = spacy.load("pt_core_news_sm")
        # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
        except OSError:
            # Comentário explicativo: Interrompe o fluxo normal e lança um erro com uma mensagem controlada.
            raise OSError("Modelo não encontrado. Execute: python -m spacy download pt_core_news_sm")
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return _nlp

# Comentário explicativo: Define a função `is_valid_luhn`, que encapsula uma parte específica da lógica do projeto.
def is_valid_luhn(n: str) -> bool:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    🔴 2. CORREÇÃO: Verifica se uma string numérica passa no algoritmo de Luhn.
    Garante que o número não é um protocolo ou ID qualquer, mas um cartão válido.
    """
    # Deixa apenas os números
    # Comentário explicativo: Define ou atualiza `n` com o valor calculado à direita.
    n = ''.join(filter(str.isdigit, n))
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not n or len(n) < 13: 
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return False
    
    # Comentário explicativo: Define ou atualiza `soma` com o valor calculado à direita.
    soma = 0
    # Comentário explicativo: Define ou atualiza `alt` com o valor calculado à direita.
    alt = False
    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for d in reversed(n):
        # Comentário explicativo: Define ou atualiza `d` com o valor calculado à direita.
        d = int(d)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if alt:
            # Comentário explicativo: Define ou atualiza `d *` com o valor calculado à direita.
            d *= 2
            # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
            if d > 9:
                # Comentário explicativo: Define ou atualiza `d -` com o valor calculado à direita.
                d -= 9
        # Comentário explicativo: Define ou atualiza `soma +` com o valor calculado à direita.
        soma += d
        # Comentário explicativo: Define ou atualiza `alt` com o valor calculado à direita.
        alt = not alt
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return soma % 10 == 0

# Comentário explicativo: Define a função `substituir_cartao`, que encapsula uma parte específica da lógica do projeto.
def substituir_cartao(match) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """Função auxiliar para o regex substituir apenas cartões reais."""
    # Comentário explicativo: Define ou atualiza `texto_capturado` com o valor calculado à direita.
    texto_capturado = match.group(0)
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if is_valid_luhn(texto_capturado):
        # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
        return '[CARTAO REMOVIDO]'
    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return texto_capturado

# Comentário explicativo: Define a função `ingest_and_anonymize`, que encapsula uma parte específica da lógica do projeto.
def ingest_and_anonymize(file_content: str) -> str:
    # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
    """
    Ingere um texto bruto, realiza limpeza estrutural e anonimiza dados sensíveis.
    """
    # 🟡 3. CORREÇÃO: Erro silencioso substituído por TypeError explícito
    # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
    if not isinstance(file_content, str):
        raise TypeError(f"Esperado string em file_content, recebido {type(file_content).__name__}")

    # =================================================================
    # ETAPA 1: Limpeza Estrutural Básica
    # =================================================================
    # Comentário explicativo: Define ou atualiza `texto_limpo` com o valor calculado à direita.
    texto_limpo = re.sub(r'\s+', ' ', file_content).strip()

    # =================================================================
    # ETAPA 2: Anonimização Contextual (spaCy - NER) — ANTES do regex
    # =================================================================
    # NER roda primeiro no texto limpo (sem placeholders de regex) para
    # evitar que textos como "[CARTAO REMOVIDO]" sejam interpretados como
    # entidades nomeadas.
    # Comentário explicativo: Define ou atualiza `nlp` com o valor calculado à direita.
    nlp = carregar_spacy()
    # Comentário explicativo: Define ou atualiza `doc` com o valor calculado à direita.
    doc = nlp(texto_limpo)
    # Comentário explicativo: Define ou atualiza `texto_anonimizado` com o valor calculado à direita.
    texto_anonimizado = texto_limpo

    # Comentário explicativo: Inicia um laço de repetição para percorrer itens de uma sequência ou coleção.
    for ent in reversed(doc.ents):
        # ℹ️ 6. CORREÇÃO: Adicionado 'ORG' (Organizações) além de 'PER' (Pessoas)
        # Comentário explicativo: Inicia uma condição: o bloco abaixo só roda se essa verificação for verdadeira.
        if ent.label_ in ["PER", "ORG"]:
            # Comentário explicativo: Define ou atualiza `inicio` com o valor calculado à direita.
            inicio = ent.start_char
            # Comentário explicativo: Define ou atualiza `fim` com o valor calculado à direita.
            fim = ent.end_char
            # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
            tipo = "NOME" if ent.label_ == "PER" else "ORGANIZAÇÃO"
            texto_anonimizado = texto_anonimizado[:inicio] + f"[{tipo} REMOVIDO]" + texto_anonimizado[fim:]

    # =================================================================
    # ETAPA 3: Anonimização Determinística (Expressões Regulares)
    # =================================================================
    # Regex roda DEPOIS do NER para não gerar placeholders que o NER
    # possa interpretar como entidades.

    # 🟡 5. CORREÇÃO: Regex para CPF aceitando formatos com ou sem pontuação explícita
    # Comentário explicativo: Define ou atualiza `texto_anonimizado` com o valor calculado à direita.
    texto_anonimizado = re.sub(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', '[CPF REMOVIDO]', texto_anonimizado)

    # Padrão para E-mails
    # Comentário explicativo: Define ou atualiza `texto_anonimizado` com o valor calculado à direita.
    texto_anonimizado = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REMOVIDO]', texto_anonimizado)

    # 🔴 1. CORREÇÃO: Telefone agora EXIGE DDD (ex: 11) para evitar que protocolos sejam capturados
    # Comentário explicativo: Define ou atualiza `texto_anonimizado` com o valor calculado à direita.
    texto_anonimizado = re.sub(r'\b(?:\+?55\s?)?\(?\d{2}\)?\s?(?:9\s?)?\d{4}[-\s]?\d{4}\b', '[TELEFONE REMOVIDO]', texto_anonimizado)

    # 🔴 2. CORREÇÃO: Integração do algoritmo de Luhn ao Regex de cartão de crédito
    # Comentário explicativo: Define ou atualiza `padrao_cartao` com o valor calculado à direita.
    padrao_cartao = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    # Comentário explicativo: Define ou atualiza `texto_anonimizado` com o valor calculado à direita.
    texto_anonimizado = re.sub(padrao_cartao, substituir_cartao, texto_anonimizado)

    # Comentário explicativo: Retorna o resultado desta função para quem chamou a função.
    return texto_anonimizado

# =================================================================
# TESTES DE MESA (Provando que as correções funcionam)
# =================================================================
# Comentário explicativo: Garante que o bloco abaixo rode apenas quando este arquivo for executado diretamente.
if __name__ == "__main__":
    # Comentário explicativo: Define ou atualiza `texto_bruto` com o valor calculado à direita.
    texto_bruto = """
    Documento de Teste de Falsos Positivos.
    Protocolo de atendimento: 1234-5678 (NÃO DEVE SUMIR)
    Data do sistema: 2025-1234 (NÃO DEVE SUMIR)
    ID do processo: 4321 8765 2109 6543 (NÃO DEVE SUMIR)
    
    Dados Reais:
    Ligar para Maria da Silva no (11) 98765-4321 ou email maria@teste.com.
    CPF sem ponto: 12345678900.
    A empresa Nubank processou o cartão 4111 1111 1111 1111.
    """
    
    # Comentário explicativo: Inicia um bloco protegido para capturar possíveis erros sem derrubar o programa imediatamente.
    try:
        # Comentário explicativo: Define ou atualiza `resultado` com o valor calculado à direita.
        resultado = ingest_and_anonymize(texto_bruto)
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("TEXTO ANONIMIZADO:\n", resultado)
        
        # Testando o TypeError
        # Comentário explicativo: Executa esta instrução como parte da lógica do arquivo.
        ingest_and_anonymize(123)
    # Comentário explicativo: Captura um erro específico e define como o programa deve reagir a ele.
    except TypeError as e:
        # Comentário explicativo: Exibe uma mensagem no terminal para teste, depuração ou orientação do usuário.
        print("\n[SUCESSO] Exceção capturada com sucesso:", e)
