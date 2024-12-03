import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
import google.oauth2.credentials

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Necessário para sessões

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurações do Google OAuth2
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CLIENT_SECRETS_FILE = 'client_secret.json'
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # Ex: 'http://localhost:5000/oauth2callback'

# Inicializa o fluxo OAuth2
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=GOOGLE_SCOPES,
    redirect_uri=GOOGLE_REDIRECT_URI
)

@app.route('/')
def index():
    """
    Rota para a página inicial do cliente onde pode agendar serviços.
    """
    return render_template('index.html')

@app.route('/admin')
def admin():
    """
    Rota para a página de administração onde pode visualizar os agendamentos.
    """
    return render_template('admin.html')

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """
    API para criar um novo agendamento.
    Recebe dados do cliente, verifica ou cria o cliente no Supabase,
    cria o agendamento e adiciona um evento no Google Calendar.
    """
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    service = data.get('service')
    appointment_time_str = data.get('appointment_time')
    
    # Valida o formato da data e hora
    try:
        appointment_time = datetime.fromisoformat(appointment_time_str)
    except ValueError:
        return jsonify({'message': 'Formato de data e hora inválido.'}), 400

    # Verifica se o cliente já existe
    response = supabase.table('clients').select('*').eq('email', email).single().execute()
    if response.status_code != 200:
        return jsonify({'message': 'Erro ao acessar o Supabase.'}), 500
    
    client = response.data
    if client:
        client_id = client['id']
    else:
        # Cria um novo cliente
        new_client = supabase.table('clients').insert({
            'name': name,
            'email': email,
            'phone': phone
        }).execute()
        if new_client.status_code != 201:
            return jsonify({'message': 'Erro ao criar cliente.'}), 500
        client_id = new_client.data[0]['id']

    # Cria o agendamento
    appointment = supabase.table('appointments').insert({
        'client_id': client_id,
        'service': service,
        'appointment_time': appointment_time.isoformat()
    }).execute()
    if appointment.status_code != 201:
        return jsonify({'message': 'Erro ao criar agendamento.'}), 500

    # Adiciona o evento no Google Calendar
    event = add_event_to_google_calendar(service, appointment_time)
    if not event:
        return jsonify({'message': 'Agendamento criado, mas falha ao adicionar no Google Calendar.'}), 500

    return jsonify({'message': 'Agendamento criado com sucesso!'}), 201

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """
    API para obter todos os agendamentos com informações dos clientes.
    """
    response = supabase.table('appointments').select('*, clients(*)').execute()
    if response.status_code != 200:
        return jsonify({'message': 'Erro ao buscar agendamentos.'}), 500
    appointments = response.data
    return jsonify(appointments), 200

# Rotas para OAuth2 com Google
@app.route('/authorize')
def authorize():
    """
    Inicia o fluxo de autorização OAuth2 com o Google.
    """
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    """
    Callback para receber o código de autorização do Google.
    """
    state = session.get('state', None)
    if not state:
        return 'Estado não encontrado na sessão.', 400

    flow.fetch_token(authorization_response=request.url)

    if not flow.credentials:
        return 'Falha ao obter credenciais.', 400

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('index'))

def credentials_to_dict(credentials):
    """
    Converte as credenciais em um dicionário para armazenamento na sessão.
    """
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def add_event_to_google_calendar(summary, start_time):
    """
    Adiciona um evento ao Google Calendar usando as credenciais armazenadas na sessão.
    """
    if 'credentials' not in session:
        # Redireciona para autorização se as credenciais não estiverem disponíveis
        return redirect(url_for('authorize'))

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': (start_time + timedelta(hours=1)).isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        # Atualiza as credenciais na sessão
        session['credentials'] = credentials_to_dict(credentials)
        return event
    except Exception as e:
        print(f"Falha ao adicionar evento no Google Calendar: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
