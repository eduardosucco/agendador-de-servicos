import os
from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.route('/')
def index():
    return jsonify({'message': 'Servidor funcionando. Use o Jotform para agendar!'})

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    try:
        data = request.json
        name, email, phone, service, time_str = map(data.get, ['name', 'email', 'phone', 'service', 'appointment_time'])
        if not all([name, email, phone, service, time_str]):
            return jsonify({'message': 'Dados incompletos recebidos.'}), 400

        try:
            appointment_time = datetime.fromisoformat(time_str)
        except ValueError:
            return jsonify({'message': 'Formato de data e hora inválido.'}), 400

        if not (8 <= appointment_time.hour <= 19 and appointment_time.minute == 0):
            return jsonify({'message': 'Horário inválido. Escolha horários de 1h em 1h, entre 08:00 e 19:00.'}), 400

        client = supabase.table('clients').select('*').eq('email', email).single().execute().data
        if not client:
            client = supabase.table('clients').insert({'name': name, 'email': email, 'phone': phone}).execute().data[0]
        
        supabase.table('appointments').insert({
            'client_id': client['id'], 'service': service, 'appointment_time': appointment_time.isoformat()
        }).execute()

        return jsonify({'message': 'Agendamento criado com sucesso!'}), 201

    except Exception as e:
        app.logger.error(f"Erro inesperado: {e}")
        return jsonify({'message': 'Erro interno no servidor.'}), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    response = supabase.table('appointments').select('*, clients(*)').execute()
    if response.status_code != 200:
        return jsonify({'message': 'Erro ao buscar agendamentos.'}), 500
    return jsonify(response.data), 200

@app.route('/api/test-webhook', methods=['POST'])
def test_webhook():
    app.logger.info(f"Dados recebidos: {request.json}")
    return jsonify({'message': 'Webhook recebido com sucesso!'}), 200

if __name__ == '__main__':
    app.run()
