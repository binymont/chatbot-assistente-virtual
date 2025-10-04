def notificar_agendamento(phone, data_hora, descricao, vendedor_phone):
    # Exemplo: enviar mensagem para o vendedor (pode ser WhatsApp, e-mail, etc.)
    # Aqui, apenas um print, mas pode integrar com send_whatsapp_message ou e-mail
    print(f"[NOTIFICAÇÃO] Novo agendamento de {phone} para {data_hora}: {descricao} (Vendedor: {vendedor_phone})")
import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Caminho para o arquivo de credenciais do Google Service Account
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

def criar_evento_agenda(data_hora, descricao, usuario_nome=None):
    """
    Cria um evento no Google Calendar.
    data_hora: datetime.datetime
    descricao: str
    usuario_nome: str (opcional)
    """
    evento = {
        "summary": f"Agendamento: {usuario_nome or ''}",
        "description": descricao,
        "start": {"dateTime": data_hora.isoformat(), "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": (data_hora + datetime.timedelta(hours=1)).isoformat(), "timeZone": "America/Sao_Paulo"},
    }
    evento = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=evento).execute()
    return evento.get("htmlLink")
