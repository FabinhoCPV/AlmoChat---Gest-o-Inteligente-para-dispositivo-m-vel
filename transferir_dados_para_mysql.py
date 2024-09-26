import mysql.connector
import csv

# Conectar-se ao servidor MySQL
conn_mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    autocommit=True
)

# Criar um cursor para executar consultas SQL
cursor = conn_mysql.cursor()

# Criar o novo banco de dados se não existir
cursor.execute("CREATE DATABASE IF NOT EXISTS estoque_componentes")

print("Banco de dados 'estoque_componentes' criado com sucesso!")

# Selecionar o banco de dados recém-criado
cursor.execute("USE estoque_componentes")

# Script SQL para criar a tabela 'componentes' se não existir
sql_create_table = """
CREATE TABLE IF NOT EXISTS componentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(255),
    nome VARCHAR(255),
    quantidade INT,
    posicao VARCHAR(255)
)
"""

cursor.execute(sql_create_table)

print("Tabela 'componentes' criada com sucesso!")

# Fechar o cursor
cursor.close()

# Reconectar-se ao banco de dados 'estoque_componentes'
conn_mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="estoque_componentes",
    autocommit=True
)

# Criar um novo cursor para inserir os dados
cursor = conn_mysql.cursor()

# Inserir dados do arquivo CSV na tabela 'componentes'
with open('arquivo_csv.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Pula o cabeçalho se houver

    for row in csvreader:
        codigo = row[1]  # Coluna B
        nome = row[2]  # Coluna C
        quantidade_str = row[3]  # Coluna D
        posicao = row[4]  # Coluna E

        try:
            quantidade = int(quantidade_str)
        except ValueError:
            print(f"Erro: Valor inválido '{quantidade_str}' na coluna de quantidade. Pulando linha...")
            continue

        # Inserir os dados na tabela 'componentes'
        cursor.execute("INSERT INTO componentes (codigo, nome, quantidade, posicao) VALUES (%s, %s, %s, %s)", (codigo, nome, quantidade, posicao))

print("Dados inseridos com sucesso!")

# Fechar o cursor e a conexão
cursor.close()
conn_mysql.close()
