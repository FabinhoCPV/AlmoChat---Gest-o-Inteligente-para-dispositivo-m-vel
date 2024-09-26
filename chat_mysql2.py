import streamlit as st
import mysql.connector
import difflib
import datetime
import hashlib

# Função para conectar ao banco de dados MySQL
def conectar_bd():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="estoque_componentes",
        autocommit=True
    )
    return conn

# Função para criar a tabela de usuários no banco de dados
def criar_tabela_usuarios():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL)''')
    conn.close()

# Função para criar a tabela de transações no banco de dados
def criar_tabela_transacoes():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transacoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT,
                    nome_componente VARCHAR(255) NOT NULL,
                    quantidade INT NOT NULL,
                    data DATETIME NOT NULL,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id))''')
    conn.close()

# Função para registrar um novo usuário no banco de dados
def registrar_usuario(username, password):
    conn = conectar_bd()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.close()

# Função para autenticar o usuário
def autenticar_usuario(username, password):
    conn = conectar_bd()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM usuarios WHERE username=%s AND password=%s", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user

# Função para localizar o componente pelo nome no banco de dados MySQL
def localizar_componente_por_nome(nome_componente_procurado):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM componentes")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        nome_componente_planilha = row[2]
        if isinstance(nome_componente_planilha, str):  
            similaridade = difflib.SequenceMatcher(None, nome_componente_procurado.lower(), nome_componente_planilha.lower()).ratio()
            if similaridade > 0.8:  
                return row[4], row[3], row[0]  
    return "Componente não encontrado com esse nome.", None, None

# Função para registrar uma transação no banco de dados
def registrar_transacao(id_usuario, nome_componente, quantidade):
    conn = conectar_bd()
    cursor = conn.cursor()
    data_transacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO transacoes (id_usuario, nome_componente, quantidade, data) VALUES (%s, %s, %s, %s)", (id_usuario, nome_componente, quantidade, data_transacao))
    conn.close()

# Função para remover um componente do banco de dados
def remover_componente(id_componente):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM componentes WHERE id=%s", (id_componente,))
    conn.close()

# Função principal
def main():
    criar_tabela_usuarios()
    criar_tabela_transacoes()

    st.title("Chatbot para Localização de Componentes")

    # Verificar se o usuário está autenticado
    if "username" not in st.session_state:
        st.subheader("Faça Login")
        username = st.text_input("Nome de usuário:")
        password = st.text_input("Senha:", type="password")

        if st.button("Login"):
            print("Tentando autenticar usuário...")
            user = autenticar_usuario(username, password)
            print("Resultado da autenticação:", user)
            if user:
                st.session_state.username = username
                print("Usuário autenticado com sucesso.")
            else:
                st.error("Credenciais inválidas. Tente novamente.")

    else:
        st.subheader("Logout")
        if st.button("Logout"):
            del st.session_state.username
            st.info("Você saiu com sucesso.")

        # Verificar se o usuário mestre está logado (id = 2)
        if st.session_state.username == 'usuario_mestre':
            st.subheader("Registrar Novo Usuário")
            novo_username =
            novo_username = st.text_input("Novo nome de usuário:")
            novo_password = st.text_input("Nova senha:", type="password")
            if st.button("Registrar-se"):
                if novo_username and novo_password:
                    registrar_usuario(novo_username, novo_password)
                    st.success("Usuário registrado com sucesso. Faça login para continuar.")
                else:
                    st.warning("Por favor, insira um nome de usuário e senha.")

        # Se o usuário estiver autenticado, permitir acesso ao chatbot
        # Solicitar ao usuário o nome do componente inicial
        nome_componente_procurado = st.text_input("Digite o nome do componente (ou 'sair' para encerrar): ")

        # Loop principal para receber mensagens do usuário
        while True:
            # Verificar se o usuário deseja sair
            if nome_componente_procurado.lower() == 'sair' or not nome_componente_procurado:
                if nome_componente_procurado.lower() == 'sair':
                    st.warning("Encerrando o chat...")
                break

            # Localizar o componente pelo nome
            endereco, quantidade, id_componente = localizar_componente_por_nome(nome_componente_procurado)

            if quantidade is not None:
                st.success(f"O componente '{nome_componente_procurado}' está localizado em '{endereco}' e a quantidade é {quantidade}.")

                # Solicitar a quantidade que o usuário deseja pegar
                quantidade_pegar = st.number_input("Quantidade a pegar:", min_value=1, max_value=int(quantidade), step=1)

                # Registrar a transação no banco de dados
                user = autenticar_usuario(st.session_state.username, "senha_qualquer")  # A senha não é usada aqui
                if user is not None:
                    id_usuario = user[0]
                    registrar_transacao(id_usuario, nome_componente_procurado, quantidade_pegar)

                    # Botão para retirar o componente do estoque
                    if st.button("Retirar Componente"):
                        remover_componente(id_componente)
                        st.success(f"Você retirou {quantidade_pegar} unidades do componente '{nome_componente_procurado}' do estoque.")
                else:
                    st.error("Usuário não autenticado.")

            else:
                st.error("Componente não encontrado.")

            # Solicitar ao usuário o nome do próximo componente
            nome_componente_procurado = st.text_input("Digite o nome do próximo componente (ou 'sair' para encerrar): ", key=f"componente-{nome_componente_procurado}")

# Executa a função principal
if __name__ == "__main__":
    main()
