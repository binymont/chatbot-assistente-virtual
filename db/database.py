def init_agenda_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            data_hora TEXT,
            descricao TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()

def salvar_agendamento(phone, data_hora, descricao):
    usuario_id = get_usuario_id(phone)
    if usuario_id is None:
        salvar_usuario(phone)
        usuario_id = get_usuario_id(phone)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agendamentos (usuario_id, data_hora, descricao) VALUES (?, ?, ?)", (usuario_id, data_hora, descricao))
    conn.commit()
    conn.close()

def buscar_agendamentos(phone, limit=5):
    usuario_id = get_usuario_id(phone)
    if usuario_id is None:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data_hora, descricao, criado_em FROM agendamentos WHERE usuario_id = ? ORDER BY data_hora DESC LIMIT ?", (usuario_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows
def atualizar_nome_usuario(phone, nome):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET nome = ? WHERE phone = ?", (nome, phone))
    conn.commit()
    conn.close()

def buscar_nome_usuario(phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE phone = ?", (phone,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else None
def contar_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def contar_mensagens():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mensagens")
    count = cursor.fetchone()[0]
    conn.close()
    return count
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/bot.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            nome TEXT,
            lead TEXT DEFAULT 'frio'
        )
    """)
def definir_lead(phone, tipo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET lead = ? WHERE phone = ?", (tipo, phone))
    conn.commit()
    conn.close()

def buscar_lead(phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT lead FROM usuarios WHERE phone = ?", (phone,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 'frio'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            mensagem TEXT,
            tipo TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()

def salvar_usuario(phone, nome=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE phone = ?", (phone,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO usuarios (phone, nome) VALUES (?, ?)", (phone, nome))
        conn.commit()
    conn.close()

def get_usuario_id(phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE phone = ?", (phone,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def salvar_mensagem(phone, mensagem, tipo):
    usuario_id = get_usuario_id(phone)
    if usuario_id is None:
        salvar_usuario(phone)
        usuario_id = get_usuario_id(phone)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mensagens (usuario_id, mensagem, tipo) VALUES (?, ?, ?)", (usuario_id, mensagem, tipo))
    conn.commit()
    conn.close()

def buscar_historico(phone, limit=20):
    usuario_id = get_usuario_id(phone)
    if usuario_id is None:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT mensagem, tipo, data FROM mensagens WHERE usuario_id = ? ORDER BY data DESC LIMIT ?", (usuario_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows
import sqlite3

DB_PATH = "data/bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            nome TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            mensagem TEXT,
            tipo TEXT, -- 'recebida' ou 'enviada'
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()

def salvar_usuario(phone, nome=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if nome:
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (phone, nome) VALUES (?, ?)
        """, (phone, nome))
    else:
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (phone) VALUES (?)
        """, (phone,))
    conn.commit()
    conn.close()

def salvar_mensagem(phone, mensagem, tipo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM usuarios WHERE phone = ?
    """, (phone,))
    usuario_id = cursor.fetchone()
    if usuario_id:
        cursor.execute("""
            INSERT INTO mensagens (usuario_id, mensagem, tipo) VALUES (?, ?, ?)
        """, (usuario_id[0], mensagem, tipo))
    conn.commit()
    conn.close()

def buscar_historico(phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.mensagem, m.tipo, m.data FROM mensagens m
        JOIN usuarios u ON m.usuario_id = u.id
        WHERE u.phone = ?
        ORDER BY m.data DESC
    """, (phone,))
    historico = cursor.fetchall()
    conn.close()
    return historico

# Chame init_db() ao iniciar o app
