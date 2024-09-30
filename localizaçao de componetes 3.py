import psycopg2
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Função para conectar ao banco de dados no Heroku
def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="ddmdls7is3k56s",
            user="u7mlau5r9lirar",
            password="p03053ab99235e5b9801cd7d602cb44a2ca2a0e4f42fb831b67c4fcce6f1d536b",
            host="c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
            port="5432"
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para verificar o usuário e a senha
def check_user(connection, nome, senha):
    cursor = connection.cursor()
    query = "SELECT * FROM usuarios WHERE nome = %s AND senha = %s"
    cursor.execute(query, (nome, senha))
    user = cursor.fetchone()
    cursor.close()
    return user is not None

# Função para buscar componente no banco de dados com aproximação
def buscar_componente(connection, nome_componente):
    cursor = connection.cursor()
    cursor.execute("SELECT nome FROM componentes")
    componentes = [row[0] for row in cursor.fetchall()]
    
    # Usando fuzzy matching para encontrar o nome mais próximo
    nome_encontrado, score = process.extractOne(nome_componente, componentes, scorer=fuzz.token_sort_ratio)

    if score >= 70:  # Definir um limite de similaridade para o nome
        cursor.execute("SELECT nome, quantidade, posicao FROM componentes WHERE nome = %s", (nome_encontrado,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado
    else:
        cursor.close()
        return None

# Função para atualizar o estoque
def atualizar_estoque(connection, nome_componente, acao, quantidade):
    cursor = connection.cursor()
    if acao == 'retirar':
        query = "UPDATE componentes SET quantidade = quantidade - %s WHERE nome = %s"
    elif acao == 'adicionar':
        query = "UPDATE componentes SET quantidade = quantidade + %s WHERE nome = %s"
    
    cursor.execute(query, (quantidade, nome_componente))
    connection.commit()
    cursor.close()

# Função principal
def main():
    connection = connect_to_db()
    if not connection:
        return
    
    # Verificar nome do usuário e senha
    while True:
        nome_usuario = input("Digite o nome do usuário: ")
        senha_usuario = input("Digite a senha: ")
        
        if check_user(connection, nome_usuario, senha_usuario):
            print("Usuário autenticado com sucesso!")
            break
        else:
            print("Nome de usuário ou senha incorretos. Tente novamente.")

    # Loop para busca e atualização de componentes
    while True:
        nome_componente = input("Digite o nome do componente que deseja buscar (ou 'sair' para encerrar): ")
        if nome_componente.lower() == 'sair':
            break

        resultado = buscar_componente(connection, nome_componente)
        if resultado:
            nome, quantidade, posicao = resultado
            print(f"Componente encontrado: {nome}")
            print(f"Quantidade: {quantidade}")
            print(f"Posição: {posicao}")
            
            # Perguntar ao usuário se deseja adicionar ou retirar
            acao = input("Deseja 'adicionar' ou 'retirar' o componente? (ou 'cancelar' para ignorar): ").lower()
            if acao in ['adicionar', 'retirar']:
                quantidade_modificar = int(input(f"Quantos deseja {acao}? "))
                atualizar_estoque(connection, nome, acao, quantidade_modificar)
                print(f"Quantidade de '{nome}' atualizada com sucesso!")
            else:
                print("Operação cancelada.")
        else:
            print("Componente não encontrado.")

    connection.close()

if __name__ == "__main__":
    main()
