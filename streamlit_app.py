import streamlit as st
import pandas as pd
import requests

# URLs dos seus endpoints no n8n
N8N_BASE_URL = "https://n8n.massadar.me/webhook/agendador-de-servicos"
GET_CLIENTS_URL = f"{N8N_BASE_URL}/clientes"
GET_APPOINTMENTS_URL = f"{N8N_BASE_URL}/agendamentos"
# ADD_CLIENT_URL = f"{N8N_BASE_URL}/add_client"
# ADD_APPOINTMENT_URL = f"{N8N_BASE_URL}/add_appointment"
# DELETE_CLIENT_URL = f"{N8N_BASE_URL}/agendamento/:id"
DELETE_APPOINTMENT_URL = f"{N8N_BASE_URL}/agendamento/:id"

# Função genérica para interagir com endpoints
def api_request(endpoint, method="GET", data=None, params=None):
    try:
        response = requests.request(method, endpoint, json=data, params=params)
        response.raise_for_status()
        return response.json() if method == "GET" else True
    except Exception as e:
        st.error(f"Erro: {e}")
        return [] if method == "GET" else False

# Função para exibir tabelas com manipulação
def display_table(data, delete_label, delete_endpoint):
    df = pd.DataFrame(data)
    st.dataframe(df)
    delete_id = st.text_input(f"ID para {delete_label}")
    if st.button(f"Deletar {delete_label}"):
        try:
            endpoint = delete_endpoint.replace(":id", delete_id)
            if api_request(endpoint, method="DELETE"):
                st.success(f"{delete_label} deletado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao deletar {delete_label}: {e}")

# Menu Lateral
menu = st.sidebar.selectbox("Menu", ["Painel Administrativo", "Novo Agendamento"])

if menu == "Painel Administrativo":
    st.title("Painel Administrativo")
    st.subheader("Clientes")
    clients = api_request(GET_CLIENTS_URL)
    display_table(clients, "Cliente", "# DELETE_CLIENT_URL (não implementado)")

    st.subheader("Agendamentos")
    appointments = api_request(GET_APPOINTMENTS_URL)
    display_table(appointments, "Agendamento", DELETE_APPOINTMENT_URL)

elif menu == "Novo Agendamento":
    st.title("Novo Agendamento")
    st.subheader("Cadastrar Cliente")
    st.warning("Endpoint ADD_CLIENT_URL não implementado")

    st.subheader("Agendar Serviço")
    st.warning("Endpoint ADD_APPOINTMENT_URL não implementado")
