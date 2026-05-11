import os
import sqlite3
from flask import (
    Flask,
    jsonify,
    render_template,
    g,
    request,
    redirect,
    url_for,
    flash,
    session,
)

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_qualquer"
DATABASE = "banco.db"

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------- CONEXÃO COM BANCO ---------------------- #


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# ---------------------- ROTAS CORPORATIVO ---------------------- #


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/logincorp", methods=["GET", "POST"])
def login_corporativo():
    if request.method == "GET":
        return render_template("logincorp.html")

    email = request.form.get("email")
    senha = request.form.get("senha")

    conn = get_db_connection()
    corporativo = conn.execute(
        "SELECT * FROM corporativos WHERE email = ? AND senha = ?", (email, senha)
    ).fetchone()
    conn.close()

    if corporativo:
        session["corp_id"] = corporativo["id"]
        session["corp_nome"] = corporativo["nome"]
        flash("✅ Login corporativo realizado com sucesso!", "success")
        return redirect(url_for("painel_admin"))
    else:
        flash("❌ Email ou senha inválidos.", "danger")
        return redirect(url_for("login_corporativo"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("index"))


@app.route("/painel_admin")
def painel_admin():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, pedido, nome, motivo, imagem, preco, quantidade, status
        FROM devolucoes
        ORDER BY id DESC
    """)
    devolucoes = cur.fetchall()
    conn.close()
    return render_template("painel_admin.html", devolucoes=devolucoes)


@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    devolucoes_pendentes = conn.execute(
        "SELECT COUNT(*) FROM devolucoes WHERE status = 'Pendente'"
    ).fetchone()[0]
    estoque_fisico = conn.execute("SELECT COUNT(*) FROM estoque_fisico").fetchone()[0]
    cur.execute("SELECT motivo, COUNT(*) FROM devolucoes GROUP BY motivo")
    resultados = cur.fetchall()
    labels = [row[0] for row in resultados]
    valores = [row[1] for row in resultados]
    conn.close()
    return render_template(
        "dashboard.html",
        total_clientes=total_clientes,
        devolucoes_pendentes=devolucoes_pendentes,
        estoque_fisico=estoque_fisico,
        labels=labels,
        valores=valores,
    )


@app.route("/atualizar_status/<int:id>", methods=["POST"])
def atualizar_status(id):
    novo_status = request.form.get("status")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE devolucoes SET status = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()
    flash("✅ Status atualizado com sucesso!", "success")
    return redirect(url_for("painel_admin"))


# ---------------------- ROTAS CLIENTE ---------------------- #


@app.route("/cliente")
def cliente():
    return render_template("cliente.html")


@app.route("/cadastroc", methods=["GET", "POST"])
def cadastroc():
    if request.method == "GET":
        return render_template("cadastroc.html")
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")
    email = request.form.get("email")
    senha = request.form.get("senha")
    confirmar_senha = request.form.get("confirmarSenha")
    if senha != confirmar_senha:
        return jsonify({"status": "error", "message": "As senhas não conferem."})
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO clientes (nome, email, cpf, senha) VALUES (?, ?, ?, ?)",
            (nome, email, cpf, senha),
        )
        conn.commit()
        conn.close()
        return jsonify(
            {"status": "success", "message": "Cliente cadastrado com sucesso!"}
        )
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "error", "message": "Email já cadastrado."})


@app.route("/loginc", methods=["GET", "POST"])
def loginc():
    if request.method == "GET":
        return render_template("loginc.html")
    cpf = request.form.get("cpf")
    email = request.form.get("email")
    senha = request.form.get("senha")
    conn = get_db_connection()
    cliente = conn.execute(
        "SELECT * FROM clientes WHERE cpf = ? AND email = ? AND senha = ?",
        (cpf, email, senha),
    ).fetchone()
    conn.close()
    if cliente:
        session["user_id"] = cliente["id"]
        session["nome"] = cliente["nome"]
        return jsonify({"status": "success", "message": "Login realizado com sucesso!"})
    else:
        return jsonify({"status": "error", "message": "CPF, email ou senha inválidos."})


@app.route("/menu_cliente")
def menu_cliente():
    return render_template("menu_cliente.html")


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/registro_devolucao", methods=["GET", "POST"])
def registro_devolucao():
    if request.method == "POST":
        customer_id = session.get("user_id")
        if not customer_id:
            flash(
                "⚠️ É necessário estar logado para registrar uma devolução.", "warning"
            )
            return redirect(url_for("loginc"))
        pedido = request.form.get("pedido")
        nome = request.form.get("nome")
        motivo = request.form.get("motivo")
        imagem = request.files.get("imagem")
        imagem_nome = None
        if imagem:
            imagem_nome = imagem.filename
            caminho = os.path.join(UPLOAD_FOLDER, imagem_nome)
            imagem.save(caminho)
        preco = request.form.get("preco")
        quantidade = request.form.get("quantidade")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO devolucoes (pedido, nome, motivo, imagem, preco, quantidade, customer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (pedido, nome, motivo, imagem_nome, preco, quantidade, customer_id),
        )
        conn.commit()
        conn.close()
        flash("✅ Devolução registrada e aguardando aprovação.", "success")
        return redirect(url_for("menu_cliente"))
    return render_template("registro_devolucao.html")


@app.route("/minhas_devolucoes")
def minhas_devolucoes():
    customer_id = session.get("user_id")
    if not customer_id:
        flash(
            "⚠️ É necessário estar logado para visualizar suas devoluções.", "warning"
        )
        return redirect(url_for("loginc"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # garante acesso por chave
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, pedido, nome, motivo, imagem, preco, quantidade, ponto, status
        FROM devolucoes
        WHERE customer_id = ?
        ORDER BY pedido DESC
    """,
        (customer_id,),
    )
    devolucoes = cur.fetchall()
    conn.close()

    return render_template("minhas_devolucoes.html", devolucoes=devolucoes)


