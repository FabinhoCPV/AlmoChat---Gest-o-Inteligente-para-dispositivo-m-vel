### Manual de Uso do Código

### pips do projeto:
### pip install psycopg2
### pip install fuzzywuzzy
### pip install python-Levenshtein
### pip install tabulate
### pip install bcrypt

# Este manual orienta como utilizar o código Python para gerenciar componentes no banco de dados PostgreSQL hospedado no Heroku, 
# incluindo pesquisa de componentes, retirada e adição de itens, e registro de transações.

# ---

# #### 1. **Instalação e Configuração**
# Certifique-se de ter o seguinte instalado:
# - Python 3.12+
# - Bibliotecas Python: `psycopg2`, `fuzzywuzzy`, `Levenshtein`, `datetime`

# Instale essas bibliotecas rodando:
# ```bash
# pip install psycopg2 fuzzywuzzy python-Levenshtein
# ```

# #### 2. **Acesso ao Banco de Dados**
# Antes de qualquer operação, você deve fornecer o nome do usuário e a senha que já estão cadastrados no banco de dados. 
# Se as credenciais estiverem corretas, o sistema permitirá a continuação.

# #### 3. **Fluxo de Uso**

# ##### **Passo 1: Autenticação**
# O código solicitará o nome de usuário e senha. Eles devem ser previamente cadastrados na tabela de `usuarios`. 
# Se a autenticação falhar, o programa será encerrado.

# **Exemplo:**
# ```
# Digite o nome de usuário: rogerio
# Digite a senha: 1234
# ```

# ##### **Passo 2: Buscar Componentes**
# Você pode digitar o nome de um componente para buscá-lo no banco de dados. Mesmo que o nome esteja com pequenos erros de digitação, 
# o sistema usa correspondência aproximada para encontrar o item correto.

# **Exemplo:**
# ```
# Digite o nome do componente que deseja buscar: Capacitor 1uF
# Resultado encontrado:
# Nome: Capacitor Poliester 1uF 250v
# Quantidade: 4
# Posição: A5.1
# ```

# ##### **Passo 3: Retirar ou Adicionar Componentes**
# Após a busca, o sistema perguntará se você deseja retirar ou adicionar componentes ao estoque.

# - **Para retirar**: O código perguntará quantos componentes deseja remover. A quantidade será subtraída do estoque e registrada na tabela `transacoes`.
# - **Para adicionar**: O código pedirá quantos componentes deseja adicionar, e a quantidade será incrementada no estoque.

# **Exemplo:**
# ```
# Deseja retirar ou adicionar componentes? (retirar/adicionar): retirar
# Quantos componentes deseja retirar?: 2
# Retirada de 2 unidades de Capacitor Poliester 1uF 250v.
# Quantidade atualizada: 2
# ```

# ##### **Passo 4: Registro de Transações**
# Cada vez que um componente é retirado, o sistema registra a transação com:
# - Nome do componente
# - Quantidade retirada
# - Data da transação
# - Usuário responsável

# Essas informações são salvas na tabela `transacoes`.

# ---

# #### 4. **Encerramento**
# Para encerrar o programa, você pode digitar `sair` no campo de busca de componentes, e o sistema será fechado.

# ---

# #### 5. **Erros Comuns**
# - **Autenticação Falhada**: Verifique se o nome de usuário e senha estão corretos.
# - **Componentes Não Encontrados**: Se o nome do componente estiver muito errado, a busca pode falhar. Tente digitar uma versão mais próxima do nome correto.

# Esse manual cobre os passos principais para usar o sistema de busca, retirada, adição e registro de transações de componentes no Heroku.

# ---
# Agora o sistema está pronto para ser utilizado!




import psycopg2
from fuzzywuzzy import process
from datetime import datetime

# Função para conectar ao banco de dados
def connect_db():
    return psycopg2.connect(
        host="c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
        database="ddmdls7is3k56s",
        user="u7mlau5r9lirar",
        password="p03053ab99235e5b9801cd7d602cb44a2ca2a0e4f42fb831b67c4fcce6f1d536b"
    )

# Função para validar usuário
def validar_usuario(cursor, nome_usuario, senha):
    cursor.execute("SELECT * FROM usuarios WHERE nome = %s AND senha = %s", (nome_usuario, senha))
    return cursor.fetchone()

# Função para buscar o componente usando fuzzy matching
def buscar_componente(cursor, nome_componente):
    cursor.execute("SELECT nome FROM componentes")
    todos_componentes = [row[0] for row in cursor.fetchall()]
    
    # Usando fuzzy matching para encontrar o componente mais próximo
    melhor_correspondencia = process.extractOne(nome_componente, todos_componentes)
    
    if melhor_correspondencia[1] >= 70:  # Limite de 70% para correspondência
        cursor.execute("SELECT * FROM componentes WHERE nome = %s", (melhor_correspondencia[0],))
        return cursor.fetchone()
    else:
        return None

# Função para registrar transação
def registrar_transacao(cursor, nome_componente, quantidade, usuario):
    data_atual = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        "INSERT INTO transacoes (nome_componente, quantidade, data, usuario) VALUES (%s, %s, %s, %s)",
        (nome_componente, quantidade, data_atual, usuario)
    )

# Função principal
def main():
    conn = connect_db()
    cursor = conn.cursor()

    nome_usuario = input("Digite seu nome de usuário: ")
    senha = input("Digite sua senha: ")

    if not validar_usuario(cursor, nome_usuario, senha):
        print("Usuário ou senha incorretos. Tente novamente.")
        return

    while True:
        nome_componente = input("\nDigite o nome do componente que deseja buscar (ou 'sair' para encerrar): ").strip()
        if nome_componente.lower() == 'sair':
            break
        
        componente = buscar_componente(cursor, nome_componente)
        if componente:
            print(f"Componente encontrado: {componente[2]}, Quantidade: {componente[3]}, Posição: {componente[4]}")
            
            acao = input("Você deseja 'retirar' ou 'adicionar' este componente? ").strip().lower()
            
            if acao == "retirar":
                quantidade = int(input("Quantos componentes deseja retirar? "))
                if quantidade <= componente[3]:  # Verifica se há quantidade suficiente
                    nova_quantidade = componente[3] - quantidade
                    cursor.execute("UPDATE componentes SET quantidade = %s WHERE id = %s", (nova_quantidade, componente[0]))
                    conn.commit()
                    
                    # Registra a transação
                    registrar_transacao(cursor, componente[2], -quantidade, nome_usuario)
                    
                    print(f"{quantidade} {componente[2]} retirados. Nova quantidade: {nova_quantidade}")
                else:
                    print("Quantidade insuficiente em estoque.")
            
            elif acao == "adicionar":
                quantidade = int(input("Quantos componentes deseja adicionar? "))
                nova_quantidade = componente[3] + quantidade
                cursor.execute("UPDATE componentes SET quantidade = %s WHERE id = %s", (nova_quantidade, componente[0]))
                conn.commit()

                # Registra a transação
                registrar_transacao(cursor, componente[2], quantidade, nome_usuario)
                
                print(f"{quantidade} {componente[2]} adicionados. Nova quantidade: {nova_quantidade}")
            
        else:
            print("Componente não encontrado.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
