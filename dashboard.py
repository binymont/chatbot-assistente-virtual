from flask import Flask, render_template_string, render_template, request, redirect, session, url_for
import sqlite3, os, bcrypt, secrets
from datetime import timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(hours=2)
TENANT_ID = os.getenv('TENANT_ID', 'pizzaria_ana')  # Multi-tenancy
DB_PATH = os.path.join(os.path.dirname(__file__), 'data/bot.db')

def criar_tabelas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS vendedores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, telefone TEXT UNIQUE, senha TEXT, tenant TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, itens TEXT, total REAL, status TEXT, pagamento TEXT, telefone TEXT, vendedor_id INTEGER, tenant TEXT)")
    conn.commit()
    conn.close()

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    criar_tabelas()
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        senha = request.form['senha']
        if not telefone.isdigit() or len(telefone) < 8:
            return 'Telefone inválido!'
        if len(senha) < 6:
            return 'Senha deve ter pelo menos 6 caracteres.'
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM vendedores WHERE telefone=? AND tenant=?", (telefone, TENANT_ID))
        if cursor.fetchone():
            conn.close()
            return 'Telefone já cadastrado! <a href="/login">Faça login</a>'
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT INTO vendedores (nome, telefone, senha, tenant) VALUES (?, ?, ?, ?)", (nome, telefone, senha_hash, TENANT_ID))
        conn.commit()
        conn.close()
        log_acao('sistema', 'registro_vendedor', f"{telefone}")
        return redirect('/login')
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    criar_tabelas()
    if request.method == 'POST':
        telefone = request.form['telefone']
        senha = request.form['senha']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, senha FROM vendedores WHERE telefone=? AND tenant=?", (telefone, TENANT_ID))
        vendedor = cursor.fetchone()
        conn.close()
        if vendedor and bcrypt.checkpw(senha.encode(), vendedor[2].encode()):
            session.permanent = True
            session['vendedor_id'] = vendedor[0]
            session['vendedor_nome'] = vendedor[1]
            log_acao(vendedor[0], 'login', None)
            return redirect(url_for('index'))
        else:
            return 'Telefone ou senha incorretos!'
    return render_template('login.html')

