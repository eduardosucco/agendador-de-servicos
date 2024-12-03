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

st.set_page_config(page_title="Plataforma de Agendamento", layout="wide")

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Painel Administrativo", "Novo Agendamento"])

# Função para criar DataFrame seguro
def safe_dataframe(data, columns=None):
    if not data:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(data)

# Painel Administrativo
if menu == "Painel Administrativo":
    st.header("Painel Administrativo")
    
    st.subheader("Clientes")
    try:
        clients = requests.get(GET_CLIENTS_URL).json()
        df_clients = safe_dataframe(clients, columns=["ID", "Nome", "Sobrenome", "Telefone", "Email", "Primeira Vez"])
        st.dataframe(df_clients)
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")

    client_id_to_delete = st.text_input("ID do Cliente para Deletar")
    if st.button("Deletar Cliente"):
        try:
            requests.post(DELETE_CLIENT_URL, json={"client_id": client_id_to_delete})
            st.success("Cliente deletado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao deletar cliente: {e}")
    
    st.subheader("Agendamentos")
    try:
        appointments = requests.get(GET_APPOINTMENTS_URL).json()
        df_appointments = safe_dataframe(
            appointments, columns=["ID", "Cliente", "Serviço", "Data", "Hora", "Comentário"]
        )
        st.dataframe(df_appointments)
    except Exception as e:
        st.error(f"Erro ao carregar agendamentos: {e}")

    appointment_id_to_delete = st.text_input("ID do Agendamento para Deletar")
    if st.button("Deletar Agendamento"):
        try:
            requests.post(DELETE_APPOINTMENT_URL, json={"appointment_id": appointment_id_to_delete})
            st.success("Agendamento deletado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao deletar agendamento: {e}")

# Novo Agendamento
elif menu == "Novo Agendamento":
    st.header("Novo Agendamento")

    st.subheader("Dados do Cliente")
    first_name = st.text_input("Nome")
    last_name = st.text_input("Sobrenome")
    phone = st.text_input("Telefone")
    email = st.text_input("Email")
    first_time = st.selectbox("Primeira vez?", ["Sim", "Não"])

    if st.button("Cadastrar Cliente"):
        try:
            client_data = {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "email": email,
                "first_time": first_time
            }
            requests.post(ADD_CLIENT_URL, json=client_data)
            st.success("Cliente cadastrado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao cadastrar cliente: {e}")

    st.subheader("Agendar Serviço")
    try:
        clients = requests.get(GET_CLIENTS_URL).json()
        client_options = {f"{c['first_name']} {c['last_name']}": c['id'] for c in clients}
        selected_client = st.selectbox("Cliente", list(client_options.keys()))
    except Exception as e:
        client_options = {}
        selected_client = None
        st.error(f"Erro ao carregar lista de clientes: {e}")

    service = st.text_input("Serviço")
    date = st.date_input("Data")
    time = st.time_input("Hora")
    comment = st.text_area("Comentário")

    if st.button("Agendar Serviço"):
        try:
            if selected_client:
                client_id = client_options[selected_client]
                appointment_data = {
                    "client_id": client_id,
                    "service": service,
                    "date": str(date),
                    "time": str(time),
                    "comment": comment
                }
                requests.post(ADD_APPOINTMENT_URL, json=appointment_data)
                st.success("Agendamento realizado com sucesso!")
            else:
                st.error("Nenhum cliente selecionado!")
        except Exception as e:
            st.error(f"Erro ao realizar agendamento: {e}")