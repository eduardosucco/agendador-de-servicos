import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Necessário para sessões

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    Recebe dados do cliente, verifica ou cria o cliente no Supabase e cria o agendamento.
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

if __name__ == '__main__':
    app.run(debug=True)