@app.route('/')
def index():
    criar_tabelas()
    if not session.get('vendedor_id'):
        return redirect(url_for('login'))
    vendedor_id = session['vendedor_id']
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE vendedor_id=? AND tenant=?", (vendedor_id, TENANT_ID))
    total_pedidos = cursor.fetchone()[0]
    cursor.execute("SELECT id, cliente, status, total, pagamento FROM pedidos WHERE vendedor_id=? AND tenant=? ORDER BY id DESC LIMIT ? OFFSET ?", (vendedor_id, TENANT_ID, per_page, offset))
    pedidos = cursor.fetchall()
    conn.close()
    total_pages = (total_pedidos // per_page) + (1 if total_pedidos % per_page else 0)
    html = """
    <h1>Meus Pedidos</h1>
    <table border=1><tr><th>ID</th><th>Cliente</th><th>Total</th><th>Status</th><th>Pagamento</th></tr>
    {% for p in pedidos %}
    <tr>
      <td>{{p[0]}}</td><td>{{p[1]}}</td><td>R$ {{p[3]:.2f}}</td><td>{{p[2]}}</td><td>{{p[4]}}</td>
    </tr>
    {% endfor %}
    </table>
    <div>Página: {{page}} de {{total_pages}}</div>
    {% if page > 1 %}<a href='/?page={{page-1}}'>Anterior</a>{% endif %}
    {% if page < total_pages %}<a href='/?page={{page+1}}'>Próxima</a>{% endif %}
    <a href="/admin">Ir para admin</a>
    <br><a href="/novo_pedido">Novo Pedido</a>
    """
    return render_template_string(html, pedidos=pedidos, page=page, total_pages=total_pages)
@app.route('/novo_pedido', methods=['GET', 'POST'])
def novo_pedido():
    if not session.get('vendedor_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        cliente = request.form['cliente']
        itens = request.form['itens']
        total = request.form['total']
        pagamento = request.form['pagamento']
        telefone = request.form['telefone']
        if not cliente or not itens or not total or not pagamento:
            return 'Preencha todos os campos! <a href="/novo_pedido">Voltar</a>'
        try:
            total_float = float(total)
            if total_float <= 0:
                return 'Total deve ser maior que zero! <a href="/novo_pedido">Voltar</a>'
        except:
            return 'Total inválido! <a href="/novo_pedido">Voltar</a>'
        vendedor_id = session['vendedor_id']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pedidos (cliente, itens, total, status, pagamento, telefone, vendedor_id, tenant) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (cliente, itens, total_float, 'pendente', pagamento, telefone, vendedor_id, TENANT_ID))
        conn.commit()
        conn.close()
        log_acao(vendedor_id, 'novo_pedido', f"Cliente: {cliente}, Total: {total_float}")
        return redirect('/')
    html = """
    <h1>Novo Pedido</h1>
    <form method='post'>
      <label>Cliente:</label><br><input type='text' name='cliente' required><br>
      <label>Itens:</label><br><textarea name='itens' rows='4' cols='40' required></textarea><br>
      <label>Total:</label><br><input type='number' name='total' step='0.01' required><br>
      <label>Pagamento:</label><br><input type='text' name='pagamento' required><br>
      <label>Telefone:</label><br><input type='text' name='telefone' required><br>
      <button type='submit'>Salvar Pedido</button>
    </form>
    <a href='/'>Voltar</a>
    """
    return render_template_string(html)
# Rota de recuperação de senha (início do fluxo)
@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        telefone = request.form['telefone']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM vendedores WHERE telefone=?", (telefone,))
        vendedor = cursor.fetchone()
        conn.close()
        if vendedor:
            # Aqui poderia ser enviado um código por WhatsApp/SMS
            return 'Em breve você receberá instruções para redefinir sua senha.'
        else:
            return 'Telefone não encontrado.'
    html = """
    <h1>Recuperar Senha</h1>
    <form method='post'>
      <label>Telefone:</label><br><input type='text' name='telefone' required><br>
      <button type='submit'>Recuperar</button>
    </form>
    <a href='/login'>Voltar</a>
    """
    return render_template_string(html)

@app.route('/admin')
def admin_dashboard():
    criar_tabelas()
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vendedores WHERE tenant=?", (TENANT_ID,))
    total_vendedores = cursor.fetchone()[0]
    cursor.execute("SELECT id, nome, telefone FROM vendedores WHERE tenant=? ORDER BY id LIMIT ? OFFSET ?", (TENANT_ID, per_page, offset))
    vendedores = cursor.fetchall()
    resumo = []
    for v in vendedores:
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM pedidos WHERE vendedor_id=? AND tenant=?", (v[0], TENANT_ID))
        qtd, total = cursor.fetchone()
        resumo.append({
            'id': v[0],
            'nome': v[1],
            'telefone': v[2],
            'qtd_vendas': qtd,
            'total_vendas': total
        })
    conn.close()
    total_pages = (total_vendedores // per_page) + (1 if total_vendedores % per_page else 0)
    html = """
    <h1>Dashboard Admin</h1>
    <table border=1><tr><th>ID</th><th>Nome</th><th>Telefone</th><th>Qtd Vendas</th><th>Total R$</th></tr>
    {% for r in resumo %}
    <tr>
      <td>{{r['id']}}</td><td>{{r['nome']}}</td><td>{{r['telefone']}}</td><td>{{r['qtd_vendas']}}</td><td>R$ {{r['total_vendas']:.2f}}</td>
    </tr>
    {% endfor %}
    </table>
    <div>Página: {{page}} de {{total_pages}}</div>
    {% if page > 1 %}<a href='/admin?page={{page-1}}'>Anterior</a>{% endif %}
    {% if page < total_pages %}<a href='/admin?page={{page+1}}'>Próxima</a>{% endif %}
    <a href="/">Voltar</a>
    """
    return render_template_string(html, resumo=resumo, page=page, total_pages=total_pages)
# Log de ações simples
def log_acao(usuario, acao, detalhes=None):
    with open('logs_acoes.txt', 'a', encoding='utf-8') as f:
        from datetime import datetime
        f.write(f"[{datetime.now()}] Usuário: {usuario} | Ação: {acao} | Detalhes: {detalhes}\n")
# Estrutura para testes automatizados
def test_novo_pedido():
    import tempfile
    db_test = tempfile.NamedTemporaryFile().name
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_test
    with app.test_client() as client:
        client.post('/registro', data={'nome':'Teste','telefone':'99999999','senha':'123456'})
        client.post('/login', data={'telefone':'99999999','senha':'123456'})
        rv = client.post('/novo_pedido', data={'cliente':'Cliente','itens':'Pizza','total':'50','pagamento':'pix','telefone':'99999999'})
        assert rv.status_code == 302

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Senha admin configurável por variável de ambiente
    senha_admin = os.getenv('ADMIN_PASSWORD', 'admin123')
    if request.method == 'POST':
        senha = request.form['senha']
        if senha == senha_admin:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return 'Senha incorreta!'
    return '''<form method="post"><input type="password" name="senha" placeholder="Senha admin"><button type="submit">Entrar</button></form>'''

if __name__ == '__main__':
    criar_tabelas()
    app.run(port=5050)