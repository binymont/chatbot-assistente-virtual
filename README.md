# 🤖 Chatbot Assistente Virtual

Bem-vindo ao **Chatbot Assistente Virtual**, um bot inteligente desenvolvido em Python com **Flask**, capaz de interagir com usuários, responder perguntas, enviar e-mails, gerar PDFs e integrar com serviços como **Google Calendar** e **OpenAI GPT**.

---

## 💡 Objetivo do Projeto

Este projeto tem como objetivo criar um assistente virtual que:

- Responda perguntas de forma inteligente.
- Gere arquivos PDF.
- Envie notificações por e-mail.
- Integre com o Google Calendar para gerenciamento de eventos.
- Sirva como base para aprendizado e expansão de bots inteligentes.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.12**
- **Flask** – Framework web para criação de APIs e interfaces.
- **OpenAI GPT** – Para geração de respostas inteligentes.
- **SQLite** – Banco de dados leve para armazenamento local.
- **JSON** – Configurações do bot.
- **HTML/CSS** – Templates para interface web.
- **Bibliotecas auxiliares**:
  - `requests`
  - `python-dotenv`
  - `flask-login`
  - `flask_sqlalchemy`
  - `fpdf2`
  - `google-api-python-client`
  - `google-auth`

---

## 📂 Estrutura do Projeto

bot/
├── app.py # Arquivo principal da aplicação Flask
├── bot_config.json # Configurações do bot (ex.: respostas padrão)
├── dashboard.py # Dashboard administrativo
├── gpt.py # Integração com GPT
├── db/
│ └── database.py # Configuração do banco de dados SQLite
├── handlers/
│ └── message_handler.py # Lógica de processamento das mensagens
├── services/
│ ├── email_service.py # Envio de e-mails
│ ├── google_calendar_service.py # Integração com Google Calendar
│ ├── openai_service.py # Chamadas à API do GPT
│ └── pdf_service.py # Geração de PDFs
├── templates/
│ ├── login.html # Tela de login
│ └── registro.html # Tela de registro
├── .gitignore # Arquivos ignorados pelo Git
└── requirements.txt # Dependências do projeto

yaml
Copiar código

---

## ⚙️ Configuração do Ambiente

1. Clone o repositório:

```bash
git clone https://github.com/binymont/chatbot-assistente-virtual.git
cd chatbot-assistente-virtual
Crie um ambiente virtual (recomendado):

bash
Copiar código
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac
Instale as dependências:

bash
Copiar código
pip install -r requirements.txt
Crie um arquivo .env na raiz do projeto (não comitar no Git!) com suas chaves de API:

ini
Copiar código
OPENAI_API_KEY=Sua_Chave_OpenAI
EMAIL_USER=seu_email@exemplo.com
EMAIL_PASS=sua_senha_de_email
GOOGLE_CREDENTIALS_JSON=caminho/para/credentials.json
🚀 Executando o Chatbot
Para iniciar a aplicação:

bash
Copiar código
python app.py
Acesse no navegador:

cpp
Copiar código
http://127.0.0.1:5000
📝 Funcionalidades
Login/Registro: Controle de usuários para acesso ao bot.

Processamento de Mensagens: Interpreta mensagens enviadas pelo usuário.

Geração de PDFs: Cria PDFs com informações ou respostas.

Envio de E-mails: Dispara e-mails com notificações ou relatórios.

Google Calendar: Cria e gerencia eventos automaticamente.

GPT Integration: Respostas inteligentes baseadas no modelo GPT.

🔐 Boas Práticas
Nunca comitar arquivos com chaves de API ou senhas (.env).

Adicione sempre .env no .gitignore.

Faça commits pequenos e claros.

Use branches separadas para novas funcionalidades.

💻 Contribuindo
Faça um fork do projeto.

Crie uma branch para sua feature: git checkout -b minha-feature.

Faça commits claros: git commit -m "Descrição da feature".

Envie para seu fork: git push origin minha-feature.

Abra um Pull Request para o repositório original.

📄 Licença
Este projeto está licenciado sob a Licença MIT.

⚡ Contato
Desenvolvido por Sabriny Monteiro
GitHub: https://github.com/binymont
