import sqlite3

def criar_estrutura():
    # Conecta ao arquivo de banco de dados (se não existir, ele cria)
    conn = sqlite3.connect('gestao_enps.db')
    cursor = conn.cursor()

    # 1. Tabela de Usuários (Login e Permissões)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL -- 'ADM' ou 'USER'
        )
    ''')

    # 2. Tabela de Respostas (Coleta do eNPS)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            unidade TEXT NOT NULL, -- SESI, SENAI, IEL, FIEAC
            nota INTEGER NOT NULL,
            comentario TEXT,
            data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
        )
    ''')

    # 3. Criar o primeiro Administrador padrão (João Victor)
    # Senha padrão inicial: 'fieac123' (Em um sistema real, usaríamos criptografia)
    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, usuario, senha, perfil)
            VALUES (?, ?, ?, ?)
        ''', ('João Victor', 'joao.adm', 'fieac123', 'ADM'))
        conn.commit()
        print("Sistema fundado com sucesso! Usuário ADM 'joao.adm' criado.")
    except sqlite3.IntegrityError:
        print("O banco já existe e o usuário ADM já está cadastrado.")

    conn.close()

if __name__ == "__main__":
    criar_estrutura()