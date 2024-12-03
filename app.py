import os
from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import pytz

# Configuração
load_dotenv()
app = Flask(__name__)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.route('/')
def index():
    return jsonify({'message': 'Servidor funcionando. Use o Jotform para agendar!'})

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    try:
        # Dados do formulário
        data = request.json
        name = data.get('Nome e Sobrenome')
        email = data.get('E-mail')
        phone = data.get('Telefone')
        service = data.get('Type a question')
        first_time = data.get('Primeira vez?')
        schedule_raw = data.get('Selecione o agendamento')

        if not all([name, email, phone, service, schedule_raw]):
            return jsonify({'message': 'Dados incompletos recebidos.'}), 400

        # Extrair e converter horário
        try:
            schedule_parts = schedule_raw.split(" - ")
            schedule_time = datetime.strptime(schedule_parts[0], "%A, %b %d, %Y %I:%M-%p")
            timezone = pytz.timezone(schedule_parts[1])
            appointment_time = timezone.localize(schedule_time).astimezone(pytz.utc)
        except (ValueError, IndexError):
            return jsonify({'message': 'Formato de data e hora inválido.'}), 400

        # Verificar ou criar cliente
        client = supabase.table('clients').select('*').eq('email', email).single().execute().data
        if not client:
            client = supabase.table('clients').insert({
                'name': name,
                'email': email,
                'phone': phone
            }).execute().data[0]

        # Criar agendamento
        supabase.table('appointments').insert({
            'client_id': client['id'],
            'service': service,
            'appointmente_time': appointment_time.isoformat(),
            'first_time': first_time
        }).execute()

        return jsonify({'message': 'Agendamento criado com sucesso!'}), 201

    except Exception as e:
        app.logger.error(f"Erro inesperado: {e}")
        return jsonify({'message': 'Erro interno no servidor.'}), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        response = supabase.table('appointments').select('*, clients(*)').execute()
        if response.status_code != 200:
            return jsonify({'message': 'Erro ao buscar agendamentos.'}), 500
        return jsonify(response.data), 200
    except Exception as e:
        app.logger.error(f"Erro ao buscar agendamentos: {e}")
        return jsonify({'message': 'Erro interno no servidor.'}), 500

@app.route('/api/test-webhook', methods=['POST'])
def test_webhook():
    app.logger.info(f"Dados recebidos no webhook de teste: {request.json}")
    return jsonify({'message': 'Webhook recebido com sucesso!'}), 200

if __name__ == '__main__':
    app.run()
