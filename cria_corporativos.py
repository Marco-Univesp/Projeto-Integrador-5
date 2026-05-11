import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "banco.db")

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS corporativos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insere usuário admin se não existir
cur.execute("SELECT * FROM corporativos WHERE email = ?", ("admin@reloop.com.br",))
if not cur.fetchone():
    cur.execute(
        """
        INSERT INTO corporativos (nome, email, senha)
        VALUES (?, ?, ?)
    """,
        ("Admin", "admin@reloop.com.br", "@dm2026"),
    )
    print("Usuário admin criado.")

conn.commit()
conn.close()

print("Tabela corporativos criada/verificada com sucesso!")
