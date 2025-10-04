import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_config():
    with open("bot_config.json") as f:
        return json.load(f)

config = load_config()

def gerar_resposta(mensagem_usuario):
    prompt = (
        f"{config['resposta_padrao']}\n"
        f"Tonalidade: {config['tonalidade']}\n"
        f"Usuário: {mensagem_usuario}\n"
        f"Resposta:"
    )

    resposta = openai.ChatCompletion.create(
        model="gpt-4",  # ou gpt-3.5-turbo
        messages=[
            {"role": "system", "content": prompt}
        ],
        max_tokens=100
    )

    return resposta['choices'][0]['message']['content'].strip()
