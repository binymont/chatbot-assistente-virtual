
from fpdf import FPDF
import os
import requests


def gerar_comanda_pdf(pedido, cliente, caminho_pdf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Comanda de Pedido - Pizzaria", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Itens do Pedido:", ln=True)
    pdf.ln(5)
    for item in pedido['itens']:
        detalhes = item.get('detalhes', '')
        pdf.cell(200, 10, txt=f"- {item['quantidade']}x {item['nome']} ({detalhes})", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total: R$ {pedido['total']:.2f}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Endereço: {pedido.get('endereco','')}", ln=True)
    pdf.cell(200, 10, txt=f"Pagamento: {pedido.get('pagamento','')}", ln=True)
    pdf.output(caminho_pdf)
    return caminho_pdf


def enviar_pdf_whatsapp(phone_number, caminho_pdf, whatsapp_token, whatsapp_phone_id):
    url = f"https://graph.facebook.com/v17.0/{whatsapp_phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}"
    }
    files = {
        'file': (os.path.basename(caminho_pdf), open(caminho_pdf, 'rb'), 'application/pdf')
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "document",
        "document": {"filename": os.path.basename(caminho_pdf)}
    }
    response = requests.post(url, headers=headers, data={"messaging_product": "whatsapp", "to": phone_number, "type": "document"}, files=files)
    if response.status_code != 200:
        print(f"Erro ao enviar PDF por WhatsApp: {response.text}")
    else:
        print("PDF enviado com sucesso!")
