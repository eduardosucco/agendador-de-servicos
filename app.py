import streamlit as st
import pandas as pd
import requests

# URLs dos seus endpoints no n8n
N8N_BASE_URL = "https://seu-endereco-n8n.com/webhook" #https://n8n.massadar.me/webhook-test/agendador-de-servicos/agendamentos
GET_CLIENTS_URL = f"{N8N_BASE_URL}/get_clients"
GET_APPOINTMENTS_URL = f"{N8N_BASE_URL}/get_appointments"
ADD_CLIENT_URL = f"{N8N_BASE_URL}/add_client"
ADD_APPOINTMENT_URL = f"{N8N_BASE_URL}/add_appointment"
DELETE_CLIENT_URL = f"{N8N_BASE_URL}/delete_client"
DELETE_APPOINTMENT_URL = f"{N8N_BASE_URL}/delete_appointment"

st.set_page_config(page_title="Plataforma de Agendamento", layout="wide")

tab1, tab2 = st.tabs(["Painel Administrativo", "Novo Agendamento"])

# Aba 1: Painel Administrativo
with tab1:
    st.header("Painel Administrativo")

    st.subheader("Clientes")
    clients = requests.get(GET_CLIENTS_URL).json()
    df_clients = pd.DataFrame(clients)
    st.dataframe(df_clients)

    client_id_to_delete = st.text_input("ID do Cliente para Deletar")
    if st.button("Deletar Cliente"):
        requests.post(DELETE_CLIENT_URL, json={"client_id": client_id_to_delete})
        st.success("Cliente deletado com sucesso!")

    st.subheader("Agendamentos")
    appointments = requests.get(GET_APPOINTMENTS_URL).json()
    df_appointments = pd.DataFrame(appointments)
    st.dataframe(df_appointments)

    appointment_id_to_delete = st.text_input("ID do Agendamento para Deletar")
    if st.button("Deletar Agendamento"):
        requests.post(DELETE_APPOINTMENT_URL, json={"appointment_id": appointment_id_to_delete})
        st.success("Agendamento deletado com sucesso!")

# Aba 2: Novo Agendamento
with tab2:
    st.header("Novo Agendamento")

    st.subheader("Dados do Cliente")
    first_name = st.text_input("Nome")
    last_name = st.text_input("Sobrenome")
    phone = st.text_input("Telefone")
    email = st.text_input("Email")
    first_time = st.selectbox("Primeira vez?", ["Sim", "Não"])

    if st.button("Cadastrar Cliente"):
        client_data = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "first_time": first_time
        }
        requests.post(ADD_CLIENT_URL, json=client_data)
        st.success("Cliente cadastrado com sucesso!")

    st.subheader("Agendar Serviço")
    clients = requests.get(GET_CLIENTS_URL).json()
    client_options = {f"{c['first_name']} {c['last_name']}": c['id'] for c in clients}
    selected_client = st.selectbox("Cliente", list(client_options.keys()))

    service = st.text_input("Serviço")
    date = st.date_input("Data")
    time = st.time_input("Hora")
    comment = st.text_area("Comentário")

    if st.button("Agendar Serviço"):
        appointment_data = {
            "client_id": client_options[selected_client],
            "service": service,
            "date": str(date),
            "time": str(time),
            "comment": comment
        }
        requests.post(ADD_APPOINTMENT_URL, json=appointment_data)
        st.success("Agendamento realizado com sucesso!")
