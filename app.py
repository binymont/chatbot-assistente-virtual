from flask import Flask, request, jsonify
from handlers.message_handler import handle_incoming_message, gerar_resposta
import os
from dotenv import load_dotenv
from db.database import init_db, init_agenda_db


load_dotenv()
init_db()
init_agenda_db()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Rota de verificação para o webhook
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Token inválido", 403

# Rota de recebimento de mensagens (unificada)
@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()

    # Caso o payload venha do WhatsApp/Facebook
    if "entry" in dados:
        handle_incoming_message(dados)
        return "ok", 200

    # Caso seja um payload direto com texto (para testes)
    mensagem = dados.get("mensagem")
    if not mensagem:
        return jsonify({"erro": "mensagem ausente"}), 400

    resposta = gerar_resposta(mensagem)
    return jsonify({"resposta": resposta})

if __name__ == '__main__':
    app.run(port=5000)
