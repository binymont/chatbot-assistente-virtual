def extrair_agendamento_natural(mensagem_usuario):
    """
    Usa IA para extrair data, hora e descrição de pedidos de agendamento em linguagem natural.
    Retorna (data_hora, descricao) ou None.
    """
    try:
        prompt = (
            "Extraia a data, hora e descrição de um pedido de agendamento na mensagem abaixo. "
            "Responda no formato: DATA;HORA;DESCRICAO. Se não houver agendamento, responda apenas 'NULO'.\nMensagem: " + mensagem_usuario
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=60
        )
        texto = response.choices[0].message.content.strip()
        if texto.upper() == 'NULO':
            return None
        partes = texto.split(';')
        if len(partes) >= 3:
            from datetime import datetime
            try:
                data_hora = datetime.strptime(f"{partes[0].strip()} {partes[1].strip()}", "%d/%m/%Y %H:%M")
                descricao = partes[2].strip()
                return data_hora, descricao
            except Exception:
                return None
        return None
    except Exception:
        return None
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "Você é um vendedor virtual extrovertido, simpático, paciente e empático. "
    "Responda de forma natural e humana, entendendo o contexto e intenção do cliente. "
    "Se o cliente quiser agendar, peça detalhes e confirme. Se pedir informações, explique com clareza. "
    "Nunca pareça um robô."
)

def gerar_resposta_ia(mensagem):
    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensagem}
            ],
            max_tokens=400,
            temperature=0.7
        )
        return resposta.choices[0].message.content.strip()
    except Exception:
        return "Desculpe, estou com dificuldades técnicas no momento."

def extrair_agendamento_natural(mensagem):
    """
    Usa IA para extrair data, hora e descrição de pedidos de agendamento em linguagem natural.
    Retorna (data_hora, descricao) ou None.
    """
    try:
        prompt = (
            "Extraia a data, hora e descrição de um pedido de agendamento na mensagem abaixo. "
            "Responda no formato: DATA;HORA;DESCRICAO. Se não houver agendamento, responda apenas 'NULO'.\nMensagem: " + mensagem
        )
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=60
        )
        texto = resposta.choices[0].message.content.strip()
        if texto.upper() == 'NULO':
            return None
        partes = texto.split(';')
        if len(partes) >= 3:
            from datetime import datetime
            try:
                data_hora = datetime.strptime(f"{partes[0].strip()} {partes[1].strip()}", "%d/%m/%Y %H:%M")
                descricao = partes[2].strip()
                return data_hora, descricao
            except Exception:
                return None
        return None
    except Exception:
        return None
