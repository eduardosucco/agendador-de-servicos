from flask import Flask, render_template, request, redirect, url_for, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    service = data.get('service')
    appointment_time = data.get('appointment_time')

    # Verificar se o cliente já existe
    client = supabase.table('clients').select('*').eq('email', email).single().execute()
    if client.data:
        client_id = client.data['id']
    else:
        # Criar novo cliente
        new_client = supabase.table('clients').insert({
            'name': name,
            'email': email,
            'phone': phone
        }).execute()
        client_id = new_client.data[0]['id']

    # Criar agendamento
    appointment = supabase.table('appointments').insert({
        'client_id': client_id,
        'service': service,
        'appointment_time': appointment_time
    }).execute()

    # Aqui você pode adicionar a lógica para integração com Google Calendar

    return jsonify({'message': 'Agendamento criado com sucesso!'}), 201

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    appointments = supabase.table('appointments').select('*, clients(*)').execute()
    return jsonify(appointments.data), 200


if __name__ == '__main__':
    app.run(debug=True)
