
import os
import requests
from dotenv import load_dotenv
from services.openai_service import gerar_resposta_ia, extrair_agendamento_natural
from db.database import (
    salvar_usuario, salvar_mensagem, buscar_historico, contar_usuarios, contar_mensagens,
    atualizar_nome_usuario, buscar_nome_usuario, salvar_agendamento, buscar_agendamentos,
    definir_lead, buscar_lead
)
from services.google_calendar_service import criar_evento_agenda

load_dotenv()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

def send_whatsapp_message(phone_number, text):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao enviar mensagem: {response.text}")

def gerar_resposta(mensagem):
    return gerar_resposta_ia(mensagem)

def handle_incoming_message(data):
    try:
        entry = data['entry'][0]['changes'][0]['value']['messages'][0]
        phone_number = entry['from']
        message = entry['text']['body']

        salvar_usuario(phone_number)
        salvar_mensagem(phone_number, message, 'recebida')

        msg_lower = message.strip().lower()
        resposta = None

        # Comandos fixos
        if msg_lower == '/historico':
            historico = buscar_historico(phone_number, limit=10)
            resposta = '\n'.join([
                f"[{tipo}] {mensagem} ({data})" for mensagem, tipo, data in reversed(historico)
            ]) or "Nenhum histórico encontrado."
        elif msg_lower == '/usuarios':
            resposta = f"Usuários cadastrados: {contar_usuarios()}"
        elif msg_lower == '/mensagens':
            resposta = f"Mensagens trocadas: {contar_mensagens()}"
        elif msg_lower == '/ajuda':
            resposta = (
                "Comandos disponíveis:\n"
                "/historico - Ver seu histórico de mensagens\n"
                "/usuarios - Quantidade de usuários cadastrados\n"
                "/mensagens - Quantidade de mensagens trocadas\n"
                "/nome SeuNome - Cadastrar/alterar seu nome\n"
                "/meunome - Ver seu nome cadastrado\n"
                "/lead quente|frio - Definir perfil de lead\n"
                "/meulead - Ver perfil de lead\n"
                "/agendar DD/MM/AAAA HH:MM Descrição - Agendar compromisso\n"
                "/meusagendamentos - Ver seus agendamentos\n"
            )
        elif msg_lower.startswith('/nome '):
            nome = message.strip()[6:].strip()
            if nome:
                atualizar_nome_usuario(phone_number, nome)
                resposta = f"Nome cadastrado/atualizado: {nome}"
            else:
                resposta = "Envie seu nome após o comando. Exemplo: /nome João"
        elif msg_lower == '/meunome':
            nome = buscar_nome_usuario(phone_number)
            resposta = f"Seu nome cadastrado: {nome}" if nome else "Você ainda não cadastrou seu nome. Use /nome SeuNome"
        elif msg_lower.startswith('/agendar '):
            try:
                partes = message.strip()[9:].strip().split(' ', 2)
                if len(partes) < 2:
                    resposta = "Formato inválido. Use: /agendar DD/MM/AAAA HH:MM Descrição"
                else:
                    data_str, hora_str = partes[0], partes[1]
                    descricao = partes[2] if len(partes) > 2 else "Agendamento"
                    from datetime import datetime
                    try:
                        data_hora = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M")
                        salvar_agendamento(phone_number, data_hora.isoformat(), descricao)
                        nome = buscar_nome_usuario(phone_number)
                        link = criar_evento_agenda(data_hora, descricao, usuario_nome=nome)
                        resposta = f"Agendamento registrado para {data_hora.strftime('%d/%m/%Y %H:%M')}: {descricao}\nEvento no Google Calendar: {link}"
                    except Exception:
                        resposta = "Data ou hora inválida. Use: /agendar DD/MM/AAAA HH:MM Descrição"
            except Exception:
                resposta = "Erro ao processar agendamento. Tente novamente."
        elif msg_lower == '/meusagendamentos':
            ags = buscar_agendamentos(phone_number, limit=5)
            if ags:
                resposta = '\n'.join([
                    f"{data_hora[:16].replace('T',' ')} - {descricao}" for data_hora, descricao, _ in ags
                ])
            else:
                resposta = "Nenhum agendamento encontrado."
        elif msg_lower.startswith('/lead '):
            tipo = message.strip()[6:].strip().lower()
            if tipo in ['quente', 'frio']:
                definir_lead(phone_number, tipo)
                resposta = f"Lead definido como: {tipo}"
            else:
                resposta = "Tipo de lead inválido. Use: /lead quente ou /lead frio"
        elif msg_lower == '/meulead':
            tipo = buscar_lead(phone_number)
            resposta = f"Seu perfil de lead: {tipo}"

        # Reconhecimento de intenção e agendamento por linguagem natural
        if resposta is None:
            resultado = extrair_agendamento_natural(message)
            if resultado:
                data_hora, descricao = resultado
                salvar_agendamento(phone_number, data_hora.isoformat(), descricao)
                nome = buscar_nome_usuario(phone_number)
                link = criar_evento_agenda(data_hora, descricao, usuario_nome=nome)
                resposta = f"Agendamento registrado para {data_hora.strftime('%d/%m/%Y %H:%M')}: {descricao}\nEvento no Google Calendar: {link}"
            else:
                resposta = gerar_resposta_ia(message)

        salvar_mensagem(phone_number, resposta, 'enviada')
        send_whatsapp_message(phone_number, resposta)

    except Exception as e:
        print(f"Erro no handler: {e}")
