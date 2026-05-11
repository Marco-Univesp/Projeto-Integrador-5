import sqlite3

conn = sqlite3.connect("banco.db")
cur = conn.cursor()

cur.executescript("""
ALTER TABLE descarte RENAME TO descarte_old;

CREATE TABLE descarte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    motivo TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    imagem TEXT
);

INSERT INTO descarte (id, nome, motivo, quantidade, imagem)
SELECT id, nome, motivo, quantidade, imagem FROM descarte_old;

DROP TABLE descarte_old;
""")


conn.commit()
conn.close()
print("Tabela descarte recriada com sucesso!")