@app.route("/status")
def status_devolucao():
    return render_template("status.html")


@app.route("/embalar")
def embalar():
    return render_template("embalar.html")


@app.route("/pontos")
def pontos():
    return render_template("pontos.html")


@app.route("/status_cliente")
def status_cliente():
    return render_template("status_cliente.html")


@app.route("/etiqueta/<int:id>")
def gerar_etiqueta(id):
    db = get_db()
    item = db.execute("SELECT * FROM devolucoes WHERE id = ?", (id,)).fetchone()
    if not item:
        flash("❌ Devolução não encontrada.", "danger")
        return redirect(url_for("minhas_devolucoes"))
    return render_template("etiqueta.html", item=item)


# ---------------------- ROTAS ESTOQUE ---------------------- #


@app.route("/estoqueDevolucao")
def estoque_devolucao():
    db = get_db()
    devolucoes = db.execute("SELECT * FROM devolucoes").fetchall()
    lista = []
    for d in devolucoes:
        item = dict(d)
        if item["preco"] is None:
            item["preco"] = 0.0
        lista.append(item)
    return render_template("estoqueDevolucao.html", devolucoes=lista)


@app.route("/estoque_fisico")
def estoque_fisico():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM estoque_fisico")
    itens = cur.fetchall()
    conn.close()
    return render_template("estoque_fisico.html", itens=itens)


# mover estoque físico para descarte
@app.route("/mover_estoque_para_descarte/<int:id>", methods=["POST"])
def mover_para_descarte_estoque(id):
    db = get_db()
    item = db.execute("SELECT * FROM estoque_fisico WHERE id = ?", (id,)).fetchone()
    if item:
        db.execute(
            """
            INSERT INTO descarte (nome, motivo, quantidade, imagem)
            VALUES (?, ?, ?, ?)
        """,
            (item["nome"], "Descarte manual", item["quantidade"], None),
        )
        db.execute("DELETE FROM estoque_fisico WHERE id = ?", (id,))
        db.commit()
        flash("✅ Item movido para descarte com sucesso!", "success")
        return redirect(url_for("estoque_fisico"))
    flash("❌ Item não encontrado no estoque físico.", "danger")
    return redirect(url_for("estoque_fisico"))


@app.route("/atualizar_quantidade/<int:id>", methods=["POST"])
def atualizar_quantidade(id):
    nova_qtd = request.form.get("quantidade")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE estoque_fisico SET quantidade = ? WHERE id = ?", (nova_qtd, id))
    conn.commit()
    conn.close()
    flash("✅ Quantidade atualizada com sucesso!", "success")
    return redirect(url_for("estoque_fisico"))


@app.route("/atualizar_status_estoque/<int:id>", methods=["POST"])
def atualizar_status_estoque(id):
    novo_status = request.form.get("status_estoque")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE estoque_fisico SET status_estoque = ? WHERE id = ?", (novo_status, id)
    )
    conn.commit()
    conn.close()
    flash("✅ Status do estoque atualizado com sucesso!", "success")
    return redirect(url_for("estoque_fisico"))


@app.route("/descarte")
def descarte():
    db = get_db()
    itens = db.execute("SELECT * FROM descarte").fetchall()
    return render_template("descarte.html", itens=itens)


@app.route("/atualizar_quantidade_descarte/<int:id>", methods=["POST"])
def atualizar_quantidade_descarte(id):
    nova_qtd = request.form.get("quantidade")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE descarte SET quantidade = ? WHERE id = ?", (nova_qtd, id))
    conn.commit()
    conn.close()
    flash("✅ Quantidade de descarte atualizada!", "success")
    return redirect(url_for("descarte"))


# ---------------------- MOVIMENTAÇÃO ---------------------- #


# mover devolução para estoque físico
@app.route("/mover_para_estoque_fisico/<int:id>", methods=["POST"])
def mover_para_estoque_fisico(id):
    db = get_db()
    item = db.execute("SELECT * FROM devolucoes WHERE id = ?", (id,)).fetchone()
    if item:
        db.execute(
            """
            INSERT INTO estoque_fisico (nome, categoria, quantidade, preco, status_estoque)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                item["nome"],
                "Categoria",
                item["quantidade"],
                item["preco"],
                "Em Estoque",
            ),
        )
        db.execute("DELETE FROM devolucoes WHERE id = ?", (id,))
        db.commit()
        flash("✅ Item movido para estoque físico com sucesso!", "success")
        return redirect(url_for("painel_admin"))
    flash("❌ Item não encontrado na lista de devoluções.", "danger")
    return redirect(url_for("painel_admin"))


# mover devolução para descarte
@app.route("/mover_para_descarte/<int:id>", methods=["POST"])
def mover_para_descarte_devolucao(id):
    db = get_db()
    item = db.execute("SELECT * FROM devolucoes WHERE id = ?", (id,)).fetchone()
    if item:
        db.execute(
            """
            INSERT INTO descarte (nome, motivo, quantidade, imagem)
            VALUES (?, ?, ?, ?)
        """,
            (item["nome"], item["motivo"], item["quantidade"], item["imagem"]),
        )
        db.execute("DELETE FROM devolucoes WHERE id = ?", (id,))
        db.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Item não encontrado"}), 404


# mover estoque físico para descarte
@app.route("/mover_estoque_para_descarte/<int:id>", methods=["POST"])

# ---------------------- ERRO 404 ---------------------- #


@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("404.html"), 404


# ---------------------- MAIN ---------------------- #

if __name__ == "__main__":
    app.run(debug=True)
