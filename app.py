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
    Rota para a página inicial (se necessário).
    """
    return jsonify({'message': 'Servidor funcionando. Use o Jotform para agendar!'})

@app.route('/admin')
def admin():
    """
    Rota para a administração de agendamentos.
    """
    return jsonify({'message': 'Área administrativa em construção!'})

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    app.logger.info("Webhook acionado!")
    try:
        data = request.json
        app.logger.info(f"Dados recebidos: {data}")
        
        # Mapear os campos
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        service = data.get('service')
        appointment_time_str = data.get('appointment_time')

        # Verificar dados recebidos
        if not all([name, email, phone, service, appointment_time_str]):
            app.logger.error("Dados incompletos recebidos.")
            return jsonify({'message': 'Dados incompletos recebidos.'}), 400

        # Validar formato de data e hora
        try:
            appointment_time = datetime.fromisoformat(appointment_time_str)
        except ValueError as e:
            app.logger.error(f"Erro de conversão de data: {e}")
            return jsonify({'message': 'Formato de data e hora inválido.'}), 400

        # Validar horário
        start_time = appointment_time.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time = appointment_time.replace(hour=19, minute=0, second=0, microsecond=0)
        if appointment_time < start_time or appointment_time > end_time or appointment_time.minute != 0:
            app.logger.error("Horário inválido.")
            return jsonify({'message': 'Horário inválido. Escolha horários de 1h em 1h, entre 08:00 e 19:00.'}), 400

        # Verificar ou criar cliente no Supabase
        response = supabase.table('clients').select('*').eq('email', email).single().execute()
        app.logger.info(f"Resposta Supabase (SELECT): {response.data}")

        client = response.data
        if not client:
            new_client = supabase.table('clients').insert({
                'name': name,
                'email': email,
                'phone': phone
            }).execute()
            app.logger.info(f"Cliente criado: {new_client.data}")
            client_id = new_client.data[0]['id']
        else:
            client_id = client['id']

        # Criar o agendamento
        appointment = supabase.table('appointments').insert({
            'client_id': client_id,
            'service': service,
            'appointment_time': appointment_time.isoformat()
        }).execute()
        app.logger.info(f"Agendamento criado: {appointment.data}")

        return jsonify({'message': 'Agendamento criado com sucesso!'}), 201

    except Exception as e:
        app.logger.error(f"Erro inesperado: {e}")
        return jsonify({'message': 'Erro interno no servidor.'}), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """
    Endpoint para listar todos os agendamentos e seus clientes.
    """
    response = supabase.table('appointments').select('*, clients(*)').execute()
    if response.status_code != 200:
        return jsonify({'message': 'Erro ao buscar agendamentos.'}), 500
    appointments = response.data
    return jsonify(appointments), 200

@app.route('/api/test-webhook', methods=['POST'])
def test_webhook():
    data = request.json
    app.logger.info(f"Dados recebidos no webhook de teste: {data}")
    return jsonify({'message': 'Webhook recebido com sucesso!'}), 200

if __name__ == '__main__':
    # Remova o parâmetro 'debug=True' em produção
    app.run()
