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
